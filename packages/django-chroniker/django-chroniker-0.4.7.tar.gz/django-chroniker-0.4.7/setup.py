 
from setuptools import setup, find_packages, Command

import os
import sys
import urllib

import chroniker

def get_reqs(reqs=['Django>=1.4.0', 'python-dateutil', 'psutil']):
    # optparse is included with Python <= 2.7, but has been deprecated in favor
    # of argparse.  We try to import argparse and if we can't, then we'll add
    # it to the requirements
    try:
        import argparse
    except ImportError:
        reqs.append('argparse>=1.1')
    return reqs

class TestCommand(Command):
    description = "Runs unittests."
    user_options = [
        ('name=', None,
         'Name of the specific test to run.'),
        ('virtual-env-dir=', None,
         'The location of the virtual environment to use.'),
    ]
    def initialize_options(self):
        self.name = None
        self.virtual_env_dir = './.env'
    def finalize_options(self):
        pass
    def run(self):
        args = dict(virtual_env_dir=self.virtual_env_dir)
        if not os.path.isdir(self.virtual_env_dir):
            os.system('virtualenv %(virtual_env_dir)s' % args)
            for package in get_reqs():
                args['package'] = package
                cmd = '. %(virtual_env_dir)s/bin/activate; pip install -U %(package)s; deactivate' % args
                #print cmd
                os.system(cmd)
        if self.name:
            cmd = '. ./.env/bin/activate; django-admin.py test --pythonpath=. --settings=chroniker.tests.settings tests.JobTestCase.%s; deactivate' % self.name
        else:
            cmd = '. ./.env/bin/activate; django-admin.py test --pythonpath=. --settings=chroniker.tests.settings tests; deactivate'
        #print cmd
        os.system(cmd)
        
setup(
    name = "django-chroniker",
    version = chroniker.__version__,
    packages = find_packages(),
    scripts = ['bin/chroniker'],
    package_data = {
        '': ['docs/*.txt', 'docs/*.py'],
        'chroniker': [
            'templates/*.*',
            'templates/*/*.*',
            'templates/*/*/*.*',
            'fixtures/*'
        ],
    },
    author = "Chris Spencer",
    author_email = "chrisspen@gmail.com",
    description = "Easily control cron jobs via Django's admin.",
    license = "BSD",
    url = "https://github.com/chrisspen/django-chroniker",
    classifiers = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    zip_safe = False,
    install_requires = get_reqs(),
#    dependency_links = [
#        'http://labix.org/download/python-dateutil/python-dateutil-1.5.tar.gz',
#    ]
    cmdclass={
        'test': TestCommand,
    },
)
