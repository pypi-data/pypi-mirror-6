#!/usr/bin/env python
# Copyright (c) 2010, 2012, 2013
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
import shutil
from tempfile import mkstemp
from coils.core import Process, BLOBManager, CoilsException
from coils.core.logic import ActionCommand


class QueueProcessAction(ActionCommand):
    '''
    Queue a new process from execution. The input of this action will be
    the input message of the new process.
    '''
    __domain__ = "action"
    __operation__ = "queue-process"
    __aliases__ = ['queueProcess', 'queueProcessAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'text/plain'

    def _copy_xattrs(self, from_, to_, ):
        '''
        Copy object properties that look like XATTRs from the specified
        entity [likely the current process] to the specified target [the
        new "child" process being created].
        '''
        for prop in self._ctx.pm.get_properties(entity=from_):
            if (
                prop.namespace == 'http://www.opengroupware.us/oie' and
                prop.name.startswith('xattr_')
            ):
                self._ctx.property_manager.set_property(
                    entity=to_,
                    namespace='http://www.opengroupware.us/oie',
                    attribute=prop.name,
                    value=prop.get_value(),
                )

    def do_action(self):
        '''
        Create the new process and place it in a queued state
        '''
        input_handle = BLOBManager.ScratchFile(suffix='.message')
        shutil.copyfileobj(self.rfile, input_handle)
        route = self._ctx.run_command('route::get', name=self._route_name)
        if (route is not None):
            process = self._ctx.run_command(
                'process::new',
                values={
                    'route_id': route.object_id,
                    'handle': input_handle,
                },
            )
            process.state = 'Q'
            process.priority = self._priority
            self.wfile.write(unicode(process.object_id))
            if self._inherit_xattrs:
                self._copy_xattrs(from_=self.process, to_=process, )
        else:
            raise CoilsException(
                'No such route as {0}'.format(self._route_name, )
            )
        BLOBManager.Close(input_handle)

    def parse_action_parameters(self):
        '''
        Process the action parameters: routeName, priority, & 'inheritXATTRs'
        '''
        self._route_name = self.action_parameters.get('routeName', None)
        if (self._route_name is None):
            raise CoilsException('No such route to queue process.')

        self._priority = int(
            self.action_parameters.get('priority', self.process.priority)
        )

        self._inherit_xattrs = True
        if self.action_parameters.get('inheritXATTRs', 'YES').upper() == 'NO':
            self._inherit_xattrs = False
