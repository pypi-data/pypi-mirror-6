from nose import tools
from unittest import TestCase

import sys
from paver.easy import path
import tempfile

from rehab.main import main

from test_rehab.utils import RepositoryTesting

# basic rehab configuration, default values will be pretty similar
EXAMPLE_CONFIG = {
    # where your repositories will checkout to
    'repodir': '/var/repos/',

    # list of repositories: type, name and other params
    'repositories': [
        ('git', 'git@github.com:kvbik/rehab.git', 'master'),
    ],

    # run commands for each file which has changed since the last run
    'updatehooks': {
        'git@github.com:kvbik/rehab.git': [
            ('requirements.txt', 'pip install -r requirements.txt'),
            ('requirements.txt', 'python setup.py develop'),
            ('setup.py', 'python setup.py develop'),
        ],
    },
}

# we use yaml as a config parser
CONFIG = """
repodir: /var/repos
repositories:
- [test, a-repo]
updatehooks:
  a-repo:
  - [a-file, do something]
  - [another-file, do something else]
"""
DATA = """
previous_versions:
  a-repo: '10'
  another-repo: '123'
"""

class TestMain(TestCase):
    def setUp(self):
        self.temp = path(tempfile.mkdtemp(prefix='test_rehab_'))
        self.config_file = self.temp / 'rehab_config.yml'
        self.data_file = self.temp / 'rehab_data.yml'

        self.cmd_line = ['rehab.py', 'update', '-c', self.config_file, '-d', self.data_file]
        with open(self.config_file, 'w') as f:
            f.write(CONFIG)
        with open(self.data_file, 'w') as f:
            f.write(DATA)

        RepositoryTesting.register()

        self.argv = sys.argv

    def _test_main_just_run_it_so_there_is_no_syntax_error(self):
        # previous commits has changed
        with open(self.data_file) as f:
            tools.assert_in("a-repo: '1'", f.read())

    def test_main_just_run_it_so_there_is_no_syntax_error(self):
        main(self.cmd_line)
        self._test_main_just_run_it_so_there_is_no_syntax_error()

    def test_main_just_run_it_so_there_is_no_syntax_error_with_argv(self):
        sys.argv = self.cmd_line
        main()
        self._test_main_just_run_it_so_there_is_no_syntax_error()

    def test_main_help_just_a_check_it_works(self):
        sys.argv = ['rehab']
        main()

    def tearDown(self):
        sys.argv = self.argv
        RepositoryTesting.unregister()
        self.temp.rmtree()

