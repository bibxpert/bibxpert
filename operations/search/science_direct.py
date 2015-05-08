#!/usr/bin/env python
#
# Copyright 2015 Rafael Ferreira da Silva
# http://www.rafaelsilva.com/tools
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
__author__ = "Rafael Ferreira da Silva"

import logging
import requests
import time
import unicodedata

from entries import entry

log = logging.getLogger(__name__)


def process(entries):
    """
    Look for Science Direct (SCOPUS) database to update the bibliography entries.
    This update evaluates only '@ARTICLE' entry types.
    :param entries: list of bibtex entries
    :return:
    """
    log.info("Seeking for Science Direct (SCOPUS) entries")
    count = 0

    for e in entries:
        if e.online_processed:
            log.debug("Entry '%s' already processed." % e.cite_key)
            continue

        if not e.entry_type == entry.EntryType.ARTICLE:
            log.debug("Skipping non-journal entry '%s'." % e.title)
            continue

        sd_params = {'query': 'TITLE("%s")' % e.title, 'view': 'STANDARD'}
        sd_url = 'http://api.elsevier.com/content/search/scidir'
        sd_headers = {'X-ELS-APIKey': '6b7571677244819622d79889d590f307', 'X-ELS-ResourceVersion': 'XOCS'}
        sd_response = requests.get(sd_url, params=sd_params, headers=sd_headers)
        sd_res = sd_response.json()

        if 'error' in sd_res['search-results']['entry'][0]:
            log.debug("No results found in Science Direct for '%s'." % e.title)
            continue

        sc_params = {'query': 'TITLE("%s")' % e.title, 'view': 'STANDARD'}
        sc_url = 'http://api.elsevier.com/content/search/scopus'
        sc_headers = {'X-ELS-APIKey': '6b7571677244819622d79889d590f307', 'X-ELS-ResourceVersion': 'XOCS'}
        sc_response = requests.get(sc_url, params=sc_params, headers=sc_headers)
        sc_res = sc_response.json()

        # SCOPUS fields
        sc_res_obj = sc_res['search-results']['entry'][0]
        entry_type = _parse_entry_type(sc_res_obj['prism:aggregationType'])
        volume = sc_res_obj['prism:volume']
        year = _parse_year(sc_res_obj['prism:coverDisplayDate'])

        # Science Direct fields
        sd_res_obj = sd_res['search-results']['entry'][0]

        # Authors
        authors = ""
        for author in sd_res_obj['authors']['author']:
            if len(authors) > 0:
                authors += " and "
            authors += author['surname'] + ", " + author['given-name']
        authors = unicodedata.normalize('NFKD', authors).encode('ascii','ignore')

        # Other fields
        title = sd_res_obj['dc:title']
        doi = sd_res_obj['prism:doi']
        journal = sd_res_obj['prism:publicationName']

        e.merge(entry.Entry(
            entry_type=entry_type,
            title=title,
            authors=authors,
            journal=journal,
            volume=volume,
            year=year,
            doi=doi
        ))
        e.online_processed = True
        count += 1

        time.sleep(1)

    if count > 0:
        log.info("Updated %s entries according to Science Direct." % count)

    return entries


def _parse_entry_type(aggregation_type):
    """

    :param aggregation_type:
    :return: entry type of entry.EntryType
    """
    if aggregation_type.lower() == "journal":
        return entry.EntryType.ARTICLE

    return None


def _parse_year(cover_display_date):
    """

    :param cover_display_date:
    :return: entry year
    """
    return cover_display_date[-4:]