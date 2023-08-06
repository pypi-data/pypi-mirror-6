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
# THE SOFTWARE
#
from coils.core import BLOBManager, CoilsException
from event_processor import DocumentEventProcessor
from events import \
    DOCUMENT_SPECIAL_DISCARDED, \
    DOCUMENT_SPECIAL_FAILED, \
    DOCUMENT_SPECIAL_COMPLETED, \
    ENQUEUE_PROCESS
from utility import \
    NAMESPACE_MANAGEMENT, \
    ATTR_MANAGEMENT_SPECIAL_PROCESSING, \
    ATTR_MANAGEMENT_SPECIAL_SOURCE_ID, \
    ATTR_MANAGEMENT_SPECIAL_SOURCE_FILENAME, \
    ATTR_MANAGEMENT_SPECIAL_SOURCE_CHECKSUM, \
    ATTR_MANAGEMENT_SPECIAL_FOLDER_ID


class DocumentSpecialProcessing(DocumentEventProcessor):
    _event_name = 'special processing'
    _discard_code = DOCUMENT_SPECIAL_DISCARDED
    _failure_code = DOCUMENT_SPECIAL_FAILED
    _completed_code = DOCUMENT_SPECIAL_COMPLETED
    _prop_namespace = NAMESPACE_MANAGEMENT
    _prop_attribute = ATTR_MANAGEMENT_SPECIAL_PROCESSING

    def run(self, document_id, version, action, actor_id, project_id, ):

        document = self.get_document(object_id=document_id, )
        # Document Available?
        if not document:
            return False

        target_string = self.get_inherited_property(document=document, )
        if not target_string:
            return False

        netloc, path, parameters, = self.parse_target_string(
            document=document, string_value=target_string
        )
        if netloc is None:
            return False

        action_filter = ['00_created', '05_changed', ]
        if 'actions' in parameters:
            action_filter = \
                [x.strip().lower() for x in parameters['actions'].split(',')]
        if action not in action_filter:
            self.worker.enqueue_event(
                self.discard_code,
                (document.object_id,
                 'Special processing of OGo#{0} discarded due the filtered '
                 'action "{1}", configured actions are "{2}"'.
                 format(document.object_id, action, ','.join(action_filter)),
                 ),
            )
            return False

        rfile = None
        try:
            route = self.context.run_command('route::get', name=path, )
            if not route:
                raise CoilsException(
                    'Unable to marshall route {0} for {1} of OGo#{2}'.
                    format(path, self._event_name, document.object_id, )
                )
                return False

            rfile, mimetype, = self.get_document_handle(document, version, )
            if not rfile:
                raise CoilsException(
                    'Cannot marshall handle for version {0} of OGo#{1}'.
                    format(version, document.object_id, )
                )

            process = self.context.run_command(
                'process::new',
                values={
                    'route_id': route.object_id,
                    'handle':  rfile,
                    'priority': 210,
                },
                mimetype=mimetype,
            )
            # Store the source document id and file name as bject property
            # on the new workflow process
            self.context.property_manager.set_property(
                process,
                NAMESPACE_MANAGEMENT,
                ATTR_MANAGEMENT_SPECIAL_SOURCE_ID,
                unicode(document.object_id),
            )
            self.context.property_manager.set_property(
                process,
                NAMESPACE_MANAGEMENT,
                ATTR_MANAGEMENT_SPECIAL_SOURCE_FILENAME,
                document.get_file_name(),
            )
            self.context.property_manager.set_property(
                process,
                NAMESPACE_MANAGEMENT,
                ATTR_MANAGEMENT_SPECIAL_SOURCE_CHECKSUM,
                document.checksum,
            )
            self.context.property_manager.set_property(
                process,
                NAMESPACE_MANAGEMENT,
                ATTR_MANAGEMENT_SPECIAL_FOLDER_ID,
                unicode(document.folder_id),
            )
            # Store any XATTR values from the URI on the process
            for key, value in parameters.items():
                if key.startswith('xattr_'):
                    self.context.property_manager.set_property(
                        process,
                        'http://www.opengroupware.us/oie',
                        'xattr_{0}'.format(key[6:].lower(), ),
                        value,
                    )

            self.context.audit_at_commit(
                object_id=document.object_id,
                action='10_commented',
                message='Workflow process OGo#{0} created from route "{1}" '
                        'for special processing of document version {2}'.
                        format(
                            process.object_id,
                            route.name,
                            version,
                        )
            )

            self.context.commit()
            self.worker.log.info(
                'Workflow process OGo#{0} created'.format(process.object_id, )
            )

            self.worker.enqueue_event(
                ENQUEUE_PROCESS,
                (process.object_id, ),
            )
        except Exception as exc:
            # Generic failure
            self.worker.log.exception(exc)
            self.worker.enqueue_event(
                self.failure_code,
                (document.object_id, unicode(exc),),
            )
            return False
        else:
            # Success
            self.worker.enqueue_event(
                self.completed_code,
                (document.object_id,
                 'Completed {0} of OGo#{1} for action "{2}"'.
                 format(
                     self.event_name,
                     document.object_id,
                     action, ),
                 ),
            )
            return True
        finally:
            # Make sure there is no derelict hanging on to stuff
            process = None
            route = None
            document = None
            if rfile:
                BLOBManager.Close(rfile)
