#
# Copyright (c) 2010, 2013
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
# THE SOFTWARE.
#
import uuid
from email.mime.text import MIMEText
from email.Utils import COMMASPACE, formatdate
from coils.core import \
    ThreadedService, \
    Packet, \
    ServerDefaultsManager, \
    AdministrativeContext, \
    SMTP, \
    ObjectInfoManager
from perflog import PerformanceLog


class AdministratorService (ThreadedService):
    __service__ = 'coils.administrator'
    __auto_dispatch__ = True

    def __init__(self):
        ThreadedService.__init__(self)
        self._id_queue = []

    def prepare(self):
        ThreadedService.prepare(self)
        self._ctx = AdministrativeContext({}, broker=self._broker)
        self._sd = ServerDefaultsManager()
        server_uuid_prop = self._ctx.property_manager.get_server_property(
            'http://www.opengroupware.us/global',
            'clusterGUID',
        )
        if (server_uuid_prop is None):
            self._cluster_guid = '{{{0}}}'.format(str(uuid.uuid4()))
            self._ctx.property_manager.set_server_property(
                'http://www.opengroupware.us/global',
                'clusterGUID',
                self._cluster_guid,
            )
            self._ctx.commit()
        else:
            self._cluster_guid = server_uuid_prop.get_value()
            server_uuid_prop = None
        self.perflog = PerformanceLog()
        self._ctx.db_close()

    @property
    def administrative_email(self):
        return self._sd.string_for_default(
            'AdministrativeEMailAddress',
            value='root@localhost',
        )

    def send_notice(
        self,
        subject,
        message,
        urgency=5,
        category='unspecified',
        alert_id=None,
    ):
        if (subject is None):
            subject = (
                u'[OpenGrouware] Administrative Notice {0}'.
                format(alert_id, )
            )
        else:
            subject = u'[OpenGrouware] {0}'.format(subject)
        message = MIMEText(message)
        message['Subject'] = subject
        message['From'] = ''
        message['To'] = self.administrative_email
        message['Date'] = formatdate(localtime=True)
        message['X-Opengroupware-Alert'] = alert_id
        message['X-Opengroupware-Cluster-GUID'] = self._cluster_guid
        SMTP.send('', [self.administrative_email, ], message)
        self.log.info('Message sent to administrator.')
        return True

    #
    # Message Handlers
    #

    def do_get_server_defaults(self, parameter, packet):
        self.send(
            Packet.Reply(
                packet,
                {'status': 200,
                 'text': 'OK',
                 'GUID': self._cluster_guid,
                 'defaults': self._sd.defaults, }
            )
        )

    def do_get_cluster_guid(self, parameter, packet):
        self.send(
            Packet.Reply(
                packet,
                {'status': 200,
                 'text': 'OK',
                 'GUID': self._cluster_guid, }
            )
        )

    def do_notify(self, parameter, packet):
        try:
            self.log.info('Received a request to notify administrator')
            category = packet.data.get('category', 'unspecified')
            urgency = packet.data.get('urgency', 5)
            subject = packet.data.get('subject', None)
            message = unicode(packet.data.get('message'))
            self.send_notice(
                subject,
                message,
                urgency=urgency,
                category=category,
                alert_id=packet.uuid,
            )
        except Exception, e:
            # TODO: log something and make response more informative
            self.log.exception(e)
            self.send(Packet.Reply(packet, {'status': 500,
                                            'text': 'Failure'}))
        else:
            self.send(Packet.Reply(packet, {'status': 201, 'text':
                                            'OK'}))

    def do_repair_objinfo(self, parameter, packet):
        self.log.info(
            'Request from {0} to repair Object Info for objectId#{1}'.
            format(packet.source, parameter, )
        )
        try:
            object_id = int(parameter)
        except:
            self.log.error(
                'Received non-integer value for objinfo repair request'
            )
        else:
            if object_id < 1000:
                return
            try:
                om = ObjectInfoManager(self._ctx, log=self.log, service=self)
                if (om.repair(object_id=object_id)):
                    self.log.info(
                        'Object Info repaired for objectId#{0}'.
                        format(object_id, )
                    )
                    self._ctx.commit()
                else:
                    self.log.info(
                        'No action performed, ObjectInfo is not '
                        'modified (objectId#{0})'.
                        format(object_id, )
                    )
                    self._ctx.rollback()
                self._ctx.db_close()
                om = None
            except Exception as exc:
                self.log.error('Exception repairing Object Info')
                self.log.exception(exc)
                self.send_notice(
                    ('Exception repairing Object Info for objectId#{0}'.
                     format(object_id, )),
                    str(exc),
                )

    def do_performance_log(self, parameter, packet):
        try:
            lname = packet.data.get('lname')
            oname = packet.data.get('oname')
            runtime = packet.data.get('runtime')
            error = packet.data.get('error')
        except Exception as exc:
            self.log.error(
                'Unable to parse performance log packet from "{0}"'.
                format(packet.source, )
            )
            self.log.exception(exc)
        else:
            try:
                self.perflog.insert_record(
                    lname, oname, runtime=runtime, error=error,
                )
            except Exception as exc:
                self.log.error('Error updating performance statistics')
                self.log.exception(exc)
                self.send_notice(
                    'Error updating performance statistics',
                    str(exc)
                )

    def do_get_performance_log(self, parameter, packet):
        try:
            self.log.info(
                'Request for performance log from "{0}"'.
                format(packet.source, )
            )
            data = self.perflog.data.get(parameter, {})
        except Exception, e:
            self.log.error('Exception retrieving performance statistics')
            self.log.exception(e)
            self.send(
                Packet.Reply(
                    packet,
                    {'status': 500, 'text': 'Exception', }
                )
            )
        else:
            self.send(
                Packet.Reply(
                    packet,
                    {'status': 200,
                     'text': 'Performance Log Data',
                     'payload': data, },
                )
            )
