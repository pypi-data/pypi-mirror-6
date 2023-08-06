
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
import logging
import shutil
import signal
import time
import random
import traceback
from coils.foundation.api.pypdf2 import PdfFileReader, PdfFileWriter

from coils.core import \
    walk_ogo_uri_to_folder, \
    Document, \
    Folder, \
    CoilsException, \
    parse_ogo_uri, \
    BLOBManager, \
    send_email_using_project7000_template, \
    PropertyManager, \
    get_yaml_struct_from_project7000

from coils.core import parse_ogo_uri
from utility import expand_labels_in_name, get_inherited_property
from event_processor import DocumentEventProcessor

from events import \
    DOCUMENT_BURST_REQUEST,\
    DOCUMENT_BURST_COMPLETED,\
    DOCUMENT_BURST_FAILED,\
    DOCUMENT_BURST_DISCARDED

from utility import \
    NAMESPACE_MANAGEMENT,\
    get_inherited_property,\
    expand_labels_in_name,\
    ATTR_MANAGEMENT_BURST_TARGET,\
    ATTR_MANAGEMENT_BURSTED_FLAG, \
    ATTR_MANAGEMENT_SOURCE_DOCUMENT_ID, \
    ATTR_MANAGEMENT_SOURCE_DOCUMENT_PAGE, \
    ATTR_MANAGEMENT_BURSTED_FLAG, \
    ATTR_MANAGEMENT_SOURCE_DOCUMENT_PAGE_COUNT

CONVERSION_TIMEOUT_SECONDS = 60

BURSTFAIL_DOCUMENT_TEMPLATE =\
    '/Templates/BurstingFailure.mako'


class TimeOutAlarm(Exception):
    pass


def timeout_alarm_handler(signum, frame):
    raise TimeOutAlarm


class BurstingTimeOutException(Exception):
    pass


def GenerateUniqueFileName(document, counter=0):
    if document.extension:
        return '{0}-{1:0>5}-{2}-{3}.{4}'.\
               format(document.name.lower(),
                      counter,
                      long(time.time() * 1000),
                      random.randrange(10000, 99999),
                      document.extension, )
    else:
        return '{0}-{1:0>5}-{2}-{3}'.\
               format(document.name.lower(),
                      counter,
                      long(time.time() * 1000),
                      random.randrange(10000, 99999), )


