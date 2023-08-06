#
# Copyright (c) 2014
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
from coils.foundation import Folder
from coils.core.logic import SearchCommand
from coils.core import CoilsException
from keymap import COILS_FOLDER_KEYMAP


def descend_yielding(context, folder, depth=0, maxdepth=-1, ):
    yield folder
    if (
        maxdepth < 0 or
        depth < maxdepth
    ):
        for candidate in folder.folders:
            for child in descend_yielding(context=context,
                                          folder=candidate,
                                          depth=depth + 1,
                                          maxdepth=maxdepth, ):
                yield child


class SearchFolders(SearchCommand):
    __domain__ = "folder"
    __operation__ = "search"
    mode = None

    def __init__(self):
        SearchCommand.__init__(self)

    def prepare(self, ctx, **params):
        SearchCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        SearchCommand.parse_parameters(self, **params)

    def _custom_search_criteria(self, key, value, conjunction, expression, ):

        if len(key) > 1:
            # No compound custom keys supported
            return (None, None, None, None, None, )

        key = key[0]
        if key == 'topfolderid' and expression == 'EQUALS':

            folder_id = None
            try:
                folder_id = long(value)
            except:
                raise CoilsException(
                    'Non-numeric value passed to search criteria topFolderId'
                )

            folder = self._ctx.r_c('folder::get', id=folder_id, )
            if not folder:
                raise CoilsException(
                    'Value "{0}" provided for topFolderId criteria of folder'
                    ' search does not materialize to a Folder entity'.
                    format(value, )
                )

            folder_ids = list()
            folder_ids.extend(
                [x.object_id for x in
                 descend_yielding(self._ctx, folder, maxdepth=25, )]
            )

            return (Folder, 'folder_id', folder_ids, conjunction, 'IN', )

        # unsupported custom key
        return (None, None, None, None, None, )

    def add_result(self, folder):
        if (folder not in self._result):
            self._result.append(folder)

    def run(self):
        keymap = COILS_FOLDER_KEYMAP.copy()
        keymap.update(
            {'created':         ['created', 'date', None, ],
             'creator_id':      ['creator_id', 'int', None, ],
             'creatorid':       ['creator_id', 'int', None, ],
             'creatorobjectid': ['creator_id', 'int', None, ],
             'ownerid':         ['owner_id', 'int', None, ],
             'owner_id':        ['owner_id', 'int', None, ],
             'ownerobjectid':   ['owner_id', 'int', None, ],
             'modified':        ['modified', 'date', None, ], }
        )
        self._query = self._parse_criteria(self._criteria, Folder, keymap)
        data = self._query.all()
        self.log.debug('query returned {0} objects'.format(len(data), ))
        self.set_return_value(data)
        return
