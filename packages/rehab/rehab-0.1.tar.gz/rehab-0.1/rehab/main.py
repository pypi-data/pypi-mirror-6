import sys
from paver import tasks
from paver.easy import cmdopts, path

import rehab
from rehab.configuration import ConfigurationFile
from rehab.repository import Repository

def main(argv=None):
    if argv is None:
        argv = sys.argv

    if not ('-f' in argv and '--file' in argv):
        pavement = path(rehab.__file__).dirname() / 'main.py'
        args = ['-f', pavement] + argv[1:]

    if len(args) == 2:
        args.append('help')
    tasks.main(args)

@cmdopts([
    ('config=', 'c', 'custom configuration file'),
    ('data=', 'd', 'data file where previous versions are stored'),
])
def update(options):
    "update repositories and run hooks there"
    config = ConfigurationFile.parse(options)
    # no ugly debug prints
    tasks.environment.quiet = True

    def _print(out):
        for f,c,o in out:
            x = '{}: {}'.format(f, c)
            print(x)
            print('='*len(x))
            print(o if o else '.. not changed')
            print()

    for r in Repository.loop(config, options):
        if config.do_update():
            r.update()
        if config.do_run():
            _print(r.run_update_hooks())
        config.set_previous_version(r.name, r.current_version)

    config.save_data_file()
up = update

if __name__ == '__main__':
    main()

