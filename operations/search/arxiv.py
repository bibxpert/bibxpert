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
    Look for arXiv database to update the bibliography entries.
    This update evaluates only '@ARTICLE' entry types.
    :param entries: list of bibtex entries
    :return:
    """
    log.info("Seeking for arXiv entries")
    count = 0

    for e in entries:
        if e.online_processed:
            log.debug("Entry '%s' already processed." % e.cite_key)
            continue

        if e.url and "arxiv" in e.url:
            # use id
            id = e.url[e.url.rfind('/') + 1:]
            url = "http://export.arxiv.org/api/query?id_list=%s" % id
        else:
            title = utils.clean_field(e.title)
            title = title.replace("-", " ")
            title = title.replace(" ", "+")
            title = urllib.quote(title)
            url = "http://export.arxiv.org/api/query?search_query=ti:%%22%s%%22&start=0&max_results=1" % title

        data = urllib.urlopen(url).read()

        root = ElementTree.fromstring(data)
        results = int(root.findall('{http://a9.com/-/spec/opensearch/1.1/}totalResults')[0].text)
        if results == 0:
            # no result found
            log.debug("No result found for entry '%s' on arXiv." % e.title)
            continue

        e_entry = root.findall('{http://www.w3.org/2005/Atom}entry')[0]

        title = e_entry.findall('{http://www.w3.org/2005/Atom}title')[0].text
        title = title.replace("\n", "")
        url = e_entry.findall('{http://www.w3.org/2005/Atom}id')[0].text
        year = e_entry.findall('{http://www.w3.org/2005/Atom}published')[0].text
        year = year[:4]

        authors_list = ""
        for author in e_entry.findall('{http://www.w3.org/2005/Atom}author'):
            if len(authors_list) > 0:
                authors_list += " and "
            authors_list += author[0].text

        e.merge(entry.Entry(
                title=title,
                authors=authors_list,
                url=url,
                year=year
            ))
        e.online_processed = True
        count += 1

        time.sleep(1)

    if count > 0:
        log.info("Updated %s entries according to arXiv." % count)

    return entries