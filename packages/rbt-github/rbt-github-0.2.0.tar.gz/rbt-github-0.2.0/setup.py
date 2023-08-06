#!/usr/bin/env python
#
# Copyright 2014 
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
try:
    from setuptools import setup, find_packages
except ImportError:
    # setuptools was unavailable. Install it then try again
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(name='rbt-github',
  version='0.2.0',
  license='Apache v2',
  description='Reviewboard github extension',
  entry_points={
    'rbtools_commands': [
        'github = rbt_github.command:Github',
    ],
  },
  install_requires=[
    'rbtools>=0.5.5',
  ],
  packages=find_packages(),
  maintainer='Jake Farrell',
  maintainer_email='jfarrell@apache.org',
  url='http://github.com/jfarrell',
  classifiers=[
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development',
])
