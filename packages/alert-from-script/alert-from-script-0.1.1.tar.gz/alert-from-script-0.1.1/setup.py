#!/usr/bin/env python

from setuptools import setup
import sys

kwargs = {
    'name': 'alert-from-script',
    'version': '0.1.1',
    'description': 'Generate SNS alerts from any command.',
    'author': 'Brandon Adams',
    'author_email': 'brandon.adams@me.com',
    'url': 'https://github.com/adamsb6/alert_from_script',
    'packages': ['alert_from_script'],
    'install_requires': [
        'boto>=2.12.0',
    ],
    'entry_points': {
        'console_scripts': ['alert-from-script = alert_from_script:main'],
    },
}

if sys.version_info < (2, 7):
    kwargs['install_requires'].append('argparse==1.2.1')

setup(**kwargs)
