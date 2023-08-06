#
# Copyright (c) 2011, 2012, 2013
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
from coils.core         import *
from coils.core.logic   import CreateCommand
from keymap             import COILS_TEAM_KEYMAP
from command            import TeamCommand

class CreateTeam(CreateCommand, TeamCommand):
    __domain__    = "team"
    __operation__ = "new"

    def prepare(self, ctx, **params):
        self.keymap = COILS_TEAM_KEYMAP
        self.entity = Team
        CreateCommand.prepare(self, ctx, **params)

    def check_run_permissions(self):
        if self._ctx.has_role( OGO_ROLE_SYSTEM_ADMIN  ):
            return
        raise AccessForbiddenException( 'Context lacks role; cannot create teams.' )

    def parse_parameters(self, **params):
        CreateCommand.parse_parameters(self, **params)

    def fill_missing_values(self):
        self.obj._is_team = 1
        if not self.obj.number:
            self.obj.number = 'OGo{0}'.format( self.obj.object_id )

    def run(self):
        # TODO: Grant this right to members of the 'team creators' team.
        if self._ctx.is_admin:
            CreateCommand.run(self)
            self.fill_missing_values()
            self.set_membership()
            self.save()
        else:
            raise CoilsException('Update of a team entity requires administrative privileges')
