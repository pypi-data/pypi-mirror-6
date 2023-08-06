#
# Copyright (c) 2010, 2011, 2013
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#
import traceback
from uuid import uuid4
from sqlalchemy import and_
from datetime import datetime
from time import time
from coils.core import \
    ThreadedService, \
    AdministrativeContext, \
    BLOBManager, \
    Packet, \
    ProcessLogEntry
from coils.logic.workflow.utility import \
    filename_for_process_log, \
    read_cached_process_log, \
    delete_cached_process_logs, \
    cache_process_log


LOGGER_FLUSH = 200


class LoggerService(ThreadedService):
    __service__ = 'coils.workflow.logger'
    __auto_dispatch__ = True
    __is_worker__ = False

    def __init__(self):
        ThreadedService.__init__(self)

    def prepare(self):
        ThreadedService.prepare(self)
        self._ctx = AdministrativeContext({}, broker=self._broker)
        self._log_queue = BLOBManager.OpenShelf(uuid='coils.workflow.logger')

        self.schedule_at_interval(
            name='flush process log message queue',
            minutes=2,
            message=LOGGER_FLUSH,
            data=None,
        )

        self._last_flush = None

    def process_service_specific_event(self, event_class, event_data):
        if event_class == LOGGER_FLUSH:
            self._empty_queue()

    def _log_message(
        self,
        source,
        process_id,
        message,
        stanza=None,
        timestamp=None,
        category='undefined',
        uuid=None
    ):
        try:
            if (timestamp is None):
                timestamp = float(time())
            self._log_queue[uuid4().hex] = (
                source,
                process_id,
                message.strip(),
                stanza,
                timestamp,
                category,
                uuid,
            )
            self._log_queue.sync()
        except Exception, e:
            self.log.exception(e)
            return False
        else:
            return True

    def _empty_queue(self):
        if self._last_flush:
            self.log.debug(
                'Last process log flush completed @ {0}'.
                format(self._last_flush.isoformat(), )
            )
        else:
            self.log.debug(
                'Performing first process log flush'
            )

        keys = list()
        try:

            for key in self._log_queue:
                (source,
                 process_id,
                 message,
                 stanza,
                 timestamp,
                 category,
                 uuid, ) = self._log_queue[key]

                # prevent excessively long string, trim to maximum lengths
                if stanza is not None:
                    stanza = stanza[:32]
                if category is not None:
                    category = category[:15]
                if source is not None:
                    source = source[:64]
                if uuid is not None:
                    uuid = uuid[:64]

                entry = ProcessLogEntry(
                    source,
                    process_id,
                    message,
                    stanza=stanza,
                    timestamp=timestamp,
                    category=category,
                    uuid=uuid,
                )
                self._ctx.db_session().add(entry)
                keys.append(key)
        except Exception, e:
            message = \
                'Workflow process message log cannot be flushed to ' \
                'database.\n{0}'.format(traceback.format_exc(), )
            subject = 'Exception creating process log entry!'
            self.log.error(subject)
            self.log.exception(e)
            self.send_administrative_notice(subject=subject,
                                            message=message,
                                            urgency=9,
                                            category='workflow')
        else:
            try:
                self.log.debug(
                    'Commiting {0} process log entries'.
                    format(len(keys), )
                )
                self._ctx.commit()
            except Exception, e:
                # TODO: Send an administrative notice!
                self.log.exception(e)
            else:
                for key in keys:
                    del self._log_queue[key]
            self._log_queue.sync()
            self.log.debug(
                '{0} process log entries purged from queue'.
                format(len(keys), )
            )

        self._ctx.db_close()

        self.log.debug('Process log flush complete')
        # Update last flush time stampe
        self._last_flush = datetime.now()

    def do_log(self, parameter, packet):
        try:
            source = Packet.Service(packet.source)
            process_id = long(packet.data.get('process_id'))
            message = packet.data.get('message', None)
            stanza = packet.data.get('stanza', None)
            category = packet.data.get('category', 'undefined')
            uuid = packet.uuid
            timestamp = packet.time
        except Exception, e:
            self.log.exception(e)
            self._ctx.rollback()
            self.send(
                Packet.Reply(
                    packet,
                    {'status': 500,
                     'text': 'Failure to parse packet payload.', },
                )
            )
        else:
            if self._log_message(
                source,
                process_id,
                message,
                stanza=stanza,
                timestamp=timestamp,
                category=category,
                uuid=uuid,
            ):
                self.send(
                    Packet.Reply(packet, {'status': 201, 'text': 'OK'})
                )
            else:
                self.send(
                    Packet.Reply(
                        packet,
                        {'status': 500,
                         'text': 'Failure to record message.', },
                    )
                )

    def do_reap(self, parameter, packet):
        process_id = int(parameter)
        db = self._ctx.db_session()
        try:
            db.query(ProcessLogEntry).\
                filter(ProcessLogEntry.process_id == process_id).\
                delete(synchronize_session='fetch')
        except Exception, e:
            self.log.exception(e)
            self.send(
                Packet.Reply(
                    packet,
                    {'status': 500,
                     'text': 'Failure to purge process log.', }
                )
            )
        else:
            self._ctx.commit()
            self.send(
                Packet.Reply(packet, {'status': 201, 'text': 'OK', }, )
            )

    def do_flush(self, parameter, packet):
        self.event_queue.put((LOGGER_FLUSH, packet.data, ))
        self.send(
            Packet.Reply(packet, {'status': 201, 'text': 'OK', }, )
        )
