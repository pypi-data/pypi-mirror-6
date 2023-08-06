# Copyright 2014 Hewlett-Packard Development Company, L.P.
#
# Author: Endre Karlson <endre.karlson@hp.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import os.path

from cliff.lister import Lister

from saltmc.cli import BaseCommand
from saltmc import sync

import sys


class Status(BaseCommand, Lister):
    """
    Shows currently installed versions
    """
    def take_action(self, parsed_args):
        settings = self.get_settings(parsed_args)

        formulas = settings.get('formulas', {})

        if not parsed_args.only_cached:
            sync.fetch_all(formulas, self.app_args.cache_dir)

        formula_reports = sync.report(self.app_args.cache_dir, settings)

        exit = 0
        table = []

        for name, reports in sorted(formula_reports.items(),
                                    key=lambda i: i[0]):
            dirs, items = sync.diff_items(reports)

            status = True if not (dirs or items) else False
            if dirs or items:
                exit = 1

            table.append((
                name,
                status,
                reports['dirs'][0]['left_present'],
                dir_string(dirs) + items_string(items)
            ))

        self.produce_output(
            parsed_args,
            ('Name', 'Up to Date', 'Cached', 'Missing / Out of date'),
            table)
        sys.exit(exit)


def dir_string(dirs):
    string = ""
    for report in dirs:
        string += "dir: %s\n" % report['right']
        for i in ['diff_files', 'left_only', 'right_only']:
            if report[i]:
                string += "%s:\n%s\n" % (i, ", ".join(report[i]))
    return string


def items_string(reports):
    string = ""
    if reports:
        string += "Items:\n"
        for name, values in reports.items():
            string += ", ".join([os.path.basename(r['left']) for r in values])
    return string
