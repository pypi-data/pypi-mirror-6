#
# Copyright (c) 2010, 2014
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
# THE SOFTWARE.
#
from coils.core import CoilsException
from coils.core.logic import ActionCommand
from coils.core.xml import Render as XML_Render


class TaskCommentAction(ActionCommand):
    '''
    Perform a comment on a Task, do not change it's status
    '''
    __domain__ = "action"
    __operation__ = "task-comment"
    __aliases__ = ['taskComment', 'taskCommentAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        '''
        Make a comment on the task, do not change it's status
        '''
        if (self._comment is None):
            # HACK: this isn't a reliable or efficient way to read input
            self._comment = self.rfile.read()
        task = self._ctx.run_command(
            'task::comment',
            values={
                'action': 'comment',
                'comment': self._comment,
            },
            id=self._task_id,
        )
        results = XML_Render.render(task, self._ctx)
        self.wfile.write(results)
        self.wfile.flush()
        self._comment = None

    def parse_action_parameters(self):
        self._comment = self.action_parameters.get('comment', None)
        if self._comment is not None:
            self._comment = self.process_label_substitutions(self._comment)
        self._task_id = self.action_parameters.get(
            'taskId', self.process.task_id,
        )
        if self._task_id is None:
            raise CoilsException(
                'Attempt to comment on task, but no task available.'
            )
