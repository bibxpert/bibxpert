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

from tools.utils import *

log = logging.getLogger(__name__)


def deduplicate(entries):
    """
    Look for duplicated bibliography entries and merge them.
    :param entries: list of entries
    :return: list of deduplicated entries
    """
    log.info("Seeking for duplicated entries")
    parsed_entries = []
    cite_keys = {}
    titles = {}
    key_replacement = {}

    count_keys = 0
    count_titles = 0

    for entry in entries:
        # Seek for duplicated cite keys
        if entry.cite_key.lower() in cite_keys:
            count_keys += 1
            cite_keys[entry.cite_key.lower()].merge(entry)

        # Seek for duplicated titles
        else:
            matched, matched_entry = _in_list(entry.title.lower(), titles)
            if matched:
                count_titles += 1
                matched_entry.merge(entry)
                if matched_entry.cite_key in key_replacement:
                    key_replacement[matched_entry.cite_key].append(entry.cite_key)
                else:
                    key_replacement[matched_entry.cite_key] = [entry.cite_key]
            else:
                cite_keys[entry.cite_key.lower()] = entry
                titles[entry.title.lower()] = entry
                parsed_entries.append(entry)

    if count_keys > 0:
        log.info("Found %s duplicated cite key entries." % count_keys)
    if count_titles > 0:
        log.info("Found %s duplicated title entries." % count_titles)
        print "The following cite keys should be replaced in your LaTeX source files:"
        for key in key_replacement:
            keys = ""
            for k in key_replacement[key]:
                if len(keys) > 0:
                    keys += ", "
                keys += k
            print "    %s ==> %s" % (keys, key)

    log.debug("Initial number of entries: %s" % len(entries))
    log.debug("Number of entries after deduplication: %s" % len(parsed_entries))

    return parsed_entries


def _in_list(name, list):
    """
    Test whether a string is similar to a string in the list.
    :param name: string to be matched
    :param list: list of strings
    :return: whether a string is similar and the similar entry
    """
    for item in list:
        if is_similar(name, item):
            return True, list[item]
    return False, None