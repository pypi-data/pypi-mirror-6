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

        sync.fetch_all(formulas, self.app_args.cache_dir)

        reports = sync.report(self.app_args.cache_dir, settings)

        exit = 0
        table = []

        keys = formulas.keys()
        keys.sort()
        for name in keys:
            items = reports[name]['items']

            missing = False
            if not reports[name]['status']:
                exit = 1
                missing = "\n".join([i['right'] for i in items])

            table.append([
                name,
                not missing,
                items[0]['left_present'],
                missing])

        self.produce_output(
            parsed_args,
            ('Name', 'Up to Date', 'Cached', 'Missing / Out of date'),
            table)

        sys.exit(exit)
