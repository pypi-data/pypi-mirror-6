#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ***** BEGIN LICENSE BLOCK *****
# Copyright (C) 2012  Hayaki Saito <user@zuse.jp>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ***** END LICENSE BLOCK *****

from cell import Cell

_LINE_TYPE_DHLT = 3
_LINE_TYPE_DHLB = 4
_LINE_TYPE_SWL  = 5
_LINE_TYPE_DWL  = 6

'''
    This module exports Line object, that consists of some cell objects.

       +-----+-----+-----+-...                   ...-+-----+
       |  A  |  B  |  C  |       ... ... ...         |     |
       +-----+-----+-----+-...                   ...-+-----+

    Ordinally, each cell contains a narrow character

    A wide character occupies 2 cells, the first cell contains '\0'

       +----+---------+-----+-...                   ...-+-----+
       | \0 | \x3042  |  C  |       ... ... ...         |     |
       +----+---------+-----+-...                   ...-+-----+
        <------------> <--->
         a wide char   char
'''

class SupportsDoubleSizedTrait():
    ''' For DECDWL/DECDHL support
    '''

    _type = _LINE_TYPE_SWL

    def set_swl(self):
        '''
        >>> line = Line(5)
        >>> line.set_swl()
        >>> line.type() == _LINE_TYPE_SWL
        True
        '''
        self._type = _LINE_TYPE_SWL
        self.dirty = True

    def set_dwl(self):
        '''
        >>> line = Line(5)
        >>> line.set_dwl()
        >>> line.type() == _LINE_TYPE_DWL
        True
        '''
        self._type = _LINE_TYPE_DWL
        self.dirty = True

    def set_dhlt(self):
        '''
        >>> line = Line(5)
        >>> line.set_dhlt()
        >>> line.type() == _LINE_TYPE_DHLT
        True
        '''
        self._type = _LINE_TYPE_DHLT
        self.dirty = True

    def set_dhlb(self):
        '''
        >>> line = Line(5)
        >>> line.set_dhlb()
        >>> line.type() == _LINE_TYPE_DHLB
        True
        '''
        self._type = _LINE_TYPE_DHLB
        self.dirty = True

    def is_normal(self):
        return self._type == _LINE_TYPE_SWL

    def type(self):
        '''
        >>> line = Line(5)
        >>> line.type() == _LINE_TYPE_SWL
        True
        '''
        return self._type

class SupportsWideTrait():
    ''' provides pad method. it makes the cell at specified position contain '\0'. '''

    def pad(self, pos):
        cell = self.cells[pos]
        cell.pad()

class SupportsCombiningTrait():
    ''' provides combine method. it combines specified character to the cell at specified position. '''

    def combine(self, value, pos):
        '''
        >>> from attribute import Attribute
        >>> line = Line(5)
        >>> attr = Attribute()
        >>> line.clear(attr._attrvalue)
        >>> line.write(0x40, 1, attr)
        >>> line.combine(0x300, 2)
        >>> print line
        <ESC>[0;39;49m<SP>@̀<SP><SP><SP>
        '''
        self.cells[max(0, pos - 1)].combine(value)

