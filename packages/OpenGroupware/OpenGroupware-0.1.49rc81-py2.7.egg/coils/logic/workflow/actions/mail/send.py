#
# Copyright (c) 2010, 2013, 2014
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
# THE SOFTWARE
#
import socket  # gaierror from socket in try/catch
import uuid
from email import Encoders, message_from_file
from email.Utils import COMMASPACE, formatdate
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.generator import Generator
from email.mime.text import MIMEText
from coils.core import CoilsException, SMTP
from coils.core.logic import ActionCommand


class SendMailAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "send-mail"
    __aliases__ = ['sendMail', 'sendMailAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'message/rfc822'

    def create_message(self):

        message = None

        if self._as_attachment:
            message = MIMEMultipart()
            if (self._body is not None):
                message.attach(MIMEText(self._body))
            else:
                message.attach(MIMEText(''))
            part = MIMEBase(
                self.input_mimetype.split('/')[0],
                self.input_mimetype.split('/')[1],
            )
            part.set_payload(self.rfile.read())
            part.add_header(
                'Content-Disposition', 'attachment; filename="{0}"'.
                format(self._partname, )
            )
            Encoders.encode_base64(part)
            message.attach(part)
        else:
            if (self._body is not None):
                message = MIMEText(self._body)
            else:
                message = MIMEText(self.rfile.read())

        message['Subject'] = self._subject
        message['From'] = self._from
        message['To'] = COMMASPACE.join(self._to)
        if (len(self._cc)):
            message['Cc'] = COMMASPACE.join(self._cc)
        message['Date'] = formatdate(localtime=True)
        message['Message-ID'] = (
            '{0}@{1}.{2}'.
            format(
                self.pid,
                self._ctx.cluster_id,
                uuid.uuid4().hex,
            )
        )

        '''
        Set the X-OpenGroupware-Regarding header to the task related to the
        process if such a relation exists, otherwise set it to the PID.
        '''
        if self.process.task_id:
            message['X-Opengroupware-Regarding'] = str(self.process.task_id)
        else:
            message['X-Opengroupware-Regarding'] = str(self.pid)

        message['X-Opengroupware-Process-Id'] = str(self.pid)
        message['X-Opengroupware-Context'] = (
            '{0}[{1}]'.format(self._ctx.get_login(), self._ctx.account_id, )
        )

        return message

    def message_from_input(self):
        return message_from_file(self.rfile)

    def get_message_to_attach(self, label):
        if self._attachment_label:
            message = self._ctx.run_command(
                'message::get',
                process=self.process,
                scope=self._scope,
                label=label,
            )
            if message:
                handle = self._ctx.run_command(
                    'message::get-handle', message=message,
                )
        return message.mimetype, handle

    def attach_to_message(self, message, mimetype, handle):
        part = MIMEBase(
            mimetype.split('/')[0],
            mimetype.split('/')[1],
        )
        part.set_payload(handle.read())
        part.add_header(
            'Content-Disposition', 'attachment; filename="{0}"'.
            format(self._partname, )
        )
        Encoders.encode_base64(part)
        message.attach(part)

    def do_action(self):

        if self.input_mimetype == 'message/rfc822':
            message = self.message_from_input()
            mimetype, handle, = self.get_message_to_attach(
                label=self._attachment_label,
            )
            if handle:
                self.attach_to_message(message, mimetype, handle, )
            else:
                raise CoilsException(
                    'Label "{0}" not available for message attach'.
                    format(self._attachment_label, )
                )
        else:
            message = self.create_message()

        message['To'] = COMMASPACE.join(self._to)
        if (len(self._cc)):
            message['Cc'] = COMMASPACE.join(self._cc)

        if self._deliver_message:
            if self._to is None:
                raise CoilsException(
                    'Attempt to send e-mail with no destination!'
                )
            addresses = []
            if 'Cc' in message:
                addresses.extend(
                    [x.strip() for x in message['Cc'].split(',')]
                )
            if 'To' in message:
                addresses.extend(
                    [x.strip() for x in message['To'].split(',')]
                )
            addresses.extend(self._bcc)
            SMTP.send(message['From'], addresses, message, )

        g = Generator(self.wfile, mangle_from_=False, maxheaderlen=255, )
        g.flatten(message)

    def parse_action_parameters(self):

        # asAttachment, otherwise the input becomes the BODY of the message
        self._as_attachment = True if self.action_parameters.get(
            'asAttachment', 'YES'
        ).upper() == 'YES' else False

        # deliverMessage
        self._deliver_message = True if self.action_parameters.get(
            'deliverMessage', 'YES'
        ).upper() == 'YES' else False

        # filename -> partname, name of the attachment
        self._partname = self.process_label_substitutions(
            self.action_parameters.get(
                'filename', 'message.data'
            )
        )

        # attachmentLabel, only used for message resume
        self._attachment_label = self.process_label_substitutions(
            self.action_parameters.get(
                'attachmentLabel', None,
            )
        )

        # SUBJECT
        self._subject = self.process_label_substitutions(
            self.action_parameters.get('subject', '')
        )

        # FROM
        self._from = self.process_label_substitutions(
            self.action_parameters.get('from', self._ctx.email)
        )

        # TO
        self._to = [
            address for address in
            self.process_label_substitutions(
                self.action_parameters.get('to', self._ctx.email)
            ).split(',') if len(address) > 4
        ]

        # CC
        self._cc = [
            address for address in
            self.process_label_substitutions(
                self.action_parameters.get('CC', '')
            ).split(',') if len(address) > 4
        ]

        # BCC
        self._bcc = [
            address for address in
            self.process_label_substitutions(
                self.action_parameters.get('BCC', '')
            ).split(',') if len(address) > 4
        ]

        # bodyText
        self._body = self.action_parameters.get('bodyText', None)
        if self._body is not None:
            self._body = self.process_label_substitutions(self._body)

    def do_epilogue(self):
        pass
