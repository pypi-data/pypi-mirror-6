from nose import tools
from unittest import TestCase

import sys

from rehab.configuration import Configuration, ConfigurationFile

class TestConfiguration(TestCase):
    def test_config_object_and_its_properties(self):
        conf = Configuration()
        tools.assert_equals({}, conf.configuration)
        tools.assert_equals({}, conf.data)

        conf = Configuration(configuration={
            'repodir': '/var/repos',
            'updatehooks': {'name': [(1,1), (2,2)]},
        })
        tools.assert_equals('/var/repos', str(conf.repodir))
        tools.assert_equals([(1,1), (2,2)], conf.get_updatehooks('name'))

    def test_config_set_current_version(self):
        conf = Configuration()
        conf.set_previous_version('repo', '10')
        tools.assert_equals('10', conf.get_previous_version('repo'))

class TestConfigurationFile(TestCase):
    def setUp(self):
        self.real_prefix = sys.real_prefix
        del sys.real_prefix

    def tearDown(self):
        sys.real_prefix = self.real_prefix

    def test_config_parse_load_some_config_object(self):
        config = ConfigurationFile.parse({'config': '/etc/my-rehab.yml', 'data': '/var/my-rehab.yml'})
        tools.assert_is_instance(config, ConfigurationFile)
        tools.assert_equals('/etc/my-rehab.yml', config.config_file)
        tools.assert_equals('/var/my-rehab.yml', config.data_file)

    def test_config_with_default_values(self):
        config = ConfigurationFile()
        tools.assert_equals('/etc/rehab.yml', config.config_file)
        tools.assert_equals('/var/rehab.yml', config.data_file)

    def test_config_data_file_can_be_specified_in_configuration(self):
        config = ConfigurationFile(configuration={'data_file': '/my/custom/data-file'})
        tools.assert_equals('/my/custom/data-file', config.data_file)

    def test_config_with_default_values_in_virtualenv(self):
        sys.real_prefix = self.real_prefix
        config = ConfigurationFile()
        tools.assert_equals(sys.prefix + '/rehab-config.yml', config.config_file)
        tools.assert_equals(sys.prefix + '/rehab-data.yml', config.data_file)

