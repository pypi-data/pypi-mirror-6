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
import datetime
from lxml import etree
from coils.core import *
from coils.core.logic import ActionCommand
from coils.core.xml import Render as XML_Render
from sqlalchemy import and_, or_, not_
from coils.core import send_email_using_project7000_template


class UserTaskReport(ActionCommand):
    __domain__ = "action"
    __operation__ = "user-task-report"
    __aliases__ = ['userTaskReportAction', 'userTaskReport', ]

    def __init__(self):
        ActionCommand.__init__(self)

    def _fetch_current_todo_statistics(self, context,):

        TODAY = datetime.date.today()
        TOMORROW = datetime.date.today() + datetime.timedelta(days=1, )
        YESTERDAY = datetime.date.today() + datetime.timedelta(days=-1, )

        result = {
            'stats': {'00_created': 0,
                      '20_processing': 0,
                      '02_rejected': 0,
                      '25_done': 0, },
            'overdue': [],
            'start-today': [],
            'start-tomorrow': [],
            'due-today': [],
            'due-tomorrow': [],
        }

        query = context.db_session().query(Task).\
            filter(
                and_(
                    Task.executor_id.in_(context.context_ids),
                    Task.state != '30_archived',
                )
            )

        for task in query.all():
            result['stats'][task.state] += 1
            if task.state not in ('25_done', '02_rejected'):
                if task.start.date() == TODAY:
                    result['start-today'].append(task)
                if task.end.date() == TODAY:
                    result['due-today'].append(task)
                if task.start.date() == TOMORROW:
                    # Starting Tommorow
                    result['start-tomorrow'].append(task)
                if task.end.date() == TOMORROW:
                    # Starting Tommorow
                    result['due-tomorrow'].append(task)
                if task.end.date() < TODAY:
                    # Overdue
                    result['overdue'].append(task)

        return result

    def _fetch_current_delegated_statisitcs(self, context,):
        result = {}
        query = context.db_session().query(Task).\
            filter(
                and_(
                    Task.owner_id == context.account_id,
                    not_(Task.executor_id.in_(context.context_ids)),
                    Task.state != '30_archived',
                )
            )
        for task in query.all():
            if task.executor_id not in result:
                result[task.executor_id] = {
                    '00_created': 0,
                    '20_processing': 0,
                    '02_rejected': 0,
                    '25_done': 0,
                }
            result[task.executor_id][task.state] += 1
        return result

    def _fetch_delegated_task_action_statistics(
        self,
        context,
        range_start,
        range_end,
    ):
        '''
        Action stats from delegated list
        '''

        result = {}

        query = context.db_session().query(TaskAction).\
            filter(
                and_(
                    TaskAction.actor_id != context.account_id,
                    TaskAction.action_date > range_start,
                    TaskAction.action_date < range_end,
                )
            )
        query = query.join(Task).filter(Task.owner_id == context.account_id)

        for action in query.all():
            if action.actor_id not in result:
                result[action.actor_id] = {
                    'actor_id': action.actor_id,
                    '00_created': 0,
                    '05_accepted': 0,
                    '02_rejected': 0,
                    '10_commented': 0,
                    '25_done': 0,
                    '30_archived': 0,
                }
            result[action.actor_id][action.action] += 1

        return result

    def _fetch_user_task_action_statistics(
        self,
        context,
        range_start,
        range_end,
    ):
        '''
        Action stats from users list
        '''

        result = {
            '00_created': 0,
            '05_accepted': 0,
            '10_commented': 0,
            '02_rejected': 0,
            '25_done': 0,
            '30_archived': 0,
        }

        query = context.db_session().query(TaskAction).\
            filter(
                and_(
                    TaskAction.actor_id == context.account_id,
                    TaskAction.action_date > range_start,
                    TaskAction.action_date < range_end,
                )
            )

        for action in query.all():

            result[action.action] += 1

        return result

    def _fetch_current_project_statistics(
        self,
        context,
    ):

        report = {}

        query = context.db_session().query(Task).\
            filter(
                and_(
                    Task.state != '30_archived',
                    Task.project_id is not None,
                )
            )
        query = query.join(Project)
        query = query.join(ProjectAssignment).\
            filter(
                ProjectAssignment.child_id.in_(context.context_ids),
            )
        query = query.enable_eagerloads(False)

        for task in query.all():
            if task.project is None:
                continue
            if task.project.number not in report:
                report[task.project.number] = {
                    'name': task.project.name.strip(),
                    'project_id': task.project_id,
                    '00_created': 0,
                    '20_processing': 0,
                    '02_rejected': 0,
                    '25_done': 0,
                }
            report[task.project.number][task.state] += 1

        return report

    def _fetch_project_task_statistics(
        self,
        context,
        range_start,
        range_end,
    ):
        #Action stats on project tasks

        report = {}

        query = context.db_session().query(TaskAction).\
            filter(
                and_(
                    TaskAction.action_date > range_start,
                    TaskAction.action_date < range_end,
                )
            )
        query = query.join(Task)
        query = query.join(Project)
        query = query.join(ProjectAssignment).\
            filter(ProjectAssignment.child_id.in_(context.context_ids))
        for action in query.all():
            if action.task and action.task.project:
                if action.task.project.number not in report:
                    report[action.task.project.number] = {
                        'name': action.task.project.name,
                        'number': action.task.project.number,
                        'project_id': action.task.project.object_id,
                        '00_created': 0,
                        '05_accepted': 0,
                        '02_rejected': 0,
                        '10_commented': 0,
                        '25_done': 0,
                        '30_archived': 0,
                    }
                report[action.task.project.number][action.action] += 1

        return report

    def _fetch_principal_list(self, context, ):

        class NullResult(object):

            @property
            def string_value(self):
                return ''

        null = NullResult()

        report = {}
        contacts = context.run_command(
            'account::get-all',
            orm_hints=('zogi', 8, ),
        )
        for contact in contacts:
            email = contact.company_values.get('email1', null).string_value
            report[contact.object_id] = {
                'objectId': contact.object_id,
                'entityName': 'Contact',
                'displayName': contact.get_display_name(),
                'version': contact.version if contact.version else 0,
                'login': contact.login,
                'email': email if email else '',
            }

        for team in context.run_command('team::get'):
            report[team.object_id] = {
                'objectId': team.object_id,
                'entityName': 'Team',
                'displayName': team.get_display_name(),
                'version': team.version if team.version else 0,
                'login': team.number,
                'email': team.email if team.email else '',
            }

        return report

    def do_action(self):

        TODAY = datetime.date.today()
        if self._day_span > 0:
            RANGE_START = TODAY
            RANGE_END = \
                datetime.date.today() + \
                datetime.timedelta(days=self._day_span, )
        else:
            RANGE_START = \
                datetime.date.today() + \
                datetime.timedelta(days=self._day_span, )
            RANGE_END = TODAY

        report = {}
        report['todo'] = \
            self._fetch_current_todo_statistics(self._ctx)
        report['delegated'] = \
            self._fetch_current_delegated_statisitcs(self._ctx)
        report['project'] = \
            self._fetch_current_project_statistics(self._ctx)
        report['delegated-actions'] = \
            self._fetch_delegated_task_action_statistics(
                self._ctx, RANGE_START, RANGE_END,
            )
        report['user-actions'] = \
            self._fetch_user_task_action_statistics(
                self._ctx, RANGE_START, RANGE_END,
            )
        report['project-actions'] = \
            self._fetch_project_task_statistics(
                self._ctx, RANGE_START, RANGE_END,
            )

        send_email_using_project7000_template(
            self._ctx,
            subject=self._message_subject,
            to_address=self._to_address,
            template_path=self._template_path,
            regarding_id=self._ctx.account_id,
            parameters={
                'report': report,
                'principals': self._fetch_principal_list(self._ctx),
                'range_start': RANGE_START,
                'range_end': RANGE_END,
            },
        )

    def parse_action_parameters(self):
        self._template_path = \
            self.action_parameters.get(
                'template',
                'Administration/Workflow/Reports/UserTaskReport.mako',
            )
        self._day_span = long(
            self.process_label_substitutions(
                self.action_parameters.get('daySpan', '1')
            )
        )
        self._message_subject = self.process_label_substitutions(
            self.action_parameters.get('subject', 'Task Report')
        )
        self._to_address = self.process_label_substitutions(
            self.action_parameters.get('to', self._ctx.email, )
        )
