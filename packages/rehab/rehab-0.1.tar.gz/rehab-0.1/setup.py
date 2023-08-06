from setuptools import setup, find_packages
from os import path

base = path.dirname(__file__)

f = open(path.join(base, 'README.rst'))
long_description = f.read().strip()
f.close()

f = open(path.join(base, 'requirements.txt'))
install_requires = [ r.strip() for r in f.readlines() if '#egg=' not in r ]
f.close()

setup(
    name='rehab',
    version='0.1',
    packages=['rehab'],
)

setup(
    name='rehab',
    version='0.1',
    description='example packaging layout',
    long_description=long_description,
    license='BSD',
    author='Jakub Vysoky',
    author_email='jakub.vysoky@gmail.com',
    url='https://github.com/kvbik/rehab',
    packages=find_packages(),
    entry_points={'console_scripts': ['rehab = rehab.main:main']},
    install_requires=install_requires,
    include_package_data=True,
    zip_safe=False,
)

