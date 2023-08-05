#!/usr/bin/env python

import sys
import os
import platform
import cexbot

try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

if getattr(sys, 'version_info', (0, 0, 0)) < (2, 5, 0, 'final'):
    raise SystemExit("cexbot requires Python 2.5 or later.")

if sys.argv[-1] == 'publish':
  os.system('python setup.py sdist upload')
  sys.exit()

scripts = ['cexbot-cli']
if os.name == 'nt':
  scripts.append('bin/cexbot-cli.bat')

packages = [
  'requests',
  'semantic_version',
]

APP = ['cexbot/main.py']
DATA_FILES = ['cexbot-cli']
OPTIONS = {'argv_emulation': True}

package_dir = os.path.realpath(os.path.dirname(__file__))

def get_file_contents(file_path):
  """Get the context of the file using full path name"""
  full_path = os.path.join(package_dir, file_path)
  return open(full_path, 'r').read()

setup(
  name = 'cexbot',
  description = cexbot.__doc__.split('\n\n')[0],
  long_description = get_file_contents('README.md'),
  keywords = 'cexbot, bitcoin, finance',
  url = 'https://github.com/nikcub/cexbot',
  platforms = ['linux', 'osx'],
  version = cexbot.get_version(),
  author = 'Nik Cubrilovic',
  author_email = 'nikcub@gmail.com',
  license = get_file_contents('LICENSE'),
  install_requires = packages,
  packages = ['cexbot'],
  app=APP,
  data_files=DATA_FILES,
  options={'py2app': OPTIONS},
  setup_requires=['py2app'],
  scripts = scripts,
  # entry_points={
  #   'console_scripts': [
  #     "cexbot-cli = cexbot.command_utils:run_cl"
  #   ],
    # 'gui_scripts': [
      # "cexbot-gui = cexbot.command_utils:run_gui"
    # ]
  # },
)