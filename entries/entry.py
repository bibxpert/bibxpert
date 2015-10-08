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

import unicodedata
from tools.utils import *

log = logging.getLogger(__name__)


class EntryType:
    ARTICLE = "article"
    BOOK = "book"
    INCOLLECTION = "incollection"
    INPROCEEDINGS = "inproceedings"
    MASTERTHESIS = "mastersthesis"
    PHDTHESIS = "phdthesis"
    MISC = "misc"
    PROCEEDINGS = "proceedings"
    TECHREPORT = "techreport"


class Entry:
    def __init__(self, entry_type=None, cite_key=None, address=None, annote=None, authors=None, booktitle=None,
                 chapter=None, crossref=None, edition=None, editor=None, howpublished=None, institution=None,
                 journal=None, key=None, month=None, note=None, number=None, organization=None, pages=None,
                 publisher=None, school=None, series=None, title=None, type=None, url=None, volume=None,
                 year=None, doi=None):
        """
        Create a bib entry.
        :param entry_type: type of the entry (e.g., article, inproceedings, etc.)
        :param cite_key: cite key used in latex files to reference the entry
        :param address:
        :param annote:
        :param authors: list of authors (separated by 'and')
        :param booktitle:
        :param chapter:
        :param crossref:
        :param edition:
        :param editors:
        :param howpublished:
        :param institution:
        :param journal:
        :param key: publication key (usually required for 'misc' entry types)
        :param month:
        :param note:
        :param number:
        :param organization:
        :param pages: page numbers (separated by dashes)
        :param publisher:
        :param school:
        :param series:
        :param title: publication title
        :param type:
        :param url: publication url
        :param volume:
        :param year: publication year
        :param doi: document object identifier
        """
        self.entry_type = entry_type
        self.cite_key = cite_key
        self.address = address
        self.annote = annote
        self.authors = Authors(authors_list=authors)
        self.booktitle = _parse_booktitle(booktitle)
        self.chapter = chapter
        self.crossref = crossref
        self.edition = edition
        self.editors = Authors(authors_list=editor)
        self.howpublished = howpublished
        self.institution = institution
        self.journal = journal
        self.key = key
        self.month = month
        self.note = note
        self.number = number
        self.organization = organization
        self.pages = _parse_pages(pages)
        self.publisher = publisher
        self.school = school
        self.series = series
        self.title = title
        self.type = type
        self.url = url
        self.volume = volume
        self.year = year
        self.doi = doi
        self.online_processed = False
        self.compressed = False

    def merge(self, entry):
        """
        Merge two entries.
        :param entry: entry to be merged
        """
        self.entry_type = _merge_entry_type(self.entry_type, entry.entry_type)
        self.address = _merge_field(self.address, entry.address)
        self.annote = _merge_field(self.annote, entry.annote)
        self.booktitle = _merge_field(self.booktitle, entry.booktitle)
        self.chapter = _merge_field(self.chapter, entry.chapter)
        self.crossref = _merge_field(self.crossref, entry.crossref)
        self.edition = _merge_field(self.edition, entry.edition)
        self.howpublished = _merge_field(self.howpublished, entry.howpublished)
        self.institution = _merge_field(self.institution, entry.institution)
        self.journal = _merge_field(self.journal, entry.journal)
        self.key = _merge_field(self.key, entry.key)
        self.month = _merge_field(self.month, entry.month)
        self.note = _merge_field(self.note, entry.note)
        self.number = _merge_field(self.number, entry.number, is_int=True)
        self.organization = _merge_field(self.organization, entry.organization)
        self.pages = _merge_field(self.pages, entry.pages)
        self.publisher = _merge_field(self.publisher, entry.publisher)
        self.school = _merge_field(self.school, entry.school)
        self.series = _merge_field(self.series, entry.series)
        self.title = _merge_field(self.title, entry.title)
        self.type = _merge_field(self.type, entry.type)
        self.url = _merge_field(self.url, entry.url)
        self.volume = _merge_field(self.volume, entry.volume)
        self.year = _merge_field(self.year, entry.year, is_int=True)
        self.doi = _merge_field(self.doi, entry.doi)
        self.editors.merge(entry.editors.authors)
        self.authors.merge(entry.authors.authors)


    def __str__(self):
        entry_str = "@%s{%s,\n" % (self.entry_type, self.cite_key)
        entry_str += _print_field("address", self.address)
        entry_str += _print_field("annote", self.annote)
        entry_str += _print_field("author", self.authors)
        entry_str += _print_field("booktitle", self.booktitle, capitals=True)
        entry_str += _print_field("chapter", self.chapter)
        entry_str += _print_field("crossref", self.crossref)
        entry_str += _print_field("edition", self.edition)
        entry_str += _print_field("editor", self.editors)
        entry_str += _print_field("howpublished", self.howpublished)
        entry_str += _print_field("institution", self.institution)
        entry_str += _print_field("journal", self.journal, capitals=True)
        entry_str += _print_field("key", self.key)
        entry_str += _print_field("month", self.month)
        entry_str += _print_field("note", self.note)
        entry_str += _print_field("number", self.number)
        entry_str += _print_field("organization", self.organization)
        entry_str += _print_field("pages", self.pages)
        entry_str += _print_field("publisher", self.publisher)
        entry_str += _print_field("school", self.school)
        entry_str += _print_field("series", self.series)
        entry_str += _print_field("title", self.title)
        entry_str += _print_field("type", self.type)
        entry_str += _print_field("url", self.url)
        entry_str += _print_field("volume", self.volume)
        entry_str += _print_field("year", self.year)
        entry_str += _print_field("doi", self.doi)
        entry_str += "}\n\n"
        return entry_str

    def __repr__(self):
        return self.__str__


