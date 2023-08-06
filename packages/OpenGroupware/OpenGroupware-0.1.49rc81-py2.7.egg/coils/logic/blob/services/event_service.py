#
# Copyright (c) 2013
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
# THE  SOFTWARE.
#
import uuid
import multiprocessing
import Queue
from sqlalchemy import and_
from coils.core import AdministrativeContext, ThreadedService
from event_worker import EventWorker

from events import \
    DOCUMENT_COLLECT_REQUEST, \
    DOCUMENT_COLLECT_DISCARDED, \
    DOCUMENT_COLLECT_FAILED, \
    DOCUMENT_COLLECT_COMPLETED, \
    DOCUMENT_DELETED, \
    DOCUMENT_BURST_REQUEST, \
    DOCUMENT_BURST_COMPLETED, \
    DOCUMENT_BURST_FAILED, \
    DOCUMENT_BURST_DISCARDED, \
    DOCUMENT_AUTOFILE_REQUEST, \
    DOCUMENT_AUTOFILE_COMPLETED, \
    DOCUMENT_AUTOFILE_FAILED, \
    DOCUMENT_AUTOFILE_DISCARDED, \
    DOCUMENT_SPECIAL_PROCESSING, \
    DOCUMENT_SPECIAL_DISCARDED, \
    DOCUMENT_SPECIAL_FAILED, \
    DOCUMENT_SPECIAL_COMPLETED, \
    DOCUMENT_UNCOLLECT_REQUEST, \
    DOCUMENT_UNCOLLECT_DISCARDED,\
    DOCUMENT_UNCOLLECT_FAILED, \
    DOCUMENT_UNCOLLECT_COMPLETED, \
    ENQUEUE_PROCESS

from utility import get_inherited_property


COMMAND_MAP = {
    DOCUMENT_COLLECT_DISCARDED:   None,
    DOCUMENT_COLLECT_FAILED:      'handle_collection_failed',
    DOCUMENT_COLLECT_COMPLETED:   'handle_collection_completed',
    DOCUMENT_BURST_COMPLETED:     'handle_document_burst_completed',
    DOCUMENT_BURST_FAILED:        'handle_document_burst_failed',
    DOCUMENT_BURST_DISCARDED:     'handle_document_burst_discarded',
    DOCUMENT_AUTOFILE_COMPLETED:  'handle_document_autofile_completed',
    DOCUMENT_AUTOFILE_FAILED:     'handle_document_autofile_failed',
    DOCUMENT_AUTOFILE_DISCARDED:  'handle_document_autofile_discarded',
    DOCUMENT_UNCOLLECT_DISCARDED: 'handle_document_uncollect_discarded',
    DOCUMENT_UNCOLLECT_FAILED:    'handle_document_uncollect_failed',
    DOCUMENT_UNCOLLECT_COMPLETED: 'handle_document_uncollect_completed',
    ENQUEUE_PROCESS:              'enqueue_workflow_process',
    DOCUMENT_SPECIAL_DISCARDED:   'handle_document_special_discarded',
    DOCUMENT_SPECIAL_FAILED:      'handle_document_special_failed',
    DOCUMENT_SPECIAL_COMPLETED:   'handle_document_special_completed',
}


