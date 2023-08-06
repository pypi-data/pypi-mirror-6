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
# THE SOFTWARE.
#
from sqlalchemy import and_
from coils.foundation.alchemy.doc import _Doc
from coils.core import Folder, Document, CoilsException
from coils.core.logic import GetCommand

'''
USAGE EXAMPLE:
    from coils.core import *
    initialize_COILS()
    ctx = AdministrativeContext()
    project = ctx.r_c('project::get', number='test123', )
    folder = ctx.r_c('project::get-root-folder', project=project, )
    doc_list = ctx.r_c('folder::ls-subdocuments', folder=folder, )
'''


class ListSubDocuments(GetCommand):
    '''
    Returns a list of all the listable documents under the specified folder
    or folder ids.  Subordinate folder entities are not included in the result,
    and archived objects are excluded as well; the result array will be only
    Document entities.
    '''
    __domain__ = "folder"
    __operation__ = "ls-subdocuments"
    mode = None

    def __init__(self):
        GetCommand.__init__(self)

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        if (len(self.object_ids) == 0):
            if ('folder' in params):
                '''
                TODO: Test that the reference value is actually a folder entity
                '''
                self.object_ids.append(params['folder'].object_id)
            else:
                raise CoilsException('No folder specified to list')
        self._name = params.get('name', None)

    def enumerate_folder(self, folder):
        result = list()
        query = self._ctx.db_session().query(_Doc).\
            filter(
                and_(
                    _Doc.folder_id == folder.object_id,
                    _Doc.status != 'archived',
                )
            )
        for obj in query.all():
            if isinstance(obj, Document):
                result.append(obj)
            elif isinstance(obj, Folder):
                result.extend(self.enumerate_folder(obj))
        return result

    def run(self):
        self.set_multiple_result_mode()

        query = self._ctx.db_session().query(Folder).\
            filter(
                and_(
                    Folder.folder_id.in_(self.object_ids),
                    Folder.status != 'archived',
                )
            )

        contents = list()
        for folder in query.all():
            contents.extend(
                self.enumerate_folder(folder)
            )

        self.set_return_value(contents, right='l', )
