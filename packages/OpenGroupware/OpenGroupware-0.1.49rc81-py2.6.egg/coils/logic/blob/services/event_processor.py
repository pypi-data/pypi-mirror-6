
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
from coils.core import BLOBManager, CoilsException, CoilsUnreachableCode
from coils.core import parse_ogo_uri
from utility import expand_labels_in_name, get_inherited_property


class DocumentEventProcessor(object):
    _event_name = None  # Override in processing class
    _discard_code = None  # Override in processing class
    _failure_code = None  # Override in processing class
    _completed_code = None  # Override in processing class
    _prop_namespace = None  # Override in processing class
    _prop_attribute = None  # Override in processing class
    context = None
    propmap = None
    worker = None

    def __init__(self, worker, propmap):
        self.worker = worker
        self.context = worker.context
        self.propmap = propmap

    @property
    def event_name(self):
        if self._event_name is None:
            raise CoilsUnreachableCode(
                'Event name not speicifed in document event processor'
            )
        return self._event_name

    @property
    def discard_code(self):
        if self._discard_code is None:
            raise CoilsUnreachableCode(
                'Discard code not specified in document event processor'
            )
        return self._discard_code

    @property
    def failure_code(self):
        if self._failure_code is None:
            raise CoilsUnreachableCode(
                'Failure code not specified in document event processor'
            )
        return self._failure_code

    @property
    def completed_code(self):
        if self._completed_code is None:
            raise CoilsUnreachableCode(
                'Completion code not specified in document event processor'
            )
        return self._completed_code

    @property
    def property_namespace(self):
        if self._prop_namespace is None:
            raise CoilsUnreachableCode(
                'Property namespace not specified in document event processor'
            )
        return self._prop_namespace

    @property
    def property_attribute(self):
        if self._prop_attribute is None:
            raise CoilsUnreachableCode(
                'Property attribute not specified in document event processor'
            )
        return self._prop_attribute

    def get_document(self, object_id, ):
        '''
        Attemptst to retrieve the specified document, returns None if the
        document is not available after putting an event on the service's
        queue to inform the service the processing was discarded.
        '''
        document = self.context.type_manager.get_entity(object_id)
        if document:
            return document

         # Document NOT available
        self.worker.log.warn(
            'OGo#{0} [Document] not available for {1}.'.
            format(object_id, self.event_name, )
        )
        self.worker.enqueue_event(
            self.discard_code,  # DISCARD
            (object_id,
             'OGo#{0} [Document] not available for {1}'.
             format(object_id, self.event_name, )
             )
        )
        # Document NOT available
        return None

    def get_inherited_property(self, document, ):
        '''
        Retreive the specified property for the document, return None if the
        property does not exist or is empty.  Prior to returning notify the
        service via the event bus that the request was discarded.
        '''
        value = get_inherited_property(
            self.context,
            document,
            self.property_namespace,
            self.property_attribute,
        )
        if not value:
            # No special processing configured
            self.worker.enqueue_event(
                self.discard_code,
                (document.object_id,
                 'No {0} target specified for OGo#{1}'.
                 format(self.event_name, document.object_id, ),
                 ),
            ),
            return None
        return value

    def parse_target_string(self, document, string_value):
        '''
        Parse the target string as an OGo URI.  In this case returning a
        None and an emptry string is not equilavent, a part of an OGo URI
        make be legitimately empty depending on the application.  If this
        method returns (None, None, None, ) then the parsing failed and the
        worker will have been notified of the discard.
        '''
        try:
            string_value = expand_labels_in_name(
                string_value,
                context=self.context,
                document=document,
                propmap=self.propmap,
            )
            netloc, path, parameters, = parse_ogo_uri(string_value)
        except Exception as exc:
            self.worker.log.error(
                'Unable to parse OGo URI "{0}" on OGo#{1} for {2}'.
                format(string_value, document.object_id, self.event_name, )
            )
            self.worker.log.exception(exc)
            self.worker.enqueue_event(
                self._discard_code,
                (document.object_id,
                 'Unable to parse {0} target URI for OGo#{1}'.
                 format(self.event_name, document.object_id, ),
                 ),
            )
            return None, None, None,
        else:
            return netloc, path, parameters,

    def get_document_handle(self, document, version, ):
        '''
        Return a file handle to the specified version of the document,
        otherwise return None.
        '''
        rfile = self.context.run_command(
            'document::get-handle',
            document=document,
            version=version,
        )
        if not rfile:
            return None, None,
        return rfile, self.context.type_manager.get_mimetype(document),

    def run(self, document_id, version, action, actor_id, project_id, ):
        raise CoilsUnreachableCode(
            'run method for document event processor was not overloaded'
        )

    def close(self):
        self.worker = None
        self.context = None
