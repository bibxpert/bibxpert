#!/usr/bin/env python
#
# Copyright 2015 Rafael Ferreira da Silva
# http://www.rafaelsilva.com/tools
#
#  Licensed under the Apache License, Version 2.0 (the "License");
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
from _hashlib import new

import logging
import re

__author__ = "Rafael Ferreira da Silva"

from entries import entry

log = logging.getLogger(__name__)


class Loader:
    def __init__(self, bib_files):
        """

        :param bib_files:
        """
        self.entries = []
        self.bibFiles = bib_files

    def load(self):
        for filename in self.bibFiles:
            log.debug("Parsing file: %s" % filename)

            with open(filename) as f:
                new_entry = {}

                buffer_line = ""

                for line in f:
                    line = line.strip()
                    if line.startswith("%"):
                        continue
                    if len(line) == 0:
                        continue

                    if line.startswith("@"):
                        new_entry = {}
                        bib_type = line[1:line.index('{')]
                        key = line[line.index('{') + 1:line.index(',')]
                        new_entry['bib_type'] = bib_type
                        new_entry['cite_key'] = key
                    else:
                        if line.startswith("}"):
                            self._add_entry(new_entry)
                            new_entry = {}
                            continue

                        multiple_lines = False
                        if not re.search(r"(\",|\"|\},|\})$", line):
                            multiple_lines = True
                            buffer_line += " " + line

                        if not multiple_lines:
                            values = _parse_entry(buffer_line + " " + line)
                            buffer_line = ""
                            for key in values:
                                if values[key]:
                                    new_entry[key] = values[key]
                                else:
                                    log.debug("[%s] Ignoring entry '%s': value is empty." % (new_entry['cite_key'], key))
        return self.entries

    def _add_entry(self, new_entry):
        """

        :param new_entry:
        """
        log.info("Adding entry: %s" % new_entry["cite_key"])
        self.entries.append(entry.Entry(
            entry_type=_parse_bib_type(new_entry["bib_type"]),
            cite_key=new_entry["cite_key"],
            address=_get_value("address", new_entry),
            annote=_get_value("annote", new_entry),
            authors=_get_value("author", new_entry),
            booktitle=_get_value("booktitle", new_entry),
            chapter=_get_value("chapter", new_entry),
            crossref=_get_value("crossref", new_entry),
            edition=_get_value("edition", new_entry),
            editor=_get_value("editor", new_entry),
            howpublished=_get_value("howpublished", new_entry),
            institution=_get_value("institution", new_entry),
            journal=_get_value("journal", new_entry),
            key=_get_value("key", new_entry),
            month=_get_value("month", new_entry),
            note=_get_value("note", new_entry),
            number=_get_value("number", new_entry),
            organization=_get_value("organization", new_entry),
            pages=_get_value("pages", new_entry),
            publisher=_get_value("published", new_entry),
            school=_get_value("school", new_entry),
            series=_get_value("series", new_entry),
            title=_get_value("title", new_entry),
            type=_get_value("type", new_entry),
            volume=_get_value("volume", new_entry),
            year=_get_value("year", new_entry)
        ))
        log.debug("Added entry: %s" % new_entry)


def _parse_entry(line):
    """

    :param line:
    :return:
    """
    multiple = re.split("\",|\},", line)

    values = {}
    for v in multiple:
        s = re.split("=\s*\"|=\s*{", v)
        key = s[0].strip().lower()
        if len(key) == 0:
            continue
        value = s[1].strip()

        if key == "howpublished":
            value = value.replace("\\url{", "")
            value = value.replace("}}", "")

        if value.startswith("{") or value.startswith("\""):
            value = value[1:len(value)]
        if value.endswith("}") or value.endswith("\""):
            value = value[0:len(value) - 1]
        if value.endswith("},") or value.endswith("\","):
            value = value[0:len(value) - 2]
        value = re.sub("{|\"|}", "", value)
        values[key] = value

    return values


def _parse_bib_type(bib_type_name):
    """

    :param bib_type_name:
    :return:
    """
    if not bib_type_name:
        log.error("Bib type not found.")
        exit(1)

    if bib_type_name.lower() == entry.EntryType.ARTICLE:
        return entry.EntryType.ARTICLE
    if bib_type_name.lower() == entry.EntryType.BOOK:
        return entry.EntryType.BOOK
    if bib_type_name.lower() == entry.EntryType.INCOLLECTION:
        return entry.EntryType.INCOLLECTION
    if bib_type_name.lower() == entry.EntryType.INPROCEEDINGS:
        return entry.EntryType.INPROCEEDINGS
    if bib_type_name.lower() == entry.EntryType.MASTERTHESIS:
        return entry.EntryType.MASTERTHESIS
    if bib_type_name.lower() == entry.EntryType.MISC:
        return entry.EntryType.MISC
    if bib_type_name.lower() == entry.EntryType.PHDTHESIS:
        return entry.EntryType.PHDTHESIS
    if bib_type_name.lower() == entry.EntryType.PROCEEDINGS:
        return entry.EntryType.PROCEEDINGS
    if bib_type_name.lower() == entry.EntryType.TECHREPORT:
        return entry.EntryType.TECHREPORT

    log.error("Unable to parse type: %s" % bib_type_name)
    exit(1)


def _get_value(key, entry):
    """

    :param key:
    :param entry:
    :return:
    """
    if key in entry:
        return entry[key]
    return None