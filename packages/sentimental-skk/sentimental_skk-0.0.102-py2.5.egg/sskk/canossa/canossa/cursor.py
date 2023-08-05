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

from attribute import Attribute


class Cursor():

    col = 0
    row = 0
    dirty = True
    attr = None
    __backup = None

    def __init__(self, y=0, x=0, attr=Attribute()):
        self.col = x
        self.row = y
        self.dirty = True
        self.attr = attr
        self.__backup = None

    def clear(self):
        self.col = 0
        self.row = 0
        self.dirty = True
        self.attr.clear()

    def save(self):
        self.__backup = Cursor(self.row, self.col, self.attr.clone())

    def restore(self):
        if self.__backup:
            self.col = self.__backup.col
            self.row = self.__backup.row
            self.attr = self.__backup.attr
            self.__backup = None

    def draw(self, s):
        s.write("\x1b[%d;%dH" % (self.row + 1, self.col + 1))
        self.dirty = False

    def setyx(self, y, x):
        self.row = y
        self.col = x

    def getyx(self):
        return self.row, self.col

    def __str__(self):
        import StringIO
        s = StringIO.StringIO()
        self.draw(s)
        return s.getvalue().replace("\x1b", "<ESC>")


def test():
    """
    >>> cursor = Cursor()
    >>> print cursor
    <ESC>[1;1H
    >>> cursor.clear()
    >>> print cursor
    <ESC>[1;1H
    >>> cursor.setyx(10, 20)
    >>> print cursor
    <ESC>[11;21H
    >>> print cursor.getyx()
    (10, 20)
    >>> cursor.save()
    >>> cursor.setyx(24, 15)
    >>> print cursor
    <ESC>[25;16H
    >>> cursor.clear()
    >>> print cursor
    <ESC>[1;1H
    >>> cursor.restore()
    >>> print cursor
    <ESC>[11;21H
    """
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    test()
