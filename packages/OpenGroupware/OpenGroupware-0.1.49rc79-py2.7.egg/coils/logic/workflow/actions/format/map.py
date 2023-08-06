#
# Copyright (c) 2010, 2014
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
from lxml import etree
from coils.core.logic import ActionCommand


class MapAction(ActionCommand):
    '''
    This action is a very stupid skeleton for recreating BIE's *awesome*
    translation maps.  OIE has implemented XSLT transforms with extension
    points; perhaps this supersedes MAP and MAP will never be implemented.
    MAP was really a way to allow more novice point-n-click creation of
    data-to-data transformations.  But without a UI developer working on a
    MAP interface we remain having just XSLT transforms.
    '''
    __domain__ = "action"
    __operation__ = "map"
    __aliases__ = ['mapAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    def _map(self, tag_dict):
        '''
        This is a terrible proprietary hack where some custom solutions
        where shoved in here back in 2010.  This activity should be a custom
        site action and removed rom here.  On the other hand, nobody and
        nothing uses mapAction as MAP has not been implemented.
        '''
        if (tag_dict['system_source'].text == 'MS'):
            tag_dict['oem_code'].text = 'XYZ'
            tag_dict['sale_amount'].text = \
                unicode(
                    float(tag_dict['sale_amount'].text) *
                    float(tag_dict['quantity'].text)
                )
        tag_dict['source'].text = 'PS{0}'.format(tag_dict['source'].text)

    def do_action(self):
        '''
        Read in the Standard XML message and perform the row mapping. Note
        that MAP has not been implemented, so this is really useless.

        TODO: Use the StandardXML class to read StandardXML, do not use a
        cut-n-pasted iterparse.  Code duplication.
        '''
        self._state = {}
        self.rfile.seek(0)
        table_name = None
        format_name = None
        format_class = None
        for event, element in etree.iterparse(self.rfile, events=("start",)):
            if event == 'start' and element.tag == 'ResultSet':
                table_name = element.attrib.get('tableName')
                format_name = element.attrib.get('formatName')
                format_class = element.attrib.get('className')
                element.clear()
                break
        self.wfile.write(u'<?xml version="1.0" encoding="UTF-8"?>')
        self.wfile.write(
            u'<ResultSet formatName="{0}" className="{1}" tableName="{2}">'.
            format(format_name, format_class, table_name, )
        )
        self.rfile.seek(0)
        tag_dict = {}
        for event, element in etree.iterparse(self.rfile, events=("end",)):
            if (event == 'end') and (element.tag == 'row'):
                self._map(tag_dict)
                self.wfile.write(etree.tostring(element))
                tag_dict = {}
            elif (event == 'end'):
                tag_dict[element.tag] = element
        self.wfile.write(u'</ResultSet>')

    def parse_action_parameters(self):
        pass

    def do_epilogue(self):
        pass
