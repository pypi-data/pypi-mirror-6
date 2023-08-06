#
# Copyright (c) 2013, 2014
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
import uuid
import traceback
import multiprocessing
import json
from coils.core import \
    send_email_using_project7000_template, \
    MultiProcessWorker, \
    AdministrativeContext, \
    PropertyManager, \
    get_yaml_struct_from_project7000

from events import \
    DOCUMENT_COLLECT_REQUEST,\
    DOCUMENT_COLLECT_DISCARDED,\
    DOCUMENT_COLLECT_FAILED,\
    DOCUMENT_COLLECT_COMPLETED,\
    DOCUMENT_DELETED, \
    DOCUMENT_BURST_REQUEST,\
    DOCUMENT_BURST_COMPLETED,\
    DOCUMENT_BURST_FAILED,\
    DOCUMENT_BURST_DISCARDED, \
    DOCUMENT_AUTOFILE_REQUEST, \
    DOCUMENT_AUTOFILE_COMPLETED, \
    DOCUMENT_AUTOFILE_FAILED, \
    DOCUMENT_AUTOFILE_DISCARDED, \
    DOCUMENT_SPECIAL_PROCESSING, \
    DOCUMENT_UNCOLLECT_REQUEST,\
    DOCUMENT_UNCOLLECT_DISCARDED,\
    DOCUMENT_UNCOLLECT_FAILED,\
    DOCUMENT_UNCOLLECT_COMPLETED

from utility import \
    NAMESPACE_MANAGEMENT,\
    ATTR_MANAGEMENT_COLLECTED,\
    ATTR_MANAGEMENT_COLLECTION_DESC,\
    get_inherited_property,\
    expand_labels_in_name,\
    ATTR_MANAGEMENT_BURST_TARGET,\
    ATTR_MANAGEMENT_BURSTED_FLAG, \
    ATTR_MANAGEMENT_AUTOFILE_TARGET, \
    ATTR_MANAGEMENT_UNCOLLECTION_DESC

from autofile_doc import DocumentAutoFile
from event_special_processing import DocumentSpecialProcessing
from event_pdf_bursting import DocumentPageBurstProcessor

COMMAND_MAP = {
    DOCUMENT_COLLECT_REQUEST: 'auto_collect_document',
    DOCUMENT_DELETED: 'process_document_deletion',
    DOCUMENT_AUTOFILE_REQUEST: 'autofile_document',
    DOCUMENT_BURST_REQUEST: 'burst_document',
    DOCUMENT_SPECIAL_PROCESSING: 'special_processing',
    DOCUMENT_UNCOLLECT_REQUEST: 'auto_uncollect_document',
}


from coils.core import Backend
from sqlalchemy import event