class Line(SupportsDoubleSizedTrait,
           SupportsWideTrait,
           SupportsCombiningTrait):

    def __init__(self, width):
        '''
        >>> line = Line(10)
        >>> len(line.cells)
        10
        >>> line.dirty
        True
        '''
        self.cells = [Cell() for cell in xrange(0, width)]
        self.dirty = True

    def length(self):
        '''
        >>> line = Line(19)
        >>> line.length()
        19
        '''
        return len(self.cells)

    def resize(self, col):
        '''
        >>> line = Line(14)
        >>> line.length()
        14
        >>> line.resize(9)
        >>> line.length()
        9
        >>> line.resize(0)
        >>> line.length()
        0
        >>> line.resize(20)
        >>> line.length()
        20
        '''
        width = len(self.cells)
        if col < width:
            self.cells = self.cells[:col]
        elif col > width:
            self.cells += [Cell() for cell in xrange(0, col - width)]
        self.dirty = True

    def clear(self, attrvalue):
        '''
        >>> from attribute import Attribute
        >>> line = Line(5)
        >>> line.clear(Attribute()._attrvalue)
        >>> print line
        <ESC>[0;39;49m<SP><SP><SP><SP><SP>
        '''
        if not self.dirty:
            self.dirty = True
        self.set_swl()
        for cell in self.cells:
            cell.clear(attrvalue)

    def write(self, value, pos, attr):
        '''
        >>> from attribute import Attribute
        >>> line = Line(5)
        >>> attr = Attribute()
        >>> line.clear(attr._attrvalue)
        >>> line.write(0x40, 0, attr)
        >>> print line
        <ESC>[0;39;49m@<SP><SP><SP><SP>
        >>> line.write(0x50, 0, attr)
        >>> print line
        <ESC>[0;39;49mP<SP><SP><SP><SP>
        >>> line.write(0x3042, 1, attr)
        >>> print line
        <ESC>[0;39;49mPあ<SP><SP><SP>
        '''
        if not self.dirty:
            self.dirty = True
        self.cells[pos].write(value, attr)

    def drawrange(self, s, left, right, cursor, lazy=False):
        '''
        >>> line = Line(5)
        >>> import StringIO
        >>> s = StringIO.StringIO()
        >>> from cursor import Cursor
        >>> line.drawrange(s, 3, 5, Cursor())
        >>> result = s.getvalue().replace("\x1b", "<ESC>")
        >>> result = result.replace("\x20", "<SP>")
        >>> print result
        <ESC>[0;39;49m<SP><SP>
        '''
        cells = self.cells
        attr = cursor.attr
        attr.draw(s)
        c = None
        if left > 0:
            cell = cells[left - 1]
            c = cell.get()
            if c is None:
                if False and lazy:
                    s.write(' ')
                    left += 1
                else:
                    s.write(u'\x08') # BS

        for cell in cells[left:right]:
            c = cell.get()
            if not c is None:
                if not attr.equals(cell.attr):
                    cell.attr.draw(s, attr)
                    attr.copyfrom(cell.attr)
                s.write(c)

        if not lazy:
            if c is None:
                for cell in cells[right:]:
                    c = cell.get()
                    if not c is None:
                        if not attr.equals(cell.attr):
                            cell.attr.draw(s, attr)
                            attr.copyfrom(cell.attr)
                        s.write(c)
                        break

    def drawall(self, s, cursor):
        self.dirty = False
        cells = self.cells
        s.write(u"\x1b#%d" % self._type)
        attr = cursor.attr
        attr.draw(s)
        c = None
        for cell in cells:
            c = cell.get()
            if not c is None:
                if not attr.equals(cell.attr):
                    cell.attr.draw(s, attr)
                    attr.copyfrom(cell.attr)
                s.write(c)
        if c is None:
            for cell in cells[right:]:
                c = cell.get()
                if not c is None:
                    if not attr.equals(cell.attr):
                        cell.attr.draw(s, attr)
                        attr.copyfrom(cell.attr)
                    s.write(c)
                    break

    def __str__(self):
        '''
        >>> line = Line(5)
        >>> print line
        <ESC>[0;39;49m<SP><SP><SP><SP><SP>
        '''
        import StringIO, codecs
        import locale
        from cursor import Cursor
        language, encoding = locale.getdefaultlocale()
        cursor = Cursor()
        s = codecs.getwriter(encoding)(StringIO.StringIO())
        self.drawrange(s, 0, len(self.cells), cursor)
        result = s.getvalue().replace("\x1b", "<ESC>")
        result = result.replace("\x20", "<SP>")
        result = result.replace("\x00", "<NUL>")
        return result

def test():
    """
    >>> from attribute import Attribute
    >>> line = Line(10)
    >>> attr = Attribute()
    >>> print line
    <ESC>[0;39;49m<SP><SP><SP><SP><SP><SP><SP><SP><SP><SP>
    >>> line.clear(attr._attrvalue)
    >>> print line
    <ESC>[0;39;49m<SP><SP><SP><SP><SP><SP><SP><SP><SP><SP>
    >>> line.write(0x40, 0, attr)
    >>> line.write(0x50, 0, attr)
    >>> print line
    <ESC>[0;39;49mP<SP><SP><SP><SP><SP><SP><SP><SP><SP>
    >>> line.write(0x40, 1, attr)
    >>> print line
    <ESC>[0;39;49mP@<SP><SP><SP><SP><SP><SP><SP><SP>
    >>> line.pad(2)
    >>> line.write(0x3042, 3, attr)
    >>> print line
    <ESC>[0;39;49mP@あ<SP><SP><SP><SP><SP><SP>
    >>> line.write(0x30, 5, attr)
    >>> print line
    <ESC>[0;39;49mP@あ<SP>0<SP><SP><SP><SP>
    """
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    test()

