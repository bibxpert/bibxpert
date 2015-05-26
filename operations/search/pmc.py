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
from tools import utils

log = logging.getLogger(__name__)

SLEEP_TIME=2

def process(entries):
    """
    Look for PubMed Central database to update the bibliography entries.
    :param entries: list of bibtex entries
    :return:
    """
    log.info("Seeking for PubMed Central entries")
    count = 0

    for e in entries:
        # only process articles
        if not e.entry_type == entry.EntryType.ARTICLE:
            continue

        if e.online_processed:
            log.debug("Entry '%s' already processed." % e.cite_key)
            continue

        title = utils.clean_field(e.title)
        title = title.replace("-", " ")
        title = title.replace(" ", "+")

        sd_params = {'db': 'pmc', 'retmode': 'json', 'term': '"%s"' % title,}
        sd_url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

        sd_response = requests.get(sd_url, params=sd_params)
        sd_res = sd_response.json()

        # ID list
        id_list = sd_res['esearchresult']['idlist']
        if len(id_list) == 0:
            # no result found
            log.debug("No result found for entry '%s' on PubMed Central." % e.title)
            time.sleep(SLEEP_TIME)
            continue

        for entry_id in id_list:
            sd_params = {'db': 'pmc', 'retmode': 'json', 'id': '%s' % entry_id}
            sd_url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

            sd_response = requests.get(sd_url, params=sd_params)
            sd_res = sd_response.json()

            if 'result' not in sd_res:
                # error when connecting to the summary service
                log.debug("Unable to connect to the summary service for entry '%s' on PubMed Central." % e.title)
                continue

            result = sd_res['result'][entry_id]
            title = result['title']

            if utils.is_similar(title, e.title):
                journal = result['fulljournalname']

                volume = None
                if 'volume' in result:
                    volume = result['volume']
                number = None
                if 'issue' in result:
                    number = result['issue']
                pages = None
                if 'pages' in result:
                    pages = result['pages']
                doi = None
                if 'articleids' in result:
                    for ids in result['articleids']:
                        if ids['idtype'] == "doi":
                            doi = ids['value']
                year = None
                if len(result['epubdate']) > 0:
                    year = _get_year(result['epubdate'])
                if not year and len(result['pubdate']) > 0:
                    year = _get_year(result['pubdate'])

                # authors
                authors_list = None
                if 'authors' in result:
                    authors_list = ""
                    for author in result['authors']:
                        if len(authors_list) > 0:
                            authors_list += " and "
                        authors_list += utils.encode(author['name'])

                e.merge(entry.Entry(
                    title=title,
                    authors=authors_list,
                    journal=journal,
                    volume=volume,
                    number=number,
                    year=year,
                    doi=doi,
                    pages=pages
                ))

                e.online_processed = True
                log.debug("[PubMed Central] Updated entry '%s'." % e.title)
                count += 1
                break
            time.sleep(SLEEP_TIME)

    if count > 0:
        log.info("Updated %s entries according to PubMed Central." % count)

    return entries


def _get_year(obj):
    """
    Get the year of the entry.
    :param obj: year string object
    :return: entry year or none if not valid value
    """
    year = obj[0:4]
    try:
        year = int(year)
    except ValueError:
        year = None
    return year