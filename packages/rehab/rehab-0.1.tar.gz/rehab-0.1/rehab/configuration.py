import sys
import copy
import yaml
from paver.easy import path

class Configuration(object):
    "configuration wrapper"
    def __init__(self, configuration=None, data=None):
        self.configuration = copy.deepcopy(configuration) if configuration else {}
        self.data = copy.deepcopy(data) if data else {}

    def do_update(self):
        return True

    def do_run(self):
        return True

    @property
    def repodir(self):
        return path(self.configuration['repodir'])

    def get_updatehooks(self, name):
        updatehooks = self.configuration['updatehooks']
        return updatehooks.get(name, [])

    def get_previous_version(self, name):
        previous_versions = self.data.get('previous_versions', {})
        return previous_versions.get(name)

    def set_previous_version(self, name, current_version):
        self.data.setdefault('previous_versions', {})
        self.data['previous_versions'][name] = current_version

class ConfigurationFile(Configuration):
    "configuration wrapper that can store data in file"
    def __init__(self, config_file=None, data_file=None, configuration=None, data=None):
        super(ConfigurationFile, self).__init__(configuration, data)

        self.config_file = config_file if config_file else self.default_config_file()
        self.configuration.update(self.load_config_file())

        self.data_file = data_file if data_file else self.get_data_file()
        self.data.update(self.load_data_file())

    def is_virtualenv(self):
        return hasattr(sys, 'real_prefix')

    def default_config_file(self):
        if self.is_virtualenv():
            return path(sys.prefix) / 'rehab-config.yml'
        return '/etc/rehab.yml'

    def get_data_file(self):
        data_file = self.configuration.get('data_file')
        if data_file:
            return data_file
        if self.is_virtualenv():
            return path(sys.prefix) / 'rehab-data.yml'
        return '/var/rehab.yml'

    @classmethod
    def parse(cls, options):
        "parse command line options and load configuration"
        config_file = options.get('config')
        data_file = options.get('data')
        config = cls(config_file, data_file)
        return config

    def load_yaml(self, file_name):
        d = {}
        file_name = path(file_name)
        if not file_name.exists():
            return d
        with open(file_name) as f:
            d = yaml.load(f.read())
        return d

    def load_config_file(self):
        return self.load_yaml(self.config_file)

    def load_data_file(self):
        return self.load_yaml(self.data_file)

    def save_data_file(self):
        with open(self.data_file, 'w') as f:
            d = yaml.dump(self.data)
            f.write(d)

