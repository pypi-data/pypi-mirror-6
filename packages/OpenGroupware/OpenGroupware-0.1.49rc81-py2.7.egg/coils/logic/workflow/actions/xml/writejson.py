#
# Copyright (c) 2010, 2013
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
import base64
import json
import StringIO
from lxml import etree
from datetime import datetime, date
from xml.sax.saxutils import escape, unescape
from coils.core import StandardXML
from coils.core.logic import ActionCommand


'''
TODO: This should write the JSON as a stream if possible, can
the ijson module do that, or is it just for reading?
TODO: Allow the action to specify options for ensure_ascii, indent,
and allow_nan
'''


class WriteJSONAction(ActionCommand):
    '''
    WriteJSONActon accepts a StandardXML stream and renders it as JSON
    '''
    __domain__ = "action"
    __operation__ = "write-json"
    __aliases__ = ['writeJSON', 'writeJSONAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'application/json'

    def parse_action_parameters(self):
        pass

    def _encode(self, o):
        if (isinstance(o, datetime)):
            return o.strftime('%Y-%m-%dT%H:%M:%S')
        elif (isinstance(o, date)):
            return o.strftime('%Y-%m-%dT00:00:00')
        raise TypeError(
            'JSON cannot serialize value of type "{0}"'.
            format(type(o), )
        )

    def do_action(self):

        table_name, format_name, format_class = \
            StandardXML.Read_ResultSet_Metadata(self.rfile)

        jsondata = {
            'tableName': table_name,
            'formatName': format_name,
            'formatClass': format_class,
            'rows': list(),
            'rowCount': 0,
        }
        row_count = 0
        for keys, fields in StandardXML.Read_Rows(self.rfile):
            row = {'keys': {}, 'fields': {}, }
            for key, value in keys.items():
                row['keys'][key] = value
            for key, value in fields.items():
                row['fields'][key] = value
            jsondata['rows'].append(row)
            row_count += 1
        jsondata['rowCount'] = row_count
        json.dump(jsondata, self.wfile, default=self._encode)
        jsondata = None

    def do_epilogue(self):
        pass
