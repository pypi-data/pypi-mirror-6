import logging
import mock
import os
import sys
import unittest

from deployer.config import ConfigStack
from deployer.action.importer import Importer
from deployer.utils import yaml_dump, yaml_load

from base import Base, TEST_OFFLINE


class Options(dict):

    def __getattr__(self, key):
        return self[key]


class ImporterTest(Base):

    def setUp(self):
        self.juju_home = self.mkdir()
        self.change_environment(JUJU_HOME=self.juju_home)
        self.options = Options({
            'bootstrap': False,
            'branch_only': False,
            'configs': [os.path.join(self.test_data_dir, 'wiki.yaml')],
            'debug': True,
            'deploy_delay': 0,
            'destroy_services': None,
            'diff': False,
            'find_service': None,
            'ignore_errors': False,
            'list_deploys': False,
            'no_local_mods': True,
            'overrides': None,
            'rel_wait': 60,
            'retry_count': 0,
            'series': None,
            'terminate_machines': False,
            'timeout': 2700,
            'update_charms': False,
            'verbose': True,
            'watch': False})

    @unittest.skipIf(TEST_OFFLINE,
                     "Requires configured bzr launchpad id and network access")
    @mock.patch('deployer.action.importer.time')
    def test_importer(self, mock_time):
        # Trying to track down where this comes from http://pad.lv/1243827
        stack = ConfigStack(self.options.configs)
        deploy = stack.get('wiki')
        env = mock.MagicMock()
        importer = Importer(env, deploy, self.options)
        importer.run()

        config = {'name': '$hi_world _are_you_there? {guess_who}'}
        self.assertEqual(
            env.method_calls[3], mock.call.deploy(
                'wiki', 'cs:precise/mediawiki', '', config, None, 1, None))

        self.assertEqual(
            yaml_load(yaml_dump(yaml_load(yaml_dump(config)))),
            config)
