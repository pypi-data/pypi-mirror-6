#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Nesli Erdogmus <Nesli.Erdogmus@idiap.ch>
# @date: Tue Jun 18 09:53:56 CET 2013
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

setup(

    name='estimate.gender',
    version='0.2',
    description='Gender estimation on several databases',

    #url='http://github.com/idiap/bob.project.example',
    license='GPLv3',
    author='Nesli Erdogmus',
    author_email='nesli.erdogmus@idiap.ch',

    long_description=open('README.rst').read(),

    packages=find_packages(),
    include_package_data=True,

    install_requires=[
      'setuptools',
      'bob', # base signal proc./machine learning library
      'xbob.db.banca',
      'xbob.db.mobio',
      'xbob.db.verification.filelist',
    ],

    namespace_packages = [
      'estimate',
    ],

    entry_points={
      'console_scripts': [
        'estimateGender.py = estimate.gender.estimateGender:main',
        'test_all.py = estimate.gender.test_all:main',
        'rank_all.py = estimate.gender.rank_all:main'
        ],

      'bob.test': [
         'example = xbob.example.test:MyTests',
         ],
    },
)