class EventService(ThreadedService):
    __service__ = 'coils.blob.event'
    __auto_dispatch__ = True

    def __init__(self):
        ThreadedService.__init__(self)

    def worker_name_generator(self):
        return 'coils.blob.event.worker({0})'.format(uuid.uuid4().hex, )

    def setup(self, silent=True):
        ThreadedService.setup(self, silent=silent, )

        self._broker.subscribe(
            '{0}.notify'.format(self.__service__, ),
            self.receive_message,
            expiration=900000,
            queue_type='fanout',
            durable=False,
            exchange_name='OpenGroupware_Coils_Notify',
        )

        self.start_workers(
            count=4,
            classname=EventWorker,
            name_generator=self.worker_name_generator, )

    def prepare(self):
        ThreadedService.prepare(self)
        self._ctx = AdministrativeContext({}, broker=self._broker, )

    def process_service_specific_event(self, event_class, event_data):
        print('CLASS: {0}, DATA: {1}'.format(event_class, event_data, ))
        if event_class in COMMAND_MAP:
            method_name = COMMAND_MAP.get(event_class)
            if method_name:
                if hasattr(self, method_name):
                    method = getattr(self, method_name)
                    tmp = None
                    try:
                        tmp = method(event_data)
                    except Exception as exc:
                        self.log.error(
                            'exception processing event {0} date="{1}"'.
                            format(event_class, event_data, )
                        )
                        self.log.exception(exc)
                    tmp = None
                else:
                    self.log.error(
                        'Method "{0}" mapped from event "{1}" does not exist.'.
                        format(method_name, event_class, ))
            else:
                self.log.info(
                    'Event "{0}" mapped as  no-operation'.
                    format(event_class, ))
        else:
            self.log.warn(
                'Event "{0}" is not in command processing map'.
                format(event_class, ))

    #
    # Message Handlers
    #

    def do___audit_document(self, parameter, packet):
        '''
        Audit message for type document received.
        '''

        object_id = long(packet.data.get('objectId', 0))
        action_tag = packet.data.get('action', 'unknown')
        version = packet.data.get('version', None)

        self.log.debug(
            'Event "{0}" received for OGo#{1} [Document] version {2}'.
            format(action_tag, object_id, version, )
        )

        try:
            if action_tag in ('00_created', '05_changed', ):
                self.enqueue_work(DOCUMENT_AUTOFILE_REQUEST, packet.data, )
            if action_tag in ('00_created', '05_changed', '10_commented', ):
                self.enqueue_work(DOCUMENT_SPECIAL_PROCESSING, packet.data, )
            if action_tag in ('05_changed', '10_commented', ):
                self.enqueue_work(DOCUMENT_UNCOLLECT_REQUEST, packet.data, )
            if action_tag in ('00_created', ):
                self.enqueue_work(DOCUMENT_COLLECT_REQUEST, packet.data, )
                self.enqueue_work(DOCUMENT_BURST_REQUEST, packet.data, )
            elif action_tag in ('99_deleted', ):
                self.enqueue_work(DOCUMENT_DELETED, packet.data, )
        except Queue.Full:
            self.log.info('Unable to queue document event for processing')

        return

    #
    # Event handling
    #

    def handle_document_burst_completed(self, event_data):
        self.log.info(
            'Bursting of OGo#{0} reported as completed'.
            format(event_data[0], ))

    def handle_document_burst_discarded(self, event_data):
        self.log.info(
            'Bursting of OGo#{0} reported as discarded'.
            format(event_data[0], ))

    def handle_document_burst_failed(self, event_data):
        self.log.error(
            'Bursting of OGo#{0} reported as having failed'.
            format(event_data[0], ))

    def handle_collection_failed(self, event_data):
        self.log.error(
            'Collecting of OGo#{0} reported as having failed'.
            format(event_data[0], ))

    def handle_collection_completed(self, event_data):
        self.log.info(
            'Collecting of OGo#{0} reported as completed'.
            format(event_data[0], ))

    def handle_document_autofile_completed(self, event_data, ):
        self.log.info(
            'Auto-filing of OGo#{0} reported as completed'.
            format(event_data[0], ))

    def handle_document_autofile_failed(self, event_data, ):
        self.log.error(
            'Auto-filing of OGo#{0} reported as failed'.
            format(event_data[0], ))

    def handle_document_autofile_discarded(self, event_data, ):
        self.log.info(
            'Auto-filing of OGo#{0} reported as discarded'.
            format(event_data[0], ))

    '''Uncollect response handlers'''

    def handle_document_uncollect_discarded(self, event_data, ):
        self.log.info(
            'Uncollection of OGo#{0} reported as discarded: {1}'.
            format(event_data[0], event_data[2]))

    def handle_document_uncollect_failed(self, event_data, ):
        self.log.error(
            'Uncollection of OGo#{0} reported as failed: {1}'.
            format(event_data[0], event_data[2]))

    def handle_document_uncollect_completed(self, event_data, ):
        self.log.info(
            'Uncollection of OGo#{0} reported as completed: {1}'.
            format(event_data[0], event_data[2]))

    '''Special processing response handlers'''
    def handle_document_special_discarded(self, event_data, ):
        self.log.info(
            'Special processing of OGo#{0} reported as discarded: {1}'.
            format(event_data[0], event_data[1])
        )

    def handle_document_special_failed(self, event_data, ):
        self.log.error(
            'Special processing of OGo#{0} reported as failed: {1}'.
            format(event_data[0], event_data[1])
        )

    def handle_document_special_completed(self, event_data, ):
        self.log.info(
            'Special processing of OGo#{0} reported as completed: {1}'.
            format(event_data[0], event_data[1])
        )

    '''Workflow handlers'''
    def enqueue_workflow_process(self, event_data, ):
        pid = event_data[0]
        self.log.info(
            'requesting start of workflow process OGo#{0}'.format(pid, )
        )
        process = self._ctx.run_command('process::get', id=pid, )
        if process:
            self._ctx.run_command('process::start', process=process, )
            self._ctx.commit()
            self.log.info(
                'Request start of OGo#{0}'.format(event_data[0], )
            )
        else:
            self.log.warn(
                'Process OGo#{0} not available to start'.
                format(pid, )
            )
        self._ctx.rollback()
