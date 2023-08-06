#
# Copyright (c) 2013
#  Adam Tauno Williams <awilliam@whitemice.org>
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
import zipfile
import shutil
from coils.core import CoilsException
from coils.core.logic import ActionCommand


class ExtractFileFromZIPArchive(ActionCommand):
    __domain__ = "action"
    __operation__ = "extract-from-zipfile"
    __aliases__ = [
        'extractFromZipArchive',
        'extractFromZipArchiveAction',
        'extractFromZipFile',
        'extractFromZipFileArchive', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return self._mimetype

    def do_action(self):

        #TODO: verify MIME-type of input message indicates ZIP content

        # Open the input message as a ZIP file
        zfile = zipfile.ZipFile(
            self.rfile, 'r',
        )

        zipinfo_to_extract = None
        if self._filename:
            try:
                zipinfo_to_extract = zfile.getinfo(self._filename)
            except KeyError:
                raise CoilsException(
                    'Zip file does not contain an object named "{0}"'.
                    format(self._filename, )
                )
        else:
            info_list = zfile.infolist()
            if info_list:
                zipinfo_to_extract = info_list[0]
                info_list = None  # Assist GC
            else:
                raise CoilsException(
                    'Zip contains no objects, nothing to extract'
                )

        zhandle = zfile.open(zipinfo_to_extract, 'r')
        shutil.copyfileobj(zhandle, self.wfile)
        self.wfile.flush()
        zfile.close()

    def parse_action_parameters(self):

        filename = self.action_parameters.get('filename', None)
        if filename:
            self._filename = self.process_label_substitutions(filename)
        else:
            self._filename = None

        self._mimetype = self.process_label_substitutions(
            self.action_parameters.get(
                'mimetype',
                'application/octet-stream',
            )
        )
