###############################################################################
###############################################################################
#   Copyright 2014 Kyle S. Hickmann and
#                  The Administrators of the Tulane Educational Fund
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
###############################################################################
###############################################################################

import os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	name = 'pyda',
	version = '1.0',
	description = 'pyda is a general object-oriented data assimilation package',
	author = 'Kyle Hickmann',
	author_email = 'khickma@tulane.edu',
	maintainer = 'Kyle Hickmann',
	maintainer_email = 'khickma@tulane.edu',
	url = 'https://hickmank.github.io/pyda',
        long_description = read('README'),
	license = 'Apache 2.0',
	classifiers = [
                'Development Status :: 3 - Alpha',
		'Intended Audience :: Developers',
		'Intended Audience :: Education',
		'Intended Audience :: Science/Research',
                'Topic :: Scientific/Engineering :: Artificial Intelligence',
                'Topic :: Scientific/Engineering :: Information Analysis',
                'Topic :: Scientific/Engineering :: Mathematics',
                'Topic :: Scientific/Engineering :: Physics',
		'Operating System :: Unix',
		'Programming Language :: Python :: 2.7',
                'License :: OSI Approved :: Apache Software License'
		],
	packages = [
		'pyda',
		],
)
