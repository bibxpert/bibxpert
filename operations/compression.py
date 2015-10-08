#!/usr/bin/env python
#
# Copyright 2015 Rafael Ferreira da Silva
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

import logging
import re

from datetime import date

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
        _compress_authors(entry.authors)
        entry.booktitle = _compress_booktitles(entry.booktitle)
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


def _compress_booktitles(booktitle):
    """
    Compress book titles by abbreviating words and removing conference acronyms.
    :param booktitle: title of the book
    :return: compressed title
    """
    if booktitle:
        # remove proceedings from the beginning of the title
        if 'proceedings of the' in booktitle.lower():
            booktitle = re.sub(r'proceedings of the', '', booktitle, flags=re.IGNORECASE).strip()
        elif 'proceedings of' in booktitle.lower():
            booktitle = re.sub(r'proceedings of', '', booktitle, flags=re.IGNORECASE).strip()
        elif 'proceedings' in booktitle.lower():
            booktitle = re.sub(r'proceedings', '', booktitle, flags=re.IGNORECASE).strip()
        elif 'proc. of the' in booktitle.lower():
            booktitle = re.sub(r'proc. of the', '', booktitle, flags=re.IGNORECASE).strip()
        elif 'proc. of' in booktitle.lower():
            booktitle = re.sub(r'proc. of', '', booktitle, flags=re.IGNORECASE).strip()

        # remove year from the beginning of the title
        s_year = booktitle[0:4]
        try:
            year = int(s_year)
            if year > 1900 and year <= date.today().year + 1:
                booktitle = booktitle[4:]
        except ValueError:
            pass

        # remove in from beginning of the title
        if booktitle.lower().startswith('in '):
            booktitle = booktitle[2:].strip()

        # replace write out numbers
        booktitle = _compress_ordinal_numbers(booktitle)

        # remove other characters
        if booktitle.startswith('.'):
            booktitle = booktitle[1:].strip()

        # abbreviate words
        if 'international' in booktitle.lower():
            booktitle = re.sub(r'international', 'Internat.', booktitle, flags=re.IGNORECASE).strip()
        if 'conference' in booktitle.lower():
            booktitle = re.sub(r'conference', 'Conf.', booktitle, flags=re.IGNORECASE).strip()
        if 'symposium' in booktitle.lower():
            booktitle = re.sub(r'symposium', 'Symp.', booktitle, flags=re.IGNORECASE).strip()
        if 'management' in booktitle.lower():
            booktitle = re.sub(r'management', 'Managem.', booktitle, flags=re.IGNORECASE).strip()

    return booktitle


def _compress_ordinal_numbers(booktitle):
    """
    Replace write out numbers by numerical representation.
    :param booktitle: title of the book
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
                booktitle = re.sub(r'%s-%s' % (decimals[d], os[n]), '%s%s%s' % (d + 2, n + 1, suffixes[n]), booktitle,
                                   flags=re.IGNORECASE)
            else:
                booktitle = re.sub(r'%s-%s' % (decimals[d], os[n]), '%s%sth' % (d + 2, n + 1), booktitle,
                                   flags=re.IGNORECASE)
    for n in range(0, 3):
        booktitle = re.sub(r'%s' % os[n], '%s%s' % (n + 1, suffixes[n]), booktitle, flags=re.IGNORECASE)
    for n in range(3, len(os)):
        booktitle = re.sub(r'%s' % os[n], '%sth' % (n + 1), booktitle, flags=re.IGNORECASE)

    return booktitle.strip()