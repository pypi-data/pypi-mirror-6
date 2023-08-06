import base64
import StringIO
import os
import unittest


from deployer.config import ConfigStack
from deployer.deployment import Deployment
from deployer.utils import setup_logging, ErrorExit

from .base import Base, TEST_OFFLINE


class DeploymentTest(Base):

    def setUp(self):
        self.output = setup_logging(
            debug=True, verbose=True, stream=StringIO.StringIO())

    def get_named_deployment(self, file_name, stack_name):
        return ConfigStack(
            [os.path.join(
                self.test_data_dir, file_name)]).get(stack_name)

    @unittest.skipIf(TEST_OFFLINE,
                     "Requires configured bzr launchpad id and network access")
    def test_deployer(self):
        d = ConfigStack(
            [os.path.join(
                self.test_data_dir, "blog.yaml")]).get('wordpress-prod')
        services = d.get_services()
        self.assertTrue([s for s in services if s.name == "newrelic"])

        # Ensure inheritance order reflects reality, instead of merge value.
        self.assertEqual(
            d.data['inherits'],
            ['wordpress-stage', 'wordpress-base', 'metrics-base'])

        # Fetch charms to verify late binding config values & validation.
        t = self.mkdir()
        os.mkdir(os.path.join(t, "precise"))
        d.repo_path = t
        d.fetch_charms()

        # Load up overrides and resolves
        d.load_overrides(["key=abc"])
        d.resolve()

        # Verify include-base64
        self.assertEqual(d.get_service('newrelic').config, {'key': 'abc'})
        self.assertEqual(
            base64.b64decode(d.get_service('blog').config['wp-content']),
            "HelloWorld")

        # TODO verify include-file

        # Verify relations
        self.assertEqual(
            list(d.get_relations()),
            [('blog', 'db'), ('blog', 'cache'), ('blog', 'haproxy')])

    def test_validate_placement_sorting(self):
        d = self.get_named_deployment("stack-placement.yaml", "stack")
        services = d.get_services()
        self.assertEqual(services[0].name, 'nova-compute')
        try:
            d.validate_placement()
        except ErrorExit:
            self.fail("Should not fail")

    def test_validate_invalid_placement_nested(self):
        d = self.get_named_deployment("stack-placement-invalid.yaml", "stack")
        services = d.get_services()
        self.assertEqual(services[0].name, 'nova-compute')
        try:
            d.validate_placement()
        except ErrorExit:
            pass
        else:
            self.fail("Should fail")

    def test_validate_invalid_placement_no_with_service(self):
        d = self.get_named_deployment(
            "stack-placement-invalid-2.yaml", "stack")
        services = d.get_services()
        self.assertEqual(services[0].name, 'nova-compute')
        try:
            d.validate_placement()
        except ErrorExit:
            pass
        else:
            self.fail("Should fail")

    def test_get_unit_placement(self):
        d = self.get_named_deployment("stack-placement.yaml", "stack")
        status = {
            'services': {
                'nova-compute': {
                    'units': {
                        'nova-compute/2': {'machine': '1'},
                        'nova-compute/3': {'machine': '2'},
                        'nova-compute/4': {'machine': '3'}}}}}
        placement = d.get_unit_placement('ceph', status)
        self.assertEqual(placement.get(0), '1')
        self.assertEqual(placement.get(1), '2')
        self.assertEqual(placement.get(2), None)

        placement = d.get_unit_placement('quantum', status)
        self.assertEqual(placement.get(0), 'lxc:1')
        self.assertEqual(placement.get(2), 'lxc:3')
        self.assertEqual(placement.get(3), None)

        placement = d.get_unit_placement('verity', status)
        self.assertEqual(placement.get(0), 'lxc:3')

        placement = d.get_unit_placement('mysql', status)
        self.assertEqual(placement.get(0), '0')

        placement = d.get_unit_placement('semper', status)
        self.assertEqual(placement.get(0), '3')

    def test_multiple_relations_no_weight(self):
        data = {"relations": {"wordpress": {"consumes": ["mysql"]},
                              "nginx": {"consumes": ["wordpress"]}}}
        d = Deployment("foo", data, include_dirs=())
        self.assertEqual(
            [('nginx', 'wordpress'), ('wordpress', 'mysql')],
            list(d.get_relations()))

    def test_multiple_relations_weighted(self):
        data = {
            "relations": {
                "keystone": {
                    "weight": 100,
                    "consumes": ["mysql"]
                },
                "nova-compute": {
                    "weight": 50,
                    "consumes": ["mysql"]
                },
                "glance": {
                    "weight": 70,
                    "consumes": ["mysql"]
                },
            }
        }
        d = Deployment("foo", data, include_dirs=())
        self.assertEqual(
            [('keystone', 'mysql'), ('glance', 'mysql'),
             ('nova-compute', 'mysql')], list(d.get_relations()))

    def test_getting_service_names(self):
        # It is possible to retrieve the service names.
        deployment = self.get_named_deployment("stack-placement.yaml", "stack")
        service_names = deployment.get_service_names()
        expected_service_names = [
            'ceph', 'mysql', 'nova-compute', 'quantum', 'semper', 'verity']
        self.assertEqual(set(expected_service_names), set(service_names))
