#!/usr/bin/python
# -*- coding: utf-8 -*-
# This file is part of pydsl.
#
# pydsl is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
# pydsl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pydsl.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Nestor Arocha"
__copyright__ = "Copyright 2008-2013, Nestor Arocha"
__email__ = "nesaro@gmail.com"

"""Parser expression grammars

Loosely based on pymeta

https://launchpad.net/pymeta

"""

from .Definition import Grammar

class Many(Grammar):
    def __init__(self, element):
        Grammar.__init__(self)
        self.element = element

#Choice is equivalent to Alphabet 

class Sequence(Grammar, list):
    def __init__(self, *args, **kwargs):
        base_alphabet = kwargs.pop('base_alphabet', None)
        Grammar.__init__(self, base_alphabet)
        list.__init__(self, *args, **kwargs)

class Not(Grammar, list):
    def __init__(self, element):
        Grammar.__init__(self)
        self.element = element

from pydsl.Alphabet import GrammarCollection

class Choice(GrammarCollection, Grammar):
    """Uses a list of grammar definitions with common base alphabets"""
    def __init__(self, grammarlist):
        GrammarCollection.__init__(self, grammarlist)
        base_alphabet_list = []
        for x in self:
            if not isinstance(x, Grammar):
                raise TypeError("Expected Grammar, Got %s:%s" % (x.__class__.__name__,x))
            if x.alphabet not in base_alphabet_list:
                base_alphabet_list.append(x.alphabet)
        if len(base_alphabet_list) != 1:
            raise ValueError('Different base alphabets from members %s' % base_alphabet_list)
        Grammar.__init__(self, base_alphabet_list[0])

    def __str__(self):
        return str([str(x) for x in self])

    def __add__(self, other):
        return Choice(GrammarCollection.__add__(self,other))

