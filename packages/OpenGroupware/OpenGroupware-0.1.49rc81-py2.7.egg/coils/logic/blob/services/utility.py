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
# THE SOFTWARE
#
import re
from datetime import datetime, timedelta

NAMESPACE_AUTOPRINT = 'http://www.opengroupware.us/autoprint'
NAMESPACE_MANAGEMENT = '57c7fc84-3cea-417d-af54-b659eb87a046'

ATTR_MANAGEMENT_COLLECTED = 'autoCollected'
ATTR_MANAGEMENT_COLLECTION_DESC = 'autoCollectionDescriptor'
ATTR_MANAGEMENT_AUTOFILE_TARGET = 'autoFileTarget'
ATTR_MANAGEMENT_BURST_TARGET = 'burstingTarget'
ATTR_MANAGEMENT_BURSTED_FLAG = 'bursted'
ATTR_MANAGEMENT_SOURCE_DOCUMENT_ID = 'sourceDocumentId'
ATTR_MANAGEMENT_SOURCE_DOCUMENT_PAGE = 'sourceDocumentPage'
ATTR_MANAGEMENT_SOURCE_DOCUMENT_PAGE_COUNT = 'sourceDocumentPageCount'
ATTR_MANAGEMENT_SOURCE_DOCUMENT_VERSION = 'sourceDocumentVersion'
ATTR_MANAGEMENT_UNCOLLECTION_DESC = 'autoUncollectionDescriptor'
ATTR_MANAGEMENT_SPECIAL_PROCESSING = 'specialProcessing'
ATTR_MANAGEMENT_SPECIAL_SOURCE_ID = 'sourceDocumentId'
ATTR_MANAGEMENT_SPECIAL_FOLDER_ID = 'sourceFolderId'
ATTR_MANAGEMENT_SPECIAL_SOURCE_FILENAME = 'sourceDocumentFilename'
ATTR_MANAGEMENT_SPECIAL_SOURCE_CHECKSUM = 'sourceDocumentChecksum'

#
# SOME CODE HERE IS ***DUPLICATED*** FROM coils/net/smtp_common.py
# It should almost certainly go into some common module
#


def week_ranges_of_month(year, month):
    weeks = []
    tmp = datetime(year, month, 1)
    week = []
    while tmp.month == month:
        week.append(tmp.day)
        if tmp.weekday() == 6:
            weeks.append(week)
            week = []
        tmp += timedelta(days=1)
    if week:
        weeks.append(week)
    return weeks


def week_offset_of_date(dt):
    week_ranges = week_ranges_of_month(dt.year, dt.month)
    counter = 0
    for week in week_ranges:
        if dt.day in week:
            break
        counter += 1
    return (counter + 1,
            week_ranges[counter][0],
            week_ranges[counter][-1], )


def week_range_name_of_date(dt):
    week_number, start_day, end_day = week_offset_of_date(dt)
    return '{0:02d}-{1:02d}'.format(start_day, end_day)


def get_inherited_property(context, folder, namespace, attribute):

    prop = context.property_manager.get_property(folder,
                                                 namespace,
                                                 attribute)

    if not prop:
        tmp = folder.folder
        while tmp:
            prop = context.property_manager.get_property(tmp,
                                                         namespace,
                                                         attribute)
            if prop:
                break
            tmp = tmp.folder

    if not prop:
        return None

    return prop.get_string_value()


def expand_labels_in_name(
    text,
    context=None,
    document=None,
    propmap=None,
):

    if not text:
        return None

    today = datetime.today()

    def get_builtin_value(label):
        if label == '$__YEAR__;':
            return today.strftime('%Y')
        elif label == '$__MONTH__;':
            return today.strftime('%m')
        elif label == '$__DAYOFMONTH__;':
            return today.strftime('%d')
        elif label == '$__WEEKOFMONTH__;':
            return week_range_name_of_date(today)
        elif label == '$__LOGIN__;' and context:
            return context.login.replace('\\', '-')

    labels = set(re.findall('\$__[A-z0-9]*__;', text))
    for label in labels:
        text = text.replace(label, get_builtin_value(label))
    if document and propmap and context:
        labels = set(re.findall('\$[A-z0-9]*;', text))
        for label in labels:
            if len(label) < 3:
                continue
            propmapkey = label[1:-1]
            if propmapkey in propmap:
                prop = context.property_manager.\
                    get_property(
                        entity=document,
                        namespace=propmap[propmapkey]['namespace'],
                        name=propmap[propmapkey]['attribute'],
                    )
                if prop:
                    text = text.replace(label, prop.get_string_value())
                else:
                    text = text.replace(label, '__undefined__')
    return text
