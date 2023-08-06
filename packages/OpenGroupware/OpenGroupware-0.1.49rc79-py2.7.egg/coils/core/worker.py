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
#
from os import getpid
import uuid
import traceback
import multiprocessing
import sys
import logging
import Queue
import time
from sqlalchemy import event
from coils.foundation import Backend


EVENTQUEUE_MAX_SIZE = 4096


from worker_events import \
    AMQ_RECEIVED, \
    AMQ_TRANSMIT, \
    AMQ_ACKNOWLEDGE, \
    AMQ_FAIL, \
    AMQ_TIMEOUT, \
    WORKER_ERROR, \
    SEND_ADMIN_NOTICE, \
    WORKER_RECONFIGURE


class MultiProcessWorker(multiprocessing.Process):

    def __init__(self, name, work_queue, event_queue, silent=True):
        multiprocessing.Process.__init__(self)
        self.name = name
        self.work_queue = work_queue
        self.event_queue = event_queue
        self.running = True
        self._is_silent = silent

        self.log = logging.getLogger(
            #'{0}[PID#{1}]'.format(self.name, getpid(), )
            self.name
        )

    def setup(self):

        if self._is_silent:
            sys.stdin = open('/dev/null', 'r')
            sys.stdout = open('/dev/null', 'w')
            sys.stderr = open('/dev/null', 'w')

        Backend.db_connect()

        event.listen(Backend._engine, "connect", self.on_db_connect)
        event.listen(Backend._engine, "checkout", self.on_db_checkout)
        event.listen(Backend._engine, "checkin", self.on_db_checkin)

        event.listen(Backend._engine, "begin", self.on_db_begin)
        event.listen(Backend._engine, "commit", self.on_db_commit)
        event.listen(Backend._engine, "rollback", self.on_db_rollback)

    def on_db_connect(self, connection, pool):
        self.log.debug('DB Connect')

    def on_db_checkout(self, dbapi_conn, connection_rec, connection_proxy):
        self.log.debug('DB Checkout')

    def on_db_checkin(self, dbapi_connection, connection_record):
        self.log.debug('DB Checkin')

    def on_db_begin(self, connection):
        self.log.debug('DB Begin')

    def on_db_commit(self, connection):
        self.log.debug('DB Commit')

    def on_db_rollback(self, connection):
        self.log.debug('DB Rollback')

    def enqueue_event(self, command, payload):
        try:
            self.event_queue.put((command, payload, ))
        except Queue.Full:
            while self.event_queue.full():
                self.log.debug(
                    'Waiting for available event queue space; {0} of {1}'.
                    format(self.event_queue.qsize(), EVENTQUEUE_MAX_SIZE, ))
                time.sleep(1.0)
            self.enqueue_event(command, payload)

    def run(self):
        self.setup()
        try:
            import procname
            procname.setprocname(self.name)
        except:
            self.log.info('Failed to set process name for service')

        while self.running:
            self.log.debug('IDLE')

            try:

                (command, payload, target, ) = self.work_queue.get()

                if target:
                    '''
                    This message is not for us, put it back in the queue
                    TODO: What happens with messages sent to a worker that
                    is defunct?
                    '''
                    if target != self.name:
                        self.log.debug(
                            'Discard worker message - not mine, '
                            'targeted to "{0}"'.format(target, )
                        )
                        self.work_queue.put((command, payload, target, ))
                        continue

                if command is None:
                    self.log.debug(
                        'Worker commencing self-termination due to '
                        'NULL command'
                    )
                    self.running = False
                if command == WORKER_RECONFIGURE:
                    self.configure_worker()
                else:
                    self.process_worker_message(command, payload, )
            except KeyboardInterrupt:
                break
            except Exception as exc:
                self.log.error(
                    'Unexpected exception in component worker "{0}"'.
                    format(self.name, )
                )
                self.log.exception(exc)
                message = (
                    'Worker:{0}\n  Command: {1}\n  Payload: {2}\n  '
                    'Target: {3}\n\n{4}\n'.
                    format(
                        self.name,
                        command,
                        payload,
                        target,
                        traceback.format_exc(),
                    )
                )
                self.enqueue_event(WORKER_ERROR, message)

    def process_worker_message(self, command, payload):
        self.log.error('WORKER SHOULD NOT BE HERE!')
        pass

    def configure_worker(self):
        self.log.debug('Worker configuration/reconfiguration invoked')

    def send_administrative_notice(
        self,
        subject=None,
        message=None,
        urgency=9,
        category='unspecified',
    ):
        self.enqueue_event(
            SEND_ADMIN_NOTICE,
            (subject,
             message,
             urgency,
             category, ), )
