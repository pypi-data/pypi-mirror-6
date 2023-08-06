from rehab.repository import Repository

class RepositoryTesting(Repository):
    def __init__(self, *args, **kwargs):
        super(RepositoryTesting, self).__init__(*args, **kwargs)
        self.commands = []

    def run_command(self, command):
        self.commands.append(command)

    @classmethod
    def register(cls):
        Repository.CLASSES['test'] = cls

    @classmethod
    def unregister(cls):
        del Repository.CLASSES['test']

