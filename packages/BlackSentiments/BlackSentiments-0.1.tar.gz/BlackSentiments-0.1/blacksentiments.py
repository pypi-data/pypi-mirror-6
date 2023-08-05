#!/usr/bin/env python
# coding: utf-8
"""
Fast sentiment analysis for the Black Speech of Mordor as given in the works of
J. R. R. Tolkien in his Middle-earth mythos.  Works for both the ancient mode
of Black Speech as used by Sauron and the Nazgûl, and the 'debased' Orkish form
used by the soldiery.

Example usage:

    >>> black_speech = "Ash nazg durbatulûk, ash nazg gimbatul, ash nazg thrakatulûk agh burzum-ishi krimpatul."
    >>> classify(black_speech)
    'neg'
    >>> debased_black_speech = "Uglúk u bagronk sha pushdug Saruman-glob búbhoshskai"
    >>> classify(debased_black_speech)
    'neg'

Robustness has been sacrificed for speed, and so it is to be noted that the
classifier is, being so specialised, likely to return spurious results if it is
fed non-Black Speech text.  I leave the determining of the input string as
genuine Black Speech as an exercise for the interested.

                        *    *    *

Copyright 2013 Stephen B. Murray

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

__author__ = "Stephen B. Murray <sbm199@gmail.com>"
__copyright__ = "Copyright 2013 Stephen B. Murray"
__version__ = "0.1"

def classify(text):
    """
    Return str indicating sentiment of given text representing
    Black Speech/Orkish.
    """
    return "neg"

if __name__ == "__main__":
    import doctest
    doctest.testmod()
