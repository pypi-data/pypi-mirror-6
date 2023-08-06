#
# Copyright (c)  2013
#   Adam Tauno Williams <awilliam@whitemice.org>
#
# License: MIT/X11
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
from ftplib import FTP
from shutil import copyfileobj
from coils.core.logic import ActionCommand


class FTPGetFileAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "ftp-get-file"
    __aliases__ = ['ftpGetFile', 'ftpGetFileAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return self._mimetype

    def _write_block_to_wfile(self, data):
        self.wfile.write(data)
        self._offset += len(data)

    def do_action(self):
        self._offset = 0

        ftp = FTP(self._hostname)
        self.log_message(
            message=(
                'Connected to FTP service "{0}"'.format(self._hostname, )
            ),
            category='debug',
        )

        ftp.set_pasv(self._passive)

        if not self._username:
            ftp.login()
        else:
            ftp.login(self._username, self._password)
        self.log_message(
            message='Authenticated to FTP service',
            category='debug',
        )

        if self._directory:
            ftp.cwd(self._directory)

        ftp.retrbinary(
            'RETR {0}'.format(self._filename, ),
            callback=self._write_block_to_wfile,
        )

        ftp.quit()

        self.log_message(
            message=(
                '{0}b data retrieved from FTP service.'.format(self._offset, )
            ),
            category='debug',
        )

    def parse_action_parameters(self):

        self._mimetype = self.process_label_substitutions(
            self.action_parameters.get(
                'mimetype',
                'application/octet-stream',
            )
        )

        self._hostname = self.process_label_substitutions(
            self.action_parameters.get('server')
        )
        self._filename = self.process_label_substitutions(
            self.action_parameters.get('filename')
        )

        passive = self.process_label_substitutions(
            self.action_parameters.get('passive', 'YES')
        )
        if not passive.upper() == 'NO':
            self._passive = True
        else:
            self._passive = False

        self._username = self.action_parameters.get('username', None)
        if self._username:
            self._username = self.process_label_substitutions(self._username)
            self._password = self.action_parameters.get(
                'password',
                '$__EMAIL__;',
            )
            self._password = self.process_label_substitutions(self._password)

        self._directory = self.action_parameters.get('directory', None)
        if self._directory:
            self._directory = self.process_label_substitutions(self._directory)

    def do_epilogue(self):
        pass
