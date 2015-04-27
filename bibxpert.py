#!/usr/bin/env python
#
# Copyright 2015 Rafael Ferreira da Silva
#  http://www.rafaelsilva.com/tools
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
__author__ = "Rafael Ferreira da Silva"

import os
from optparse import OptionParser

from operations.deduplicate import *
from tools import loader

log = logging.getLogger(__name__)


def process(options, args):

    # Load entries
    entries = loader.Loader(args).load()

    # Deduplicate
    if options.all or options.deduplicate:
        entries = deduplicate(entries)

    # Write results
    if options.output:
        f = open(options.output, 'w')
        log.info("Writing entries to '%s'." % options.output)

    for entry in entries:
        if options.output:
            f.write(entry.__str__())
        else:
            print entry

    if options.output:
        f.close()


def option_parser(usage):
    """

    :param usage: tool usage string
    :return: parsed options and arguments
    """
    parser = OptionParser(usage="usage: %s" % usage)

    parser.add_option("-a", "--all", dest="all", action="store_true",
                      default=False, help="Apply all options")
    parser.add_option("-D", "--deduplicate", dest="deduplicate", action="store_true",
                      default=False, help="Remove duplicated entries")

    parser.add_option("-o","--output",action="store",type="string",
        dest="output",default=None, help = "Output file")
    parser.add_option("-d", "--debug", dest="debug", action="store_true",
                      default=False, help="Turn on debugging")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                      default=False, help="Show progress messages")

    # Add a hook so we can handle global arguments
    fn = parser.parse_args

    def parse(*args, **kwargs):
        options, args = fn(*args, **kwargs)

        if options.debug:
            configure_logging(level=logging.DEBUG)
        elif options.verbose:
            configure_logging(level=logging.INFO)
        else:
            configure_logging(logging.WARNING)
        return options, args

    parser.parse_args = parse

    return parser


def main():
    args = sys.argv[1:]
    parser = option_parser("bibxpert.py [OPTIONS] <LIST_OF_BIBFILES>")
    options, args = parser.parse_args(args)

    if len(args) == 0:
        log.error("At least one bibtex file should be provided.")
        parser.print_help()
        exit(1)
    if not options.all and not options.deduplicate:
        log.error("At least one option should be provided.")
        parser.print_help()
        exit(1)

    process(options, args)


if __name__ == '__main__':
    main()