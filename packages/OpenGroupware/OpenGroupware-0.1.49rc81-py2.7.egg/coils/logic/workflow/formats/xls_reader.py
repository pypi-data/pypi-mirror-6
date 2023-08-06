#
# Copyright (c) 2011, 2013, 2014
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
from locale import atof, atoi
from xlrd import xldate_as_tuple, empty_cell
from coils.core import NotImplementedException, CoilsException
from format import \
    COILS_FORMAT_DESCRIPTION_OK, \
    COILS_FORMAT_DESCRIPTION_INCOMPLETE
from xls_format import SimpleXLSFormat
from exception import RecordFormatException


class RowField(object):

    def __init__(self, field, ):
        self.static_value = field.get('static', None)  # static value!
        self.field_default = field.get('default', None)
        self.field_kind = field.get('kind', 'string')
        self.field_name = field.get('name', None)
        self.field_iskey = unicode(field.get('key', 'false')).lower()
        self.field_null = False
        self.field_lower = field.get('lower', False)
        self.field_upper = field.get('upper', False)
        self.field_divisor = field.get('divisor', 1)
        self.field_floor = field.get('floor', None)
        self.field_ceiling = field.get('ceiling', None)
        self.field_required = field.get('required', False)
        self.field_target = \
            field.get('rename', self.field_name).replace(' ', '-')
        self.field_cast = field.get('coerceVia', None)

    def reset(self):
        self.field_value = self.static_value

    def set_value(self, value):
        if value is None:
            self.field_null = True
            self.field_value = None
        else:
            self.field_null = False
            self.field_value = value

    def use_default_value(self):
        self.set_value(self.field_default)

    def process_value(self, datetype):

        def get_type_error_message(expected, got, name):
            return 'Expected {0} value but got "{1}" {2} in column "{3}".'.\
                   format(expected, got, type(got), name, )

        # Empty
        if self.field_value in [empty_cell.value, None, ]:
            self.field_null = True
        # booleanString, booleanInteger
        elif self.field_kind in ('booleanString', 'booleanInteger', ):
            if self.field_value in [0, 1]:
                if self.field_kind in ('booleanString', ):
                    self.field_value = unicode(bool(self.field_value))
                elif self.field_kind in ('booleanInteger', ):
                    self.field_value = int(self.field_value)
            else:
                raise TypeError(
                    get_type_error_message(
                        'boolean',
                        self.field_value,
                        self.field_name,
                    )
                )

        # String
        elif self.field_kind in ('string'):
            if not isinstance(self.field_value, basestring):
                self.coerce_via()
            if isinstance(self.field_value, basestring):
                if self.field_lower:
                    self.field_value = self.field_value.lower()
                if self.field_upper:
                    self.field_value = self.field_value.upper()
            else:
                raise TypeError(
                    get_type_error_message(
                        'string',
                        self.field_value,
                        self.field_name,
                    )
                )

        # Date
        elif self.field_kind in ('date', ):
            # TODO: shouldn't we pass the books datemode?
            date_value = \
                str(xldate_as_tuple(self.field_value, datetype)[0:3])
            self.field_value = \
                SimpleXLSFormat.Reformat_Date_String(
                    date_value,
                    '(%Y, %m, %d)',
                    '%Y-%m-%d')
        # Time
        elif self.field_kind in ('time', ):
            time_value = \
                xldate_as_tuple(self.field_value, datetype)[3:]
            self.field_value = '{0:02d}:{1:02d}:{2:02d}'.format(*time_value)

        # DateTime
        elif self.field_kind in ('datetime', ):
            date_value = unicode(
                xldate_as_tuple(self.field_value, datetype)
            )
            self.field_value = \
                SimpleXLSFormat.Reformat_Date_String(
                    date_value,
                    '(%Y, %m, %d, %H, %M, %S)',
                    '%Y-%m-%d %H:%M:%S',
                )

        # Integer, float, ifloat
        elif self.field_kind in ('integer', 'float', 'ifloat', ):

            '''
            if the value is a string - this often happens in
            XLS documents - remove any whitespace characters
            before attempting to process the value as a numeric
            value.
            '''
            if isinstance(self.field_value, basestring):
                self.field_value = self.field_value.strip()

            if self.field_kind == 'integer':
                # Integer
                if isinstance(self.field_value, basestring):
                    self.field_value = atoi(self.field_value)
                else:
                    self.field_value = int(self.field_value)
                if self.field_floor is not None:
                    floor = int(self.field_floor)
                if self.field_ceiling is not None:
                    ceiling = int(self.field_ceiling)
                if self.field_divisor != 1:
                    self.field_value = \
                        (self.field_value / int(self.field_divisor))
            else:
                # Float
                if isinstance(self.field_value, basestring):
                    self.field_value = atof(self.field_value)
                else:
                    self.field_value = float(self.field_value)
                if self.field_floor is not None:
                    self.field_floor = float(self.field_floor)
                if self.field_ceiling is not None:
                    self.field_ceiling = \
                        float(self.field_ceiling)
                if self.field_divisor != 1:
                    self.field_value = \
                        (self.field_value / float(self.field_divisor))

            # Floor test
            if (
                (self.field_floor is not None) and
                (self.field_value < self.field_floor)
            ):
                message = (
                    'Value {0} below floor {1}'.
                    format(
                        self.field_value,
                        self.field_floor,
                    )
                )
                raise ValueError(message)

            # Cieling Test
            if (
                (self.field_ceiling is not None) and
                (self.field_value > self.field_ceiling)
            ):
                message = (
                    'Value {0} above ceiling {1}'.
                    format(
                        self.field_value,
                        self.field_ceiling,
                    )
                )
                raise ValueError(message)

    def coerce_via(self):
        '''
        coerceVia allows a non-string value to be read
        in as a string
        '''
        if not self.field_cast:
            return
        for cast in self.field_cast:
            try:
                if cast == 'integer':
                    self.field_value = \
                        int(self.field_value)
                elif cast == 'conditionalInteger':
                    if isinstance(self.field_value, float):
                        if self.field_value.is_integer():
                            self.field_value = \
                                int(self.field_value)
                elif cast == 'float':
                    self.field_value = \
                        float(self.field_value)
                elif cast == 'string':
                    self.field_value = \
                        unicode(self.field_value)
            except Exception as exc:
                # TODO: capture the original exception for more information
                raise TypeError(
                    'Unable to coerce value "{0}" to type "{1}"'.
                    format(self.field_lower, cast, ))
        self.field_value = unicode(self.field_value)


