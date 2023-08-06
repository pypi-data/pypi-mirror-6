from paver.easy import sh

class Repository(object):
    CLASSES = {}

    def __init__(self, name, config, *args, **kwargs):
        self.name = name
        self.config = config
        self.cwd = self.config.repodir

    @classmethod
    def by_tag(cls, tag, name, config, *args):
        "create repository of proper class given by tag"
        C = cls.CLASSES.get(tag, cls)
        return C(name, config, *args)

    @classmethod
    def loop(cls, config, options):
        "iterate through repositories from config"
        for i in config.configuration.get('repositories', []):
            tag, name = i[:2]
            args = i[2:]
            yield cls.by_tag(tag, name, config, *args)

    @property
    def current_version(self):
        return '1'

    def has_changed(self, file_path):
        return True

    def update(self):
        pass

    def run_command(self, command):
        out = sh(command, cwd=self.cwd, capture=True, ignore_error=False)
        return out.strip()

    def run_update_hooks(self):
        "take all the hooks and run commands if given file has changed"
        out = []
        updatehooks = self.config.get_updatehooks(self.name)
        for file_path, command in updatehooks:
            line = [file_path, command, None]
            if self.has_changed(file_path):
                line[-1] = self.run_command(command)
            out.append(line)
        return out

class Git(Repository):
    "git vcs abstraction"

    def __init__(self, name, config, branch, directory=None):
        self.name = name
        self.branch = branch
        self.config = config

        self.url = name
        self.directory = d = name.split('/')[-1]
        if d.endswith('.git'):
            self.directory = d[:-4]
        self.directory = directory or self.directory

        self.cwd = self.config.repodir / self.directory

    @property
    def current_version(self):
        cmd = 'git log --format=format:%H -n1'
        return self.run_command(cmd)

    def has_changed(self, file_path):
        previous_version = self.config.get_previous_version(self.name)
        if previous_version is None:
            return True
        cmd = 'git diff {v}.. {f}'.format(v=previous_version, f=file_path)
        return bool(self.run_command(cmd))

Repository.CLASSES['git'] = Git

