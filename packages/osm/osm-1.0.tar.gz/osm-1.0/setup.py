"""
Optimal Stellar Models (OSM)

Copyright (c) 2012 R. Samadi (LESIA - Observatoire de Paris)

This is a free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
 
This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with this code.  If not, see <http://www.gnu.org/licenses/>.
"""

from distutils.core import setup



setup(name = 'osm',
      version = '1.0',
      description = 'Optimal Stellar Models (OSM): a Python module for calculating optimal stellar models with CESTAM',
      author = 'R. Samadi',
      author_email = 'reza.samadi@obspm.fr',
      url =  'http://lesia.obspm.fr/',
      scripts = ['osm.py','runadipls.pl'],
      py_modules = ['osmlib','osmmodes','osmlevmar'],
      long_description = open('README.txt').read()
      )
