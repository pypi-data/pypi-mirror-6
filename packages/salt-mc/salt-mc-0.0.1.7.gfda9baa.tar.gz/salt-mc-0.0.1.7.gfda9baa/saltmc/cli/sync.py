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
import os
import shutil

from saltmc.cli import BaseCommand
from saltmc import sync
from saltmc import utils


LOG = logging.getLogger(__name__)


class Sync(BaseCommand):
    """
    Sync a deployment using a specification or add / install a specific
    formula
    """
    def take_action(self, parsed_args):
        settings = self.get_settings(parsed_args)

        formulas = settings.get('formulas', {})

        if not parsed_args.only_cached:
            sync.fetch_all(formulas, self.app_args.cache_dir)

        formula_reports = sync.report(self.app_args.cache_dir, settings)

        for name, reports in sorted(formula_reports.items(),
                                    key=lambda i: i[0]):
            dirs, items = sync.diff_items(reports)

            # NOTE: We don't care about each changed thing in dirs, we just
            # wipe the whole dest and copy the source.
            if dirs:
                if dirs[0]['right_present']:
                    LOG.info("Deleting existing formula dir %s" %
                              dirs[0]['right'])
                    utils.rmtree(dirs[0]['right'])

                LOG.info("Copying from %s to %s" % (dirs[0]['left'],
                         dirs[0]['right']))
                shutil.copytree(dirs[0]['left'], dirs[0]['right'])

            if items:
                for key, values in items.items():
                    destination = os.path.join(settings['directory'], key)
                    import ipdb
                    ipdb.set_trace()
                    if not os.path.exists(destination):
                        LOG.info('Destination %s was missing, creating.' %
                                  destination)
                        os.makedirs(destination)
                    for item in values:
                        LOG.info('Copying %s to %s' %
                                 (item['left'], item['right']))
                        shutil.copy(item['left'], item['right'])
