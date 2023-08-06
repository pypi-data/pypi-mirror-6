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
#
from coils.foundation import Project
from coils.core import Resource, Appointment
from coils.core.logic import SearchCommand
from keymap import COILS_RESOURCE_KEYMAP, COILS_APPOINTMENT_KEYMAP


class SearchResources(SearchCommand):
    __domain__ = "resource"
    __operation__ = "search"
    mode = None

    def __init__(self):
        SearchCommand.__init__(self)

    def prepare(self, ctx, **params):
        SearchCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        SearchCommand.parse_parameters(self, **params)

    def add_result(self, project):
        if (project not in self._result):
            self._result.append(project)

    def run(self):
        self._query = self._parse_criteria(
            self._criteria,
            Resource,
            COILS_RESOURCE_KEYMAP,
        )
        data = self._query.all()
        self.log.debug('query returned %d objects' % len(data))
        self.set_return_value(data)
        return


class SearchAppointments(SearchCommand):
    '''
    Search the database for appointments based on specified criteria
    '''
    __domain__ = 'appointment'
    __operation__ = 'search'

    def __init__(self):
        SearchCommand.__init__(self)

    def prepare(self, ctx, **params):
        SearchCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        SearchCommand.parse_parameters(self, **params)

    def add_result(self, appointment):
        if appointment not in self._result:
            self._result.append(appointment)

    def _custom_search_criteria(self, key, value, conjunction, expression, ):
        return SearchCommand._custom_search_criteria(
            self,
            key=key,
            value=value,
            conjunction=conjunction,
            expression=expression,
        )

    def run(self):
        keymap = COILS_APPOINTMENT_KEYMAP.copy()
        keymap.update(
            {'ownerid':         ['owner_id', 'int', None, ],
             'owner_id':        ['owner_id', 'int', None, ],
             'ownerobjectid':   ['owner_id', 'int', None, ],
             'modified':        ['modified', 'date', None, ], }
        )
        self._query = self._parse_criteria(
            self._criteria,
            Appointment,
            keymap,
        )
        data = self._query.all()
        self.set_return_value(data)
        return
