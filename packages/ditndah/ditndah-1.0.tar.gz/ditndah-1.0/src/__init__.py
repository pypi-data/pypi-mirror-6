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
## File:	__init__.py
## Author:	Isaac E. Wagner <isaac@wagnerfam.com>
## 
## 
## TODO:
## 
## BUGS:
## 
## UPDATE INFO:
## Updated on:	18 Dec 2009 02:53:00 UTC
## Updated by:	Isaac E. Wagner <isaac@wagnerfam.com>
## 
##------==//

"""
This is the Dit 'n Dah Python Morse code library.  The name
comes from the sound of Morse code characters.

Simple library usage::

  import ditndah
  m = ditndah.MorseGen()
  data = m.textToAudioData("Hello World")
  <send data to sound card>

The above would use the default values to generate raw audio data.  The
raw data generated above could be output to a sound card using a suitable
library, or dumped to a wav file if the appropriate header information
was added to the data.

Morse complex example::
  import ditndah
  m = ditndah.MorseGen(pitch=700,
                       sampleRate=8000,
                       wpm=5,
                       fwpm=13,
                       format=ditndah.FORMAT_S16LE,
                       numChannels=2)
  m.textToWavFile("Four score and seven years ago...",
                  "/some/directory/output.wav")

Note that all the important classes, methods, and constants are imported
into the base package for you.  So, you don't need to explicitly import
ditndah.constants for example.

All of the standard Morse alphanumeric characters are included.  In addition,
the following characters are also supported::
    '.' (period)
    ',' (comma)
    '?' (question)
    '-' (hyphen)
    '/' (slash)
    '"' (quote)
    '@' (the "AT" sign used in emails)

For prosigns you encode them like: <XX>.  For example::
    <AR>
    <SK>
    etc.

Actually, the logic used in the program allows you to run together arbitrary
characters.  So, while it might not make sense if you really wanted to you
could send some character like <3@>, which would end up being sent as a single
"character" of '...--.--.-.'  Like I said, not really useful but allowing
arbitrary two character prosigns was the easiest to program. :)

@author: Isaac E. Wagner
@copyright: This library is released under the GPL version 3. A copy of the
            license can be found in the source distribution.
"""

from excepts import *
from constants import MORSE_TABLE, FORMAT_S8, FORMAT_U8, FORMAT_S16BE, FORMAT_S16LE, FORMAT_U16BE, FORMAT_U16LE
from morselib import MorseGen
from morsestream import MorseStream
