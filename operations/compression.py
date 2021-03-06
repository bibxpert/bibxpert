#!/usr/bin/env python
#
# Copyright 2015-2016 Rafael Ferreira da Silva
# http://www.rafaelsilva.com/tools
#
# Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
__author__ = "Rafael Ferreira da Silva"

from datetime import date
from entries.entry import *
from tools.utils import *

log = logging.getLogger(__name__)


def compression(entries):
    """
    Compress bibliography entries and print minimum requirements.
    :param entries: list of entries
    :return: list of compressed entries
    """
    log.info("Compressing entries")
    count = 0

    for entry in entries:
        if not entry.entry_type == EntryType.MISC:
            _compress_authors(entry.authors)
            if entry.booktitle:
                entry.booktitle = _compress_book_title(entry.booktitle)
            if entry.journal:
                entry.journal = _compress_journal_title(entry.journal)
            entry.compressed = True
            count += 1

    if count > 0:
        log.info("Compressed %s entries." % count)

    return entries


def _compress_authors(authors_obj):
    """
    Compress authors by abbreviating first name.
    :param authors: list of authors
    :return: list of compressed authors
    """
    for author in authors_obj.authors:
        if author.first_name and not author.first_name == "others" and len(author.first_name) > 2:
            first_name = ""
            for given_name in author.first_name.split(" "):
                if len(first_name) > 0:
                    first_name += " "
                first_name += given_name[0:1] + "."
            author.first_name = first_name


def _compress_book_title(title):
    """
    Compress book titles by abbreviating words and removing conference acronyms.
    :param title: title of the book
    :return: compressed title
    """

    # remove proceedings from the beginning of the title
    if 'proceedings of the' in title.lower():
        title = re.sub(r'proceedings of the', '', title, flags=re.IGNORECASE).strip()
    elif 'proceedings of' in title.lower():
        title = re.sub(r'proceedings of', '', title, flags=re.IGNORECASE).strip()
    elif 'proceedings' in title.lower():
        title = re.sub(r'proceedings', '', title, flags=re.IGNORECASE).strip()
    elif 'proc. of the' in title.lower():
        title = re.sub(r'proc. of the', '', title, flags=re.IGNORECASE).strip()
    elif 'proc. of' in title.lower():
        title = re.sub(r'proc. of', '', title, flags=re.IGNORECASE).strip()

    # remove year from the beginning of the title
    s_year = title[0:4]
    try:
        year = int(s_year)
        if 1900 < year <= date.today().year + 1:
            title = title[4:]
    except ValueError:
        pass

    # remove in from beginning of the title
    if title.lower().startswith('in '):
        title = title[2:].strip()

    # replace write out numbers
    title = _compress_ordinal_numbers(title)

    # remove other characters
    if title.startswith('.'):
        title = title[1:].strip()

    # abbreviate of common terms
    title = replace_text(title, 'international', 'Internat.')
    title = replace_text(title, 'conference', 'Conf.')
    title = replace_text(title, 'symposium', 'Symp.')
    title = replace_text(title, 'management', 'Managem.')

    return title


def _compress_journal_title(title):
    """
    Compress journal titles with their abbreviations
    :param title:
    :return:
    """
    # abbreviate of common terms
    title = replace_text(title, 'transactions', 'Trans.')
    title = replace_text(title, 'communications', 'Commun.')
    title = replace_text(title, 'lecture', 'Lect.')
    title = replace_text(title, 'academic', 'Acad.')
    title = replace_text(title, 'conference', 'Conf.')
    title = replace_text(title, 'series', 'Ser.')
    title = replace_text(title, 'journal', 'J.')
    title = replace_text(title, 'magazine', 'Mag.')
    title = replace_text(title, 'bulletin', 'B.')
    title = replace_text(title, 'review', 'Rev.')
    title = replace_text(title, 'proceedings', 'Proc.')
    title = replace_text(title, 'advances', 'Adv.')
    title = replace_text(title, 'annales', 'Ann.')
    title = replace_text(title, 'annals', 'Ann.')
    title = replace_text(title, 'applied', 'Appl.')

    return title


def _compress_ordinal_numbers(title):
    """
    Replace write out numbers by numerical representation.
    :param title: title of the book or journal
    :return: compressed ordinal numbers
    """
    os = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'eleventh',
         'twelfth', 'thirteenth', 'fourteenth', 'fifteenth', 'sixteenth', 'seventeenth', 'eighteenth', 'nineteenth',
         'twentieth', 'thirtieth', 'fortieth', 'fiftieth', 'sixtieth', 'seventieth', 'eightieth', 'ninetieth']
    suffixes = ['st', 'nd', 'rd']
    decimals = ['twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']

    for d in range(0, len(decimals)):
        for n in range(0, 9):
            if n < 3:
                title = re.sub(r'%s-%s' % (decimals[d], os[n]), '%s%s%s' % (d + 2, n + 1, suffixes[n]), title,
                               flags=re.IGNORECASE)
            else:
                title = re.sub(r'%s-%s' % (decimals[d], os[n]), '%s%sth' % (d + 2, n + 1), title,
                               flags=re.IGNORECASE)
    for n in range(0, 3):
        title = re.sub(r'%s' % os[n], '%s%s' % (n + 1, suffixes[n]), title, flags=re.IGNORECASE)
    for n in range(3, len(os)):
        title = re.sub(r'%s' % os[n], '%sth' % (n + 1), title, flags=re.IGNORECASE)

    return title.strip()