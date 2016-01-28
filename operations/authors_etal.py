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

from entries.entry import *

log = logging.getLogger(__name__)


def authors_etal(entries, max_authors=2):
    """
    Limit the number of authors and editors.
    :param entries: list of entries
    :param max_authors: number of authors/editors that should appear in the bib entry
    :return: list of number of authors/editors limited entries
    """
    log.info("Limiting the number of authors to '%s'." % max_authors)
    count = 0

    for entry in entries:
        if len(entry.authors) > max_authors or len(entry.editors) > max_authors:
            authors_list = []
            num = 0
            for author in entry.authors.authors:
                if num < max_authors:
                    authors_list.append(author)
                    num += 1
                else:
                    authors_list.append(Author("others"))
                    break
            entry.authors.authors = authors_list

            editors_list = []
            num = 0
            for author in entry.editors.authors:
                if num < max_authors:
                    editors_list.append(author)
                    num += 1
                else:
                    editors_list.append(Author("others"))
                    break
            entry.editors.authors = editors_list

            log.debug("[Authors et al.] Updated entry '%s'." % entry.title)
            count += 1

    if count > 0:
        log.info("Limited the number of authors/editors in %s entries." % count)

    return entries
