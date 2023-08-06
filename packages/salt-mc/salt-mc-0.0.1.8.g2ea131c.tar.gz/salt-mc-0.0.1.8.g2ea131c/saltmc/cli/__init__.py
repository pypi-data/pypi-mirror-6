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
from cliff.command import Command
import os

from saltmc import utils


class BaseCommand(Command):
    def get_parser(self, prog_name):
        parser = super(BaseCommand, self).get_parser(prog_name)
        parser.add_argument(
            '--only-cached',
            action='store_true',
            help="Only use cached items (WARNING: Might fail!)")
        return parser

    def get_settings(self, args):
        """
        Fetches the settings from the deployment.read
        """
        settings = utils.read_json(self.app_args.spec)
        spec_dir = os.path.dirname(self.app_args.spec)

        # Handle directory setting
        settings.setdefault('directory', spec_dir + '/salt')
        settings['directory'] = os.path.realpath(settings['directory'])

        settings.setdefault('formulas', {})

        mirror = settings['mirrors']['default']

        if 'JENKINS_HOME' in os.environ:
            mirror = settings['mirrors']['jenkins']

        for key, value in settings['formulas'].items():
            fsetting = {} if not isinstance(value, dict) else value

            if isinstance(value, basestring):
                fsetting['url'] = value

            if 'url' not in fsetting:
                fsetting['url'] = "%s/%s" % (mirror, fsetting['repository'])

            if 'revision' in fsetting:
                fsetting['url'] = "%s@%s" % (fsetting['url'], fsetting['revision'])

            settings['formulas'][key] = fsetting
        return settings