class Authors:
    def __init__(self, authors_list=None):
        """

        :param authors_list: list of authors names
        """
        self.authors = []
        if authors_list:
            authors_list = authors_list.replace(" AND ", " and ")
            for author in authors_list.split(" and "):
                self.authors.append(Author(author.strip()))

    def merge(self, merge_authors):
        max_len = min(len(merge_authors), len(self.authors))
        for i in range(0, max_len):
            self.authors[i].merge(merge_authors[i])
        if len(merge_authors) > len(self.authors):
            for i in range(max_len, len(merge_authors)):
                self.authors.append(merge_authors[i])

    def __str__(self):
        authors = ""
        for author in self.authors:
            if len(authors) > 0:
                authors += " and "
            authors += author.__str__()
        return authors

    def __repr__(self):
        return self.__str__

    def __len__(self):
        return len(self.authors)


class Author:
    def __init__(self, author_name):
        """

        :param author_name: name of a single author
        """
        self.first_name = ""
        self.last_name = ""

        if "," in author_name:
            s = author_name.split(",")
            self.first_name = s[1].strip()
            self.last_name = s[0].strip()
        else:
            s = author_name.split(" ")
            if len(s) == 2:
                self.first_name = s[0].strip()
                self.last_name = s[1].strip()
            elif len(s) > 2:
                index = len(s) - 1
                value = s[len(s) - 2]
                if len(value) <= 2 and not value.endswith('.'):
                    self.last_name = value + " " + s[len(s) - 1]
                    index -= 1
                else:
                    self.last_name = s[len(s) - 1]
                for i in range(0, index):
                    if len(self.first_name) > 0:
                        self.first_name += " "
                    self.first_name += s[i]
            else:
                self.first_name = author_name
                self.last_name = None
                if not author_name.lower() == "others":
                    log.warning("Unable to find last name: %s" % author_name)

    def merge(self, author_merge):
        """
        Merge author's first and last names with another similar entry.
        :param author_merge: author names to be merged
        """
        if not self.last_name and author_merge.last_name:
            self.last_name = author_merge.last_name
            if self.first_name.lower() == "others":
                self.first_name = author_merge.first_name

        elif author_merge.last_name and is_similar(self.last_name, author_merge.last_name, threshold=0.5):
            if len(author_merge.last_name) > len(self.last_name):
                self.last_name = author_merge.last_name
            if len(author_merge.first_name) > len(self.first_name):
                self.first_name = author_merge.first_name

    def __str__(self):
        if self.last_name:
            return self.last_name + ", " + self.first_name
        else:
            return self.first_name

    def __repr__(self):
        return self.__str__


def _parse_pages(pages):
    """
    Parse the page number to a 2-dashes format (e.g. 100--120).
    :param pages: entry page numbers
    :return:
    """
    if pages:
        if "-" in pages:
            if not pages.count("-") == 2:
                pages = re.sub("-+", "--", pages)
        return pages
    return None


def _parse_booktitle(booktitle):
    """

    :param booktitle: entry book title
    """
    if booktitle:
        if "," in booktitle:
            bt = booktitle.split(",")
            booktitle = bt[1].strip() + " " + bt[0].strip()
        return booktitle
    return None


def _print_field(field_name, field_value, capitals=False):
    """
    Print a field in bib format is value is not none.
    :param field_name: name of the field
    :param field_value: value of the field
    :return: field in bib format or blank if field is None
    """
    if field_value:
        field_value = str(field_value).replace("_", "\_")
        field_value = str(field_value).replace("\\\\_", "\_")
        field_value = str(field_value).replace("#", "\#")
        field_value = str(field_value).replace("\\\\#", "\#")
        field_value = str(field_value).replace("$", "")
        if capitals:
            return "\t%s = {{%s}},\n" % (field_name, field_value)
        else:
            return "\t%s = {%s},\n" % (field_name, field_value)
    return ""


def _merge_field(f1, f2, is_int=False):
    """
    Merge field contents from two entries.
    :param f1: first field
    :param f2: second field
    :param is_int: whether the field is an integer
    :return: merged field contents
    """
    if not f1 and not f2:
        return None
    if not f2 and f1 is not None:
        return f1
    if not f1 and f2 is not None:
        return f2
    if is_int:
        try:
            if int(f1) >= int(f2):
                return f1
            else:
                return f2
        except ValueError:
            pass
    if len(f1) >= len(f2):
        return f1
    else:
        return f2
    return f1


def _merge_entry_type(t1, t2):
    """
    Merge entry type field from two entries according to entry type level.
    :param t1: first entry type
    :param t2: second entry type
    :return: merged entry type
    """
    if t1 == EntryType.ARTICLE or t2 == EntryType.ARTICLE:
        return EntryType.ARTICLE
    if t1 == EntryType.INPROCEEDINGS or t2 == EntryType.INPROCEEDINGS:
        return EntryType.INPROCEEDINGS
    if t1 == EntryType.INCOLLECTION or t2 == EntryType.INCOLLECTION:
        return EntryType.INCOLLECTION
    if t1 == EntryType.PROCEEDINGS or t2 == EntryType.PROCEEDINGS:
        return EntryType.PROCEEDINGS
    if t1 == EntryType.BOOK or t2 == EntryType.BOOK:
        return EntryType.BOOK
    if t1 == EntryType.PHDTHESIS or t2 == EntryType.PHDTHESIS:
        return EntryType.PHDTHESIS
    if t1 == EntryType.MASTERTHESIS or t2 == EntryType.MASTERTHESIS:
        return EntryType.MASTERTHESIS
    if t1 == EntryType.TECHREPORT or t2 == EntryType.TECHREPORT:
        return EntryType.TECHREPORT
    return EntryType.MISC
