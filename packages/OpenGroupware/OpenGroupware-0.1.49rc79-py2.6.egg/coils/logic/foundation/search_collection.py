#
# Copyright (c) 2011, 2013, 2014
#   Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core import Collection, CollectionAssignment
from coils.core.logic import SearchCommand
from keymap import COILS_COLLECTION_KEYMAP


class SearchCollections(SearchCommand):
    # TODO: Does searching membership work?
    __domain__ = "collection"
    __operation__ = "search"
    mode = None

    def __init__(self):
        SearchCommand.__init__(self)

    def prepare(self, ctx, **params):
        SearchCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        SearchCommand.parse_parameters(self, **params)

    def add_result(self, collection):
        if (collection not in self._result):
            self._result.append(collection)

    def run(self):
        keymap = COILS_COLLECTION_KEYMAP.copy()
        keymap.update(
            {'created':          ['created', 'date', None, ],
             'assignment_count': ['assignment_count', 'int', None, ], }
        )
        self._query = self._parse_criteria(
            self._criteria,
            Collection,
            keymap,
        )
        data = self._query.all()
        self.set_return_value(data)
        return

    def _custom_search_criteria(self, key, value, conjunction, expression, ):
        if key[0] == 'assigned_id':
            return (
                CollectionAssignment,
                'assigned_id',
                value,
                conjunction,
                expression,
            )
        return SearchCommand._custom_search_criteria(
            self,
            key=key,
            value=value,
            conjunction=conjunction,
            expression=expression,
        )
