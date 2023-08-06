##------==//
## 
## Copyright (c) 2008-2009 Isaac E. Wagner
## 
## This file is part of Dit 'n Dah
## 
## Dit 'n Dah is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Dit 'n Dah is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with Dit 'n Dah.  If not, see <http://www.gnu.org/licenses/>.
## 
##------==//

##------==//
## 
## Project:	Dit 'n Dah
## 
## File:	setup.py
## Author:	Isaac E. Wagner <isaac@wagnerfam.com>
## 
## 
## TODO:
## 
## BUGS:
## 
## UPDATE INFO:
## Updated on:	18 Dec 2009 02:49:32 UTC
## Updated by:	Isaac E. Wagner <isaac@wagnerfam.com>
## 
##------==//

from distutils.core import setup

setup(name="ditndah",
      version="1.0",
      author="Isaac E. Wagner",
      author_email="isaac@wagnerfam.com",
      description="Dit 'n Dah Python Morse Library",
      license="GPL",
      keywords="morse",
      url="http://sourceforge.net/projects/mrmorse",
      package_dir={'ditndah': 'src'},
      packages=['ditndah'])

