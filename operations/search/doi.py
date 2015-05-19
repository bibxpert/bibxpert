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

from entries import entry

log = logging.getLogger(__name__)


def process(entries):
    """
    Look for DOI database to update the bibliography entries.
    :param entries: list of bibtex entries
    :return
    """
    log.info("Seeking for DOI entries")
    count = 0

    for e in entries:
        if not e.doi:
            log.debug("Skipping entry with no DOI '%s'." % e.title)
            continue

        doi_addr = e.doi
        if "dx.doi.org" in doi_addr:
            doi_addr = doi_addr.replace("http://", "")
            doi_addr = doi_addr[doi_addr.rfind("dx.doi.org") + 11:]

        sd_url = 'http://dx.doi.org/%s' % doi_addr
        sd_headers = {'Accept': 'application/rdf+xml;q=0.5, application/vnd.citationstyles.csl+json;q=1.0'}
        sd_response = requests.get(sd_url, headers=sd_headers)
        if not sd_response:
            log.warning("Could not retrieve information for DOI: %s" % doi_addr)
            continue

        sd_res = sd_response.json()

        # DOI fields
        title = sd_res['title']
        type = sd_res['type']
        container_title = sd_res['container-title']
        publisher = sd_res['publisher']

        pages = None
        if 'page' in sd_res:
            pages = sd_res['page']

        number = None
        if 'issue' in sd_res:
            number = sd_res['issue']

        volume = None
        if 'volume' in sd_res:
            volume = sd_res['volume']

        if 'issued' in sd_res:
            year = sd_res['issued']['date-parts'][0][0]

        # authors
        authors_list = None
        if 'author' in sd_res:
            authors_list = ""
            for author in sd_res['author']:
                if len(authors_list) > 0:
                    authors_list += " and "
                authors_list += author['family'] + ", " + author['given']

        # editors
        editor = None
        if 'editor' in sd_res:
            editor = ""
            for author in sd_res['editor']:
                if len(editor) > 0:
                    editor += " and "
                editor += author['family'] + ", " + author['given']

        booktitle = None
        journal = None
        entry_type = entry.EntryType.MISC

        if type == "journal-article":
            entry_type = entry.EntryType.ARTICLE
            journal = container_title
        elif type == "proceedings-article":
            entry_type = entry.EntryType.INPROCEEDINGS
            booktitle = container_title
        elif type == "book-chapter":
            entry_type = entry.EntryType.INCOLLECTION
            booktitle = container_title
        elif type == "journal-issue":
            entry_type = entry.EntryType.PROCEEDINGS
            booktitle = container_title

        e.merge(entry.Entry(
            entry_type=entry_type,
            title=title,
            authors=authors_list,
            editor=editor,
            journal=journal,
            booktitle=booktitle,
            volume=volume,
            number=number,
            year=year,
            doi=doi_addr,
            pages=pages,
            publisher=publisher
        ))
        e.online_processed = True
        log.debug("[DOI] Updated entry '%s'." % e.title)
        count += 1

        time.sleep(0.5)

    if count > 0:
        log.info("Updated %s entries according to the DOI." % count)

    return entries
