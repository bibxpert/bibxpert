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
import time
import urllib

from entries import entry
from tools import utils
from xml.etree import ElementTree

log = logging.getLogger(__name__)


def process(entries):
    """
    Look for IEEE Xplore database to update the bibliography entries.
    :param entries: list of bibtex entries
    :return:
    """
    log.info("Seeking for IEEE Xplore entries")
    count = 0

    for e in entries:
        if e.online_processed:
            log.debug("Entry '%s' already processed." % e.cite_key)
            continue

        title = utils.clean_field(e.title)
        url = "http://ieeexplore.ieee.org/gateway/ipsSearch.jsp?ti=\"%s\"&hc=1" % title

        data = urllib.urlopen(url).read()
        root = ElementTree.fromstring(data)

        if "Error" in root.tag:
            # no result found
            log.debug("No result found for entry '%s' on IEEE Xplore." % e.title)
            continue

        document = root.findall('document')[0]
        title = document.findall('title')[0].text
        authors_list = document.findall('authors')[0].text.replace("; ", " and ")
        pubtitle = document.findall('pubtitle')[0].text
        pubtype = _get_field("pubtype", document)
        publisher = document.findall('publisher')[0].text
        volume = _get_field("volume", document)
        number = _get_field("issue", document)
        year = _get_field("py", document)
        doi = _get_field("doi", document)
        start_page = _get_field("spage", document)
        end_page = _get_field("epage", document)

        pages = None
        if start_page and end_page:
            pages = start_page + "--" + end_page

        booktitle = None
        journal = None
        entry_type = entry.EntryType.MISC

        if pubtype == "Journals & Magazines":
            entry_type = entry.EntryType.ARTICLE
            journal = pubtitle
        elif pubtype == "Conference Publications":
            entry_type = entry.EntryType.INPROCEEDINGS
            booktitle = pubtitle

        e.merge(entry.Entry(
            entry_type=entry_type,
            title=title,
            authors=authors_list,
            journal=journal,
            booktitle=booktitle,
            volume=volume,
            number=number,
            year=year,
            doi=doi,
            pages=pages,
            publisher=publisher
        ))
        e.online_processed = True
        count += 1

        time.sleep(1)

    if count > 0:
        log.info("Updated %s entries according to IEEE Xplore." % count)

    return entries


def _get_field(field_name, element):
    """
    Look for the value of a given field name from a XML element.
    :param field_name: name of the field
    :param element: XML element
    :return: field value if exists, or None otherwise
    """
    for child in element:
        if field_name in child.tag:
            return element.findall(field_name)[0].text
    return None