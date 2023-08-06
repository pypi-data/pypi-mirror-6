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
# THE SOFTWARE.
#
from datetime import datetime, timedelta
from coils.core import CoilsException
from coils.core.logic import ActionCommand


class ReapCollectionsAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "reap-collections"
    __aliases__ = ['reapCollections', 'reapCollectionsActions', ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):

        floor_date = datetime.now() - timedelta(days=self._minimum_age)

        criteria = [
            {'expression': 'EQUALS',
             'conjunction': 'AND',
             'key': 'kind',
             'value': self._kind_value, },
            {'expression': 'EQUALS',
             'conjunction': 'AND',
             'key': 'assignment_count',
             'value': 0, },
            {'expression': 'LT',
             'conjunction': 'AND',
             'key': 'created',
             'value': floor_date, },
        ]
        candidates = self._ctx.run_command(
            'collection::search',
            criteria=criteria,
        )
        for candidate in candidates:
            rights = self._ctx.access_manager.access_rights(candidate)
            if not set('wad').intersection(rights):
                self.log_message(
                    ('Collection OGo#{0} ignored due to insufficient '
                     'permissions'.format(candidate.object_id, )),
                    category='debug', )
                continue
            self._ctx.run_command(
                'collection::delete', object=candidate,
            )

    def parse_action_parameters(self):
        self._kind_value = self.action_parameters.get('kindString', None)
        if not self._kind_value:
            raise CoilsException(
                'No "kindString" specified for reapCollectionAction'
            )
        self._minimum_age = self.action_parameters.get('minimumAge', '1')
        self._minimum_age = long(self._minimum_age)
