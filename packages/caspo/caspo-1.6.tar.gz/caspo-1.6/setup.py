# Copyright (c) 2012-2013, Santiago Videla, Sven Thiele, CNRS, INRIA, EMBL
#
# This file is part of caspo.
#
# caspo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# caspo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with caspo.  If not, see <http://www.gnu.org/licenses/>.import random
# -*- coding: utf-8 -*-
from setuptools import setup
                         
setup(name='caspo',
      version='1.6',
      url='http://caspo.genouest.org/',
      license='GPLv3',
      description='Reasoning on the response of logical signaling networks with Answer Set Programming',
      long_description=open('README.txt').read() + open('CHANGES.txt').read(),
      author='Sven Thiele, Santiago Videla',
      author_email='santiago.videla@irisa.fr',
      packages = ['__caspo__'],
      package_dir = {'__caspo__' : 'src'},
      package_data = {'__caspo__' : ['query/*.lp']},
      scripts = ['caspo-learn.py', 'caspo-control.py'],
      install_requires=[
        "cellnopt.wrapper==1.0.5",
        "pyasp>=1.2"
      ]
)
