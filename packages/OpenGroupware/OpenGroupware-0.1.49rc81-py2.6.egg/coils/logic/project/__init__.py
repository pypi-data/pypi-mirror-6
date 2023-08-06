#
# Copyright (c) 2009, 2012, 2014
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
from get_project import GetProject
from accessmanager import ProjectAccessManager
from get_root_folder import GetProjectRootFolder
from get_documents import GetProjectDocuments
from get_notes import GetProjectNotes
from get_tasks import GetProjectTasks

from search_project import SearchProjects

# project::get-task-actions
from get_actions import GetProjectTaskActions

# project::get-contacts
from get_contacts import GetProjectContacts

# project::set-contacts
from set_contacts import SetProjectContacts

# project::get-enterprises
from get_enterprises import GetProjectEnterprises

# project::set-enterprises
from set_enterprises import SetProjectEnterprises

# project::new
from create_project import CreateProject

# project::set
from update_project import UpdateProject

# project::get-path
from get_path import GetProjectPath

# project::get-projects
from get_projects import GetChildProjects

# project::get-favorite
from get_favorites import GetFavorites

# project::set-favorite
from set_favorite import SetFavorite

# project::delete
from delete_project import DeleteProject

# project::assign-enterprise, project::assign-contact, project::assign-team
from assign_company import \
    AssignEnterpriseToProject, \
    AssignContactToProject, \
    AssignTeamToProject

# project::unassign-enterprise
from unassign_company import UnassignEnterpriseFromProject

# project::unassign-contact
from unassign_company import UnassignContactFromProject