class ColumnarXLSReaderFormat(SimpleXLSFormat):

    def __init__(self):
        SimpleXLSFormat.__init__(self)

    def set_description(self, fd):
        code = SimpleXLSFormat.set_description(self, fd)
        error = [COILS_FORMAT_DESCRIPTION_INCOMPLETE, ]
        if (code[0] == 0):
            # TODO: Verify XLS format parameters
            self.description = fd
            self._definition = self.description.get('data')
            self._field_list = []
            for field in self._definition.get('columns'):
                self._field_list.append(RowField(field))
            return (COILS_FORMAT_DESCRIPTION_OK, 'OK')
        else:
            return code

    @property
    def mimetype(self):
        return 'application/vnd.ms-excel'

    def process_record_in(self):

        #TODO: Handle cell type "xlrd.XL_CELL_ERROR".
        #TODO: Read cell formatting info?
        row = []

        for field in self._field_list:
            field.reset()

            if field.field_value:
                # This is a static value, we don't care what is in the file
                pass

            elif field.field_name in self._column_names:
                # Process a column that IS FOUND IN THE SHEET

                if field.field_value is None:
                    '''
                    This columen will be processed from the sheet as the
                    value is not static!
                    '''
                    self._colNum = self._column_names.index(field.field_name)
                    field.set_value(
                        self._sheet.cell(self._rowNum, self._colNum).value
                    )
                    try:
                        field.process_value(datetype=self._datetype)
                    except ValueError as exc:
                        raise RecordFormatException(
                            'Error in column#{0} row#{1}\n{2}'.
                            format(
                                self._colNum + 1,
                                self._rowNum + 1,
                                str(exc)
                            )
                        )
                    except TypeError as exc:
                        raise RecordFormatException(
                            'Error in column#{0} row#{1}\n{2}'.
                            format(
                                self._colNum + 1,
                                self._rowNum + 1,
                                str(exc)
                            )
                        )
            else:

                # Process a column that NOT FOUND IN THE SHEET

                if not field.field_required:
                    # Field is NOT required, we use the specified default value
                    field.use_default_value()
                else:
                    message = \
                        (' \n  Field name \"{0}\" given in description, but '
                         'not found in XLS input document; seen field names '
                         'are: {1}').\
                        format(
                            field.field_name,
                            ','.join([
                                '"{0}"'.format(x) for x in self._column_names]
                            )
                        )
                    raise RecordFormatException(message)

            row.append(field)

        # RENDER ROW
        with self.xml.container('row',
                                attrs={'id': unicode(self._rowNum), }) as xml:
            for tmp in row:
                if tmp.field_null:
                    xml.element(
                        tmp.field_target,
                        attrs={'dataType': tmp.field_kind,
                               'isNull': 'true',
                               'isPrimaryKey': tmp.field_iskey, }, )
                else:
                    xml.element(
                        tmp.field_target,
                        text=unicode(tmp.field_value),
                        attrs={'dataType': tmp.field_kind,
                               'isNull': 'false',
                               'isPrimaryKey': tmp.field_iskey, })

        return True

    def process_record_out(self, record):
        raise NotImplementedException('Cannot write XLS documents.')