class EventWorker(MultiProcessWorker):

    def __init__(self, name, work_queue, event_queue, silent=True):
        MultiProcessWorker.__init__(
            self,
            name=name,
            work_queue=work_queue,
            event_queue=event_queue,
            silent=silent,
        )
        self.context = AdministrativeContext()
        self.configure_worker()

    def configure_worker(self):
        self._property_alias_map = get_yaml_struct_from_project7000(
            context=self.context,
            path='/PropertyAliases.yaml',
            access_check=False,
        )
        self.log.info(
            '{0} aliases loaded from PropertyAliases.yaml'.
            format(
                len(self._property_alias_map),
            )
        )

    def process_worker_message(self, command, payload, ):

        object_id = long(payload.get('objectId', 0))

        self.log.debug(
            'recieved command {0} for OGo#{1}'.
            format(command, object_id, )
        )
        if command in COMMAND_MAP:
            method = 'do_{0}'.format(COMMAND_MAP[command], )
            if hasattr(self, method):
                method = getattr(self, method)
                if method:
                    method(
                        object_id=object_id,
                        action=payload.get('action', 'unknown'),
                        message=payload.get('message', ''),
                        actor_id=payload.get('actorId',  0),
                        project_id=payload.get('projectId',  0),
                        version=payload.get('version', None)
                    )
            else:
                self.log.error(
                    'Command received with no corresponding implementation; '
                    'looking for "{0}"'.format(method))
        else:
            self.log.error('Unmapped command "{0}" received.'.format(command))
        self.context.db_close()

    def do_auto_collect_document(
        self,
        object_id,
        action,
        message,
        actor_id,
        project_id,
        version,
    ):

        document = self.context.run_command('document::get', id=object_id)
        if not document:
            self.enqueue_event(
                DOCUMENT_COLLECT_DISCARDED,
                (object_id, 'Document', 'Document not available', ), )
            return

        prop = self.context.property_manager.get_property(
            document,
            NAMESPACE_MANAGEMENT,
            ATTR_MANAGEMENT_COLLECTED)
        if prop:
            self.enqueue_event(DOCUMENT_COLLECT_DISCARDED,
                               (object_id,
                                'Document',
                                'Document already collected', ), )
            return

        collection_desc = get_inherited_property(
            self.context,
            document,
            NAMESPACE_MANAGEMENT,
            ATTR_MANAGEMENT_COLLECTION_DESC)
        if not collection_desc:
            self.enqueue_event(
                DOCUMENT_COLLECT_DISCARDED,
                (object_id, 'Document', 'No collection path defined.', ), )
            return

        try:
            collection_description = json.loads(collection_desc)
        except:
            self.enqueue_event(
                DOCUMENT_COLLECT_FAILED,
                (object_id, 'Document', traceback.format_exc(), ),
            )
            return
        else:
            collection_name = \
                expand_labels_in_name(collection_description.get('name', None))
            if not collection_name:
                self.enqueue_event(
                    DOCUMENT_COLLECT_FAILED,
                    (object_id,
                     'Document',
                     'Collection description has no name.', ), )
                return

            collection_description['name'] = collection_name

        criteria = [{'key': 'name',
                     'value': collection_description['name'], }, ]
        if collection_description.get('kind', None):
            criteria.append({'key': 'kind',
                             'value': collection_description['kind'], }, )

        collection = self.context.run_command('collection::search',
                                              criteria=criteria)
        if not collection:
            collection = self.context.r_c('collection::new',
                                          values=collection_description)
            collection.project_id = document.project_id
            self.log.info('Automatically created new collection OGo#{0}'.
                          format(collection.object_id))
        else:
            '''
            Searches always have multiple results, we are taking the first one
            '''
            collection = collection[0]
            self.log.debug(
                'Discovered OGo#{0} [Collection] that matches descriptor'.
                format(collection.object_id))

        self.context.r_c('object::assign-to-collection',
                         collection=collection,
                         entity=document)

        self.log.debug(
            'OGo#{0} [Document] automatically joined to OGo#{1} [Collection]'.
            format(document.object_id, collection.object_id, ))

        self.context.pm.set_property(
            document,
            NAMESPACE_MANAGEMENT,
            ATTR_MANAGEMENT_COLLECTED,
            'OGo#{0};name:"{1}";kind:"{2}"'.format(
                collection.object_id,
                collection_description['name'],
                collection_description.get('kind', None)))

        self.log.debug(
            'OGo#{0} [Document] collection join recorded via property'.
            format(document.object_id, ))

        self.context.commit()

        self.log.debug(
            'OGo#{0} [Document] collection join committed.'.
            format(document.object_id, ))

        self.enqueue_event(
            DOCUMENT_COLLECT_COMPLETED,
            (object_id, 'Document', None, ))

        return

    def do_auto_uncollect_document(
        self,
        object_id,
        action,
        message,
        actor_id,
        project_id,
        version,
    ):

        document = self.context.run_command('document::get', id=object_id)
        if not document:
            self.enqueue_event(
                DOCUMENT_COLLECT_DISCARDED,
                (object_id,
                 'Document',
                 'Document not available for uncolleciton', ),
            )
            return

        uncollection_desc = get_inherited_property(
            self.context,
            document,
            NAMESPACE_MANAGEMENT,
            ATTR_MANAGEMENT_UNCOLLECTION_DESC)
        if not uncollection_desc:
            self.enqueue_event(
                DOCUMENT_UNCOLLECT_DISCARDED,
                (object_id,
                 'Document',
                 'No un-collection spec defined.', ), )
            return

        try:
            uncollection_description = json.loads(uncollection_desc)
        except ValueError as exc:
            self.log.exception(exc)
            self.enqueue_event(
                DOCUMENT_UNCOLLECT_FAILED,
                (object_id,
                 'Document',
                 'JSON data expected, but cannot deserialize.\n'
                 '{1}'.format(traceback.format_exc(), ),
                 ),
            )
        except Exception as exc:
            self.log.exception(exc)
            self.enqueue_event(
                DOCUMENT_UNCOLLECT_FAILED,
                (object_id, 'Document', traceback.format_exc(), ),
            )
            return
        else:
            uncollection_kind = \
                uncollection_description.get('kind', None)
            uncollection_properties = \
                uncollection_description.get('properties', None)
            uncollection_mode = \
                uncollection_description.get('mode', 'ALL')
            uncollection_mode = uncollection_mode.upper()
            if not uncollection_kind or not uncollection_properties:
                self.enqueue_event(
                    DOCUMENT_UNCOLLECT_FAILED,
                    (object_id,
                     'Document',
                     'Uncollection spec is incomplete', ), )
                return

        uncollection_properties = \
            [PropertyManager.Parse_Property_Name(p)
             for p in uncollection_properties]

        if uncollection_mode == 'ALL':
            qualify_flag = True
        else:
            qualify_flag = False

        for (namespace, attribute, ) in uncollection_properties:
            p = self.context.property_manager.get_property(
                entity=document,
                namespace=namespace,
                name=attribute, )
            if p and uncollection_mode == 'ANY':
                qualify_flag = True
                break
            elif uncollection_mode == 'ALL' and not p is None:
                qualify_flag = False
                break

        if not qualify_flag:
            self.enqueue_event(
                DOCUMENT_UNCOLLECT_DISCARDED,
                (object_id,
                 'Document',
                 'Did not meet uncollection criteria', ),
            )
            return

        uncollection_description = {'kind': uncollection_kind, }

        criteria = [
            {'key': 'kind',
             'value': uncollection_kind,
             'expression': 'EQUALS',
             'conjunction': 'AND', },
            {'key': 'assigned_id',
             'value': document.object_id,
             'expression': 'EQUALS',
             'conjunction': 'AND', }, ]

        collections = self.context.run_command('collection::search',
                                               criteria=criteria, )
        if not collections:
            self.enqueue_event(
                DOCUMENT_UNCOLLECT_DISCARDED,
                (object_id,
                 'Document',
                 'Not assigned to any matching collection', ),
            )
            return

        for collection in collections:
            self.context.run_command(
                'collection::delete-assignment',
                collection=collection,
                entity=document,
            )
        self.context.commit()

        self.log.debug(
            'OGo#{0} [Document] uncollected'.
            format(document.object_id, ))

        self.enqueue_event(
            DOCUMENT_UNCOLLECT_COMPLETED,
            (object_id, 'Document', None, ))

    def process_document_deletion(self, object_id):

        # Collections

        # Object-Links

        return

    def do_autofile_document(
        self,
        object_id,
        action,
        message,
        actor_id,
        project_id,
        version,
    ):

        # Document Available?
        document = self.context.type_manager.get_entity(object_id)
        if not document:
            self.log.warn(
                'OGo#{0} [Document] not available for auto-file.'.
                format(object_id, ))
            self.enqueue_event(
                DOCUMENT_BURST_FAILED,
                (object_id,
                 'OGo#{0} [Document] not available for auto-file'.
                 format(object_id, ), )
            )
            # Document NOT available
            self.context.rollback()
            return

        # Auto-file Target?
        target_path = get_inherited_property(
            self.context,
            document,
            NAMESPACE_MANAGEMENT,
            ATTR_MANAGEMENT_AUTOFILE_TARGET, )
        if not target_path:
            self.context.rollback()
            self.enqueue_event(
                DOCUMENT_BURST_DISCARDED,
                (object_id, 'No auto-filing target specified.', ), )
            # No burst path
            return

        autofiler = DocumentAutoFile(
            self.context,
            document,
            version,
            propmap=self._property_alias_map,
        )

        try:
            target_folder, \
                delete_after, = autofiler.resolve_path(target_path)
        except Exception as exc:
            self.send_administrative_notice(
                subject='Exception auto-filing OGo#{0}'.
                        format(document.object_id, ),
                message='Failure walking auto-file URI to destination.\n'
                        'URI {0}\n'
                        '{1}\n'.format(target_path,
                                       traceback.format_exc(), ),
                urgency=7,
                category='document', )
            self.context.rollback()
            self.enqueue_event(
                DOCUMENT_AUTOFILE_FAILED,
                (object_id,
                 'Attempt to auto-file document OGo#{0} failed'.
                 format(object_id, )), )
            return

        if not target_folder:
            self.log.debug(
                'Target URI "{0}" for auto-filing of OGo#{1} [Document]'
                'cannot be marshalled'.
                format(target_path, document.object_id))
            self.context.rollback()
            self.enqueue_event(
                DOCUMENT_AUTOFILE_FAILED,
                (object_id,
                 'Target  "{0}" does not exist'.format(target_path, )), )
            # Cannot marshall target

            return

        result_code = autofiler.file_to(target_folder)

        if result_code == DOCUMENT_AUTOFILE_COMPLETED:

            if not delete_after:
                self.context.audit_at_commit(
                    object_id=document.object_id,
                    action='10_commented',
                    message='Copy of document auto-filed to OGo#{0}'.
                            format(target_folder.object_id, ))
            else:
                self.context.run_command('document::delete', object=document, )
            self.context.commit()
            self.enqueue_event(
                DOCUMENT_AUTOFILE_COMPLETED,
                (object_id,
                 'Document OGo#{0} auto-filed successfully'.
                 format(object_id, )), )
            return

        elif result_code == DOCUMENT_AUTOFILE_DISCARDED:
            self.context.rollback()
            self.context.audit_at_commit(
                object_id=document.object_id,
                action='10_commented',
                message='Request to auto-file document discarded as a no-op')
            self.context.commit()
            self.enqueue_event(
                DOCUMENT_AUTOFILE_DISCARDED,
                (object_id,
                 'Request to auto-file document OGo#{0} was discarded'.
                 format(object_id, )), )
            return

        # result was neither completed or discarded, so it failed.

        self.context.rollback()
        self.context.audit_at_commit(
            object_id=document.object_id,
            action='10_commented',
            message='Unable to auto-file OGo#{0} to specified target'.
                    format(document.object_id, ))
        self.context.commit()
        self.enqueue_event(
            DOCUMENT_AUTOFILE_FAILED,
            (object_id,
             'Attempt to auto-file document OGo#{0} failed'.
             format(document.object_id, )), )

        return

    def do_burst_document(
        self,
        object_id,
        action,
        message,
        actor_id,
        project_id,
        version,
    ):
        '''
          Step 1: is the document available?
          Step 2: is a burst target defined that applies to the document?
          Step 3: has the document already been bursted [avoid loops!]
          Step 4: Burst
          Step 4.1:  create burster
          Step 4.2:  resolve target
          Step 4.3:  burst
          Step 4.4:  burst result notification
        '''
        processor = DocumentPageBurstProcessor(
            worker=self,
            propmap=self._property_alias_map,
        )
        if processor.run(
            document_id=object_id,
            version=version,
            action=action,
            actor_id=actor_id,
            project_id=project_id,
        ):
            self.log.debug(
                'Document bursting completed for OGo#{0}'.
                format(object_id, )
            )
        else:
            self.log.debug(
                'Document bursting not completed for OGo#{0}'.
                format(object_id, )
            )
        processor.close()

        return

    def do_special_processing(
        self,
        object_id,
        action,
        message,
        actor_id,
        project_id,
        version,
    ):
        self.log.debug(
            'Special processing requested for OGo#{0}'.format(object_id, )
        )
        processor = DocumentSpecialProcessing(
            worker=self,
            propmap=self._property_alias_map,
        )
        if processor.run(
            document_id=object_id,
            version=version,
            action=action,
            actor_id=actor_id,
            project_id=project_id,
        ):
            self.log.debug(
                'Special processing completed for OGo#{0}'.
                format(object_id, )
            )
        else:
            self.log.debug(
                'Special processing not completed for OGo#{0}'.
                format(object_id, )
            )
        processor.close()
