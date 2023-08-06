================================
rehab - manage your dependencies
================================

rehab is a very simple tool, that runs a set of commands
only if a given file has been changed since the last run

install
=======

only::

  pip install rehab

configuration
=============

crate a configuration file::

  # basic rehab configuration, default values will be pretty similar
  EXAMPLE_CONFIG = {
      # where your repositories will checkout to
      'repodir': '/var/repos/',

      # list of repositories: type, name and other params
      'repositories': [
          ['git', 'git@github.com:kvbik/rehab.git', 'master'],
      ],

      # run commands for each file which has changed since the last run
      'updatehooks': {
          'git@github.com:kvbik/rehab.git': [
              ['requirements.txt', 'pip install -r requirements.txt'],
              ['requirements.txt', 'python setup.py develop'],
              ['setup.py', 'python setup.py develop'],
          ],
      },
  }

  import yaml
  with open('/etc/my-rehab.yml', 'w') as f:
    f.write(yaml.dump(EXAMPLE_CONFIG))

and call::

  rehab update -c /etc/my-rehab.yml -d /var/my-rehab.yml

