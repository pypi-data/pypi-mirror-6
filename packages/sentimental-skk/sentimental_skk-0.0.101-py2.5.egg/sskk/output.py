#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ***** BEGIN LICENSE BLOCK *****
# Copyright (C) 2012-2013  Hayaki Saito <user@zuse.jp>
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


from canossa import tff

class OutputHandler(tff.DefaultHandler):

    def __init__(self, screen, mode_handler, 
                 termenc="UTF-8", termprop=None, visibility=False):

        self._screen = screen
        self._mode_handler = mode_handler
        self.dirty_flag = False

    def handle_esc(self, context, intermediate, final):
        return self._mode_handler.handle_esc(context, intermediate, final)

    def handle_csi(self, context, parameter, intermediate, final):
        """
        >>> mode_handler = tff.DefaultHandler()
        >>> from canossa import Screen, termprop
        >>> termprop = termprop.MockTermprop()
        >>> screen = Screen(24, 80, 0, 0, "utf-8", termprop)
        >>> output_handler = OutputHandler(screen, mode_handler)
        """
        if self._mode_handler.handle_csi(context, parameter, intermediate, final):
            return True
        if final == 0x4c or final == 0x4d or final == 0x53 or final == 0x54:
            if not intermediate:
                if self._screen.has_visible_windows():
                    self.dirty_flag = True
        return False

    def handle_char(self, context, c):
        if c == 0x0a:  # LF
            screen = self._screen
            if screen.cursor.row == screen.scroll_bottom - 1:
                if screen.has_visible_windows():
                    self.dirty_flag = True
        return False

    def handle_draw(self, context):
        if self.dirty_flag:
            self.dirty_flag = False
            screen = self._screen
            screen.drawall(context)
            screen.drawwindows(context)

        return False

def test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    test()
