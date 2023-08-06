from nose import tools
from unittest import TestCase

from paver.easy import path
import tempfile
import tarfile

from rehab.repository import Git, Repository
from rehab.configuration import Configuration

import test_rehab
from test_rehab.utils import RepositoryTesting

def extract_git(where):
    tar = tarfile.open(path(test_rehab.__file__).dirname() / "repos.tar")
    tar.extractall(where)
    tar.close()

class TestGitRepository(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = path(tempfile.mkdtemp(prefix='test_rehab_'))
        extract_git(cls.temp)
        cls.repo = cls.temp / 'repos' / 'repo'
        cls.origin = cls.temp / 'repos' / 'repo.git'

    def setUp(self):
        self.config = Configuration(configuration={
            'repodir': str(self.temp / 'repos'),
        })

    @classmethod
    def tearDownClass(cls):
        cls.temp.rmtree()

    def test_repository_exists(self):
        tools.assert_true(self.repo.exists())
        tools.assert_true(self.origin.exists())

    def test_repository_properties(self):
        git = Git(self.origin, config=self.config, branch='master')
        tools.assert_equals(self.origin, git.name)
        tools.assert_equals(self.origin, git.url)
        tools.assert_equals('repo', git.directory)

    def test_repository_run_command_output(self):
        git = Git(self.origin, config=self.config, branch='master')
        tools.assert_equals(str(self.repo), git.run_command('pwd'))

    def test_repository_current_version(self):
        git = Git(self.origin, config=self.config, branch='master')
        tools.assert_equals('f1f3f67f703d5b05e63ee01221d74b78633d4414', git.current_version)

    def test_every_file_is_changed_if_there_is_no_previous_commits(self):
        git = Git(self.origin, config=self.config, branch='master')
        tools.assert_true(git.has_changed('first-file'))
        tools.assert_true(git.has_changed('second-file'))

    def test_every_file_is_changed_since_the_initial_empty_commit(self):
        self.config.data['previous_versions'] = {
            str(self.origin): 'f917730de114db30e79e362cdd3ce39974f5ba84',
        }
        git = Git(self.origin, config=self.config, branch='master')
        tools.assert_true(git.has_changed('first-file'))
        tools.assert_true(git.has_changed('second-file'))

    def test_files_without_change_did_not_change(self):
        self.config.data['previous_versions'] = {
            str(self.origin): 'de1e71336916848680292588b02d173d10fdfdbf',
        }
        git = Git(self.origin, config=self.config, branch='master')
        tools.assert_false(git.has_changed('second-file'))

class TestBaseRepository(TestCase):
    def setUp(self):
        self.config = Configuration(configuration={'repodir': '/var/repos'})

    def test_repo_object_and_its_properties(self):
        repo = Repository('name', config=self.config)
        tools.assert_equals('name', repo.name)
        tools.assert_equals('1', repo.current_version)
        tools.assert_true(repo.has_changed('any-file-name.txt'))

    def test_repo_create_by_tag_proper_object(self):
        repo = Repository.by_tag('a-default', 'name', config=self.config)
        tools.assert_is_instance(repo, Repository)
        repo = Repository.by_tag('git', 'git@repo/dir.git', self.config, 'branch')
        tools.assert_is_instance(repo, Git)
        tools.assert_equals('dir', repo.directory)
        repo = Repository.by_tag('git', 'git@repo/dir.git', self.config, 'branch', 'directory')
        tools.assert_is_instance(repo, Git)
        tools.assert_equals('directory', repo.directory)

    def test_repo_run_update_hooks_iterates_over_all_given_files(self):
        conf = Configuration(configuration={
            'repodir': '/var/repos',
            'updatehooks': {
                'REPO': [('file.txt', 'echo file.txt has changed')],
            },
        })
        repo = RepositoryTesting('REPO', config=conf)
        repo.run_update_hooks()
        tools.assert_equals(['echo file.txt has changed'], repo.commands)

    def test_repo_loop_iterates_over_repositories_from_config(self):
        conf = Configuration(configuration={
            'repodir': '/var/repos',
            'repositories': [
                ('git', 'git@github.com:kvbik/rehab.git', 'master'),
            ],
        })
        repo = list(Repository.loop(conf, {}))[0]
        tools.assert_is_instance(repo, Git)
        tools.assert_equals('git@github.com:kvbik/rehab.git', repo.name)
        tools.assert_equals('master', repo.branch)

