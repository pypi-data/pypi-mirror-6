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
import logging
import shutil

from cliff.lister import Lister

from saltmc.cli import BaseCommand
from saltmc import sync
from saltmc import utils


LOG = logging.getLogger(__name__)


class Sync(BaseCommand, Lister):
    """
    Sync a deployment using a specification or add / install a specific
    formula
    """
    def take_action(self, parsed_args):
        settings = self.get_settings(parsed_args)

        formulas = settings.get('formulas', {})

        sync.fetch_all(formulas, self.app_args.cache_dir)

        reports = sync.report(self.app_args.cache_dir, settings)

        table = []

        keys = formulas.keys()
        keys.sort()
        for name in keys:
            items = reports[name]['items']

            changed_items = []
            if not reports[name]['status']:

                for i in items:
                    LOG.info("Copying from %s to %s" % (
                             i['left'], i['right']))
                    if not i['status'] and i['right_present']:
                        LOG.debug("Deleting existing formula dir %s" %
                                  i['right'])
                        utils.rmtree(i['right'])

                    shutil.copytree(i['left'], i['right'])

                changed_items.append([name, "\n".join(changed_items)])

            table.append((name, changed_items))

        return ('Formula', 'Updated'), table