class DocumentPageBurstProcessor(DocumentEventProcessor):
    _event_name = 'page bursted'
    _discard_code = DOCUMENT_BURST_DISCARDED
    _failure_code = DOCUMENT_BURST_FAILED
    _completed_code = DOCUMENT_BURST_DISCARDED
    _prop_namespace = NAMESPACE_MANAGEMENT
    _prop_attribute = ATTR_MANAGEMENT_BURST_TARGET
    context = None
    propmap = None
    worker = None

    def __init__(self,  worker, propmap):
        DocumentEventProcessor.__init__(self, worker, propmap, )
        self.log = worker.log

    def resolve_path(self, target_path):

        all_copy_enabled = False
        copy_on_failure = False
        error_folder_id = None
        on_fail_notify = None
        folder, arguments, = walk_ogo_uri_to_folder(
            context=self.context,
            uri=target_path,
            create_path=True,
            default_params={
                'allcopyenabled': 'NO',
                'copyonfailure': 'NO',
                'errorfolderid': None,
                'onfailnotify': None,
            }
        )
        if arguments['allcopyenabled'].upper() == 'YES':
            all_copy_enabled = True
        if arguments['copyonfailure'].upper() == 'YES':
            copy_on_failure = True
        if arguments['errorfolderid']:
            error_folder_id = long(arguments['errorfolderid'])
        on_fail_notify = arguments['onfailnotify']

        return \
            folder, \
            all_copy_enabled, \
            copy_on_failure, \
            error_folder_id, \
            on_fail_notify

    def burst_to(
        self,
        document,
        folder,
        all_copy_enabled=False,
    ):
        self.last_page_count = 0
        self.last_exception = None
        mimetype = self.context.type_manager.get_mimetype(document)
        if mimetype in ('application/pdf', 'application/x-pdf', ):
            self.log.info(
                'PDF document OGo#{0} will be page bursted'.
                format(document.object_id, )
            )
            return self.burst_pdf_to(document=document, folder=folder, )
        elif all_copy_enabled:
            self.log.info(
                'Non-PDF document, bursting OGo#{0} as whole document copy'.
                format(document.object_id, )
            )
            return self.copy_to(document=document, folder=folder)
        else:
            return DOCUMENT_BURST_DISCARDED

    def copy_to(self, document, folder):
        '''
        Fall back to copy to processing due to either a bursting error or
        the document being of an unburstable MIME type.
        '''

        filename = GenerateUniqueFileName(document)

        burstling = None
        if document.folder.object_id == folder.object_id:
            burstling = document
        else:
            rfile = self.context.run_command(
                'document::get-handle',
                document=document,
            )
            if not rfile:
                return DOCUMENT_BURST_FAILED
            burstling = self.context.run_command(
                'document::new',
                folder=folder,
                name=filename,
                handle=rfile,
                values={},
            )

        self.post_processing(
            document=document,
            burstling=burstling,
            counter=0,
            of_pages=0,
        )

        self.log.info(
            'Bursted copy of OGo#{0} is OGo#{1} in OGo#{2}'.
            format(
                document.object_id,
                burstling.object_id,
                burstling.folder.object_id,
            )
        )

        return DOCUMENT_BURST_COMPLETED

    def burst_pdf_to(self, document, folder):

        rfile = self.context.run_command('document::get-handle',
                                         document=document, )
        if not rfile:
            self.context.log.error(
                'Handle for OGo#{0} [Document] cannot be marshalled'.
                format(document.object_id, )
            )
            return DOCUMENT_BURST_FAILED

        signal.signal(signal.SIGALRM, timeout_alarm_handler)
        try:
            pages = []

            reader = PdfFileReader(rfile, strict=False, )
            of_pages = reader.getNumPages()
            for page in range(0, reader.getNumPages()):
                #
                try:
                    signal.alarm(CONVERSION_TIMEOUT_SECONDS)
                    sfile = BLOBManager.ScratchFile()
                    writer = PdfFileWriter()
                    writer.addPage(reader.getPage(page))
                    writer.write(sfile)
                    writer = None
                    signal.alarm(0)
                    sfile.seek(0)
                    pages.append(sfile)
                except TimeOutAlarm:
                    raise BurstingTimeOutException
                finally:
                    signal.alarm(0)

            reader = None

            counter = 1
            for rfile in pages:
                filename = GenerateUniqueFileName(
                    document=document,
                    counter=counter,
                )
                burstling = self.context.r_c('document::new',
                                             folder=folder,
                                             name=filename,
                                             handle=rfile,
                                             values={}, )
                self.post_processing(document=document,
                                     burstling=burstling,
                                     counter=counter,
                                     of_pages=of_pages, )
                self.log.info(
                    'Page {0} burstling of OGo#{1} is OGo#{2} in OGo#{3}'.
                    format(counter,
                           document.object_id,
                           burstling.object_id,
                           burstling.folder.object_id))
                # Close the origin file
                BLOBManager.Close(rfile)
                # Indicate the page counter
                self.last_page_count = counter
                counter += 1

            pages = None

        except Exception as exc:
            if isinstance(exc, BurstingTimeOutException):
                self.log.error(
                    'A time-out occured during PDF burst of OGo#{0}'.
                    format(document.object_id, ))
            else:
                self.log.error(
                    'Unexpected exception occurred in PDF bursting'
                    ' of OGo#{0} [Document]'.
                    format(document.object_id, ))
            self.log.exception(exc)
            self.last_exception = \
                '{0}\n{1}'.format(exc,
                                  traceback.format_exc())
            return DOCUMENT_BURST_FAILED
        else:
            self.context.audit_at_commit(
                object_id=document.object_id,
                action='10_commented',
                message='Document bursted to {0} pages into OGo#{1}'.
                        format(self.last_page_count, folder.object_id, ))
            return DOCUMENT_BURST_COMPLETED
        finally:
            pass

    def post_processing(self, document, burstling, counter, of_pages):

        burstling.owner_id = document.owner_id

        # Copy properties from the origin document to the burstling
        for prop in self.context.pm.get_properties(document):
            self.context.property_manager.set_property(
                entity=burstling,
                namespace=prop.namespace,
                attribute=prop.name,
                value=prop.get_value(), )

        self.context.pm.set_property(
            entity=burstling,
            namespace=NAMESPACE_MANAGEMENT,
            attribute=ATTR_MANAGEMENT_SOURCE_DOCUMENT_ID,
            value=document.object_id,
        )

        if counter:
            self.context.pm.set_property(
                entity=burstling,
                namespace=NAMESPACE_MANAGEMENT,
                attribute=ATTR_MANAGEMENT_SOURCE_DOCUMENT_PAGE,
                value=counter, )

        if of_pages:
            self.context.pm.set_property(
                entity=burstling,
                namespace=NAMESPACE_MANAGEMENT,
                attribute=ATTR_MANAGEMENT_SOURCE_DOCUMENT_PAGE_COUNT,
                value=of_pages, )

        self.context.pm.set_property(
            entity=burstling,
            namespace=NAMESPACE_MANAGEMENT,
            attribute=ATTR_MANAGEMENT_BURSTED_FLAG,
            value='TARGET', )

        # Create link indicating source document
        self.context.link_manager.link(
            burstling,
            document,
            kind='coils:burstedFrom',
            label='Document Burst')

        self.context.link_manager.copy_links(document, burstling)

        if counter:
            self.context.audit_at_commit(
                object_id=burstling.object_id,
                action='10_commented',
                message='Created by page bursting of document OGo#{0} from '
                        'folder OGo#{1}. This document represents page {2} '
                        'of the source document'.
                        format(document.object_id,
                               document.folder.object_id,
                               counter, ))
        else:
            self.context.audit_at_commit(
                object_id=burstling.object_id,
                action='10_commented',
                message='Created by page bursting of document OGo#{0} from '
                        'folder OGo#{1}'.
                        format(document.object_id,
                               document.folder.object_id, ))

        return

    def run(self, document_id, version, action, actor_id, project_id, ):
        # Document Available?
        document = self.get_document(document_id)
        if not document:
            return False

        prop = self.context.pm.get_property(document,
                                            NAMESPACE_MANAGEMENT,
                                            ATTR_MANAGEMENT_BURSTED_FLAG)
        if prop:
            self.log.debug(
                'OGo#{0} [Document] has already been bursted @ {1}'.
                format(document_id, prop.get_value(), )
            )
            self.worker.enqueue_event(
                self.failure_code,
                (document_id,
                 'OGo#{0} has already been bursted or is a burstling'.
                 format(document_id, ), ),
            )
            # Document has already been bursted
            return False

        target_path = self.get_inherited_property(document)
        if not target_path:
            return False

        target_folder, \
            copy_enabled, \
            copy_on_failure, \
            error_folder_id, \
            notify_address, = self.resolve_path(target_path)

        if not target_folder:
            self.log.debug(
                'Target URI "{0}" for bursting of OGo#{1} [Document]'
                'cannot be marshalled'.
                format(target_path, document.object_id))
            self.worker.enqueue_event(
                self.failure_code,
                (document_id,
                 'Target folder {0} does not exist'.format(target_folder, )), )
            # Cannot marshall target
            return False

        self.log.debug(
            'OGo#{0} [Document] will be bursted to OGo#{1}; '
            'copyAllEnabled={2} copyOnFailure={3} errorFolderId={4} '
            'notificationAddress="{5}"'.
            format(
                document.object_id,
                target_folder.object_id,
                copy_enabled,
                copy_on_failure,
                error_folder_id,
                notify_address,
            )
        )

        result = self.burst_to(
            document=document,
            folder=target_folder,
            all_copy_enabled=copy_enabled,
        )

        if result == DOCUMENT_BURST_FAILED:

            self.context.rollback()

            self.log.debug(
                'Bursting of OGo#{0} failed, transaction rolled back'.
                format(document.object_id, )
            )

            self.context.pm.set_property(document,
                                         NAMESPACE_MANAGEMENT,
                                         ATTR_MANAGEMENT_BURSTED_FLAG,
                                         'FAIL', )

            self.context.pm.set_property(document,
                                         NAMESPACE_MANAGEMENT,
                                         'damaged',
                                         'YES', )

            self.send_initial_bursting_failed_notice(
                document=document,
                target=target_folder,
                exception=self.last_exception,
            )

            self.context.audit_at_commit(
                object_id=document.object_id,
                action='10_commented',
                message='Attempt to burst document failed.'
            )

            self.context.commit()

            self.log.debug(
                'Document OGo#{0} marked as damaged; admin notice sent'.
                format(document.object_id, )
            )

            if notify_address:
                self.send_bursting_failure_notification(
                    document=document,
                    folder=target_folder,
                    exception=self.last_exception,
                    copy_on_failure=copy_on_failure,
                    to_address=notify_address,
                    copy_enabled=copy_enabled,
                    error_folder_id=error_folder_id,
                )

            if copy_on_failure:
                if error_folder_id:
                    target_folder = self.context.run_command(
                        'folder::get',
                        id=error_folder_id,
                    )
                if not target_folder:
                    self.send_fallback_burst_no_error_folder_notice(
                        document=document,
                        target=target_folder,
                    )
                else:
                    result = self.copy_to(document, target_folder)
                    if result == DOCUMENT_BURST_COMPLETED:
                        self.context.audit_at_commit(
                            object_id=document.object_id,
                            action='10_commented',
                            message='Initial bursting failed, fallback copy '
                                    'saved to OGo#{0}'.
                                    format(target_folder.object_id, ))
                        self.context.commit()
                    else:
                        self.send_fallback_burst_failed_notice(
                            document=document,
                            target=target_folder,
                            exception=self.last_exception,
                        )
                        self.context.rollback()

                        self.context.audit_at_commit(
                            object_id=document.object_id,
                            action='10_commented',
                            message='Attempt to save fallback copy from '
                                    'bursting of document failed.')
                        self.context.commit()

            self.worker.enqueue_event(
                DOCUMENT_BURST_FAILED,
                (document_id,
                 'Bursting of OGo#{0} [Document] failed'.
                 format(document.object_id, ), ), )

        elif result == DOCUMENT_BURST_COMPLETED:
            self.context.pm.set_property(document,
                                         NAMESPACE_MANAGEMENT,
                                         ATTR_MANAGEMENT_BURSTED_FLAG,
                                         'OK')
            self.context.commit()
            self.log.debug('commited bursting')
            self.worker.enqueue_event(
                DOCUMENT_BURST_COMPLETED, (document_id, ),
            )
        elif result == DOCUMENT_BURST_DISCARDED:
            self.context.rollback()
            self.log.debug('bursting operation was discarded, rolled back.')
            self.worker.enqueue_event(
                DOCUMENT_BURST_DISCARDED, (document_id, ),
            )

    def send_fallback_burst_failed_notice(
        self,
        document,
        target,
        exception,
    ):
        self.worker.send_administrative_notice(
            subject='Copy-To fallback from document burst failed.',
            message='Copy-To fallback save from bursting of Go#{0} [Document] '
                    '"{1}" failed to OGo#{2} [Folder] "{3}" failed.'
                    '\n-\n{4}\n'.
                    format(document.object_id,
                           document.get_file_name(),
                           target.object_id,
                           target.name,
                           exception, ),
            urgency=7,
            category='document', )

    def send_fallback_burst_no_error_folder_notice(
        self,
        document,
        target,
    ):
        self.log.error(
            'Unable to marshall folder for collecting burst failure')
        self.worker.send_administrative_notice(
            subject='Bursting of document failed.'.
                    format(document.object_id, ),
            message='Bursting of OGo#{0} [Document] "{1}" to OGo#{2} '
                    '[Folder] "{2}" failed.'.
                    format(document.object_id,
                           document.get_file_name(),
                           target.object_id,
                           target.name, ),
            urgency=7,
            category='document', )

    def send_initial_bursting_failed_notice(
        self,
        document,
        target,
        exception,
    ):
        self.log.error(
            'Page bursting of OGo#{0} failed'.format(document.object_id, )
        )
        self.worker.send_administrative_notice(
            subject='Bursting of document failed.'.
                    format(document.object_id, ),
            message='Bursting of OGo#{0} [Document] "{1}" to OGo#{2} [Folder] '
                    '"{3}" failed.\n-\n{4}'.
                    format(document.object_id,
                           document.get_file_name(),
                           target.object_id,
                           target.name,
                           exception, ),
            urgency=7,
            category='document',
        )

    def send_autofile_fail_notice(
        self,
        document,
        target,
    ):
        self.log.error(
            'Unable to marshall folder for collecting burst failure')
        self.worker.send_administrative_notice(
            subject='Bursting of document failed.'.
                    format(document.object_id, ),
            message='Bursting of OGo#{0} [Document] "{1}" to OGo#{2} '
                    '[Folder] "{2}" failed.'.
                    format(document.object_id,
                           document.get_file_name(),
                           target.object_id,
                           target.name, ),
            urgency=7,
            category='document', )

    def send_bursting_failure_notification(
        self,
        document,
        folder,
        exception,
        copy_on_failure,
        to_address,
        copy_enabled,
        error_folder_id
    ):
        try:
            mimetype = self.context.type_manager.get_mimetype(document)
            subject = (
                'Failed to burst OGo#{0} Created In '
                'burst enabled Folder OGo#{1}'.
                format(
                    document.object_id,
                    document.folder.object_id,
                )
            )
            send_email_using_project7000_template(
                context=self.context,
                subject=subject,
                to_address=to_address,
                template_path=BURSTFAIL_DOCUMENT_TEMPLATE,
                regarding_id=document.object_id,
                parameters={
                    'document': document,
                    'folder': folder,
                    'mimetype': mimetype,
                    'copy_on_failure': copy_on_failure,
                    'traceback': exception,
                    'copy_on_failure': copy_on_failure,
                    'to_address': to_address,
                    'copy_enabled': copy_enabled,
                    'error_folder': error_folder_id,
                },
            )
        except Exception as exc:
            self.log.error(
                'An exception occurred generating unburstable '
                'notice.')
            self.log.exception(exc)
            self.worker.send_administrative_notice(
                subject='Burster Unable To Generate '
                        'Unburstable Alert For OGo#{0}'.
                        format(document.object_id, ),
                message=traceback.format_exc(),
                urgency=5,
                category='data',
            )
            self.context.audit_at_commit(
                object_id=document.object_id,
                action='10_commented',
                message='Failed to sent bursting failure notice to "{0}"'.
                        format(to_address, )
            )
        else:
            self.context.audit_at_commit(
                object_id=document.object_id,
                action='10_commented',
                message='Bursting failure notice sent to "{0}"'.
                        format(to_address, ))
