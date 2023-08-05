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

import os

import title
import kanadb
import eisuudb
import dictionary
import word
import settings

from charbuf import CharacterContext
from canossa import Listbox, IListboxListener
from canossa import InnerFrame, IInnerFrameListener
from canossa import IScreenListener
from canossa import IWidget
from canossa import Cursor
from canossa import tff
from canossa import mouse

import codecs
import logging

# マーク
_SKK_MARK_SELECT = u'▼'
_SKK_MARK_OPEN = u'【'
_SKK_MARK_CLOSE = u'】'

homedir = os.path.expanduser("~")
rcdir = os.path.join(homedir, ".sskk")
histdir = os.path.join(rcdir, "history")
if not os.path.exists(histdir):
    os.makedirs(histdir)


class IScreenListenerImpl(IScreenListener):

    def ontitlechanged(self, s):
        title.setoriginal(s)
        self._refleshtitle()
        return None

    def onmodeenabled(self, n):
        return False

    def onmodedisabled(self, n):
        return False


class TitleTrait():

    _counter = 0

    def set_titlemode(self):
        self._counter = 0

    def _getface(self):
        self._counter = 1 - self._counter
        return [u'三 ┗( ^o^)┓ ＜', u'三 ┏( ^o^)┛ ＜ '][self._counter]

    def _refleshtitle(self):
        title.draw(self._output)

    def settitle(self, value):
        face = self._getface()
        title.setmessage(face + value)
        self._refleshtitle()


class IListboxListenerImpl(IListboxListener):

    def oninput(self, listbox, context, c):
        if c == 0x0d:  # CR C-m
            self.onsettled(listbox, context)
        elif c == settings.get('skk-kakutei-key'):  # LF C-j
            self.onsettled(listbox, context)
        elif c == 0x07:  # BEL C-g
            self.oncancel(listbox, context)
        elif c == 0x08 or c == 0x7f:  # C-h BS or DEL
            if self._clauses:
                self._clauses.shift_left()
                candidates = self._clauses.getcandidates()

                listbox.assign(candidates)
            else:
                self.onsettled(listbox, context)
                context.write(c)
        elif c == 0x09:  # TAB C-i
            listbox.movenext()
        elif c == 0x0c:  # LF C-l
            clauses = self._clauses
            if clauses:
                clauses.shift_right()
                candidates = clauses.getcandidates()
                listbox.assign(candidates)
        elif c == 0x0e:  # C-n
            listbox.movenext()
        elif c == 0x16:  # C-v
            listbox.jumpnext()
        elif c == 0x17:  # C-w
            value = self._clauses.getvalue()
            self.open_wikipedia(value)
        elif c == 0x10:  # C-p
            listbox.moveprev()
        elif c == 0x1b:  # ESC C-[
            self.oncancel(listbox, context)
        elif c == 0x02:  # C-b
            return False
        elif c == 0x06:  # C-f
            return False
        elif c < 0x20:  # other control chars
            self.onsettled(listbox, context)
            context.write(c)
        elif c == 0x20:  # SP
            listbox.movenext()
        elif c == 0x78:  # x
            listbox.moveprev()
        elif c <= 0x7e:
            self.onsettled(listbox, context)
            return False
        return True

    def onselected(self, listbox, index, text, remarks):
        if self._clauses:
            self._clauses.getcurrentclause().select(index)
            self._remarks = remarks
            if self._remarks:
                self.settitle(u'%s - %s' % (text, remarks))
            else:
                self.settitle(text)
        elif index >= 0:
            self._remarks = remarks
            self._wordbuf.reset()
            self._wordbuf.startedit()
            self._wordbuf.append(text)
            self._charbuf.reset()

    def onsettled(self, listbox, context):
        self._screen.setfocus()
        if self._clauses:
            self._settle(context)
        if self._wordbuf.length() > 0:
            self._showpopup()

    def oncancel(self, listbox, context):
        if self._clauses:
            listbox.close()
        text = self._clauses.getkey()
        self._clauses = None
        self._inputmode.endabbrev()
        wordbuf = self._wordbuf
        wordbuf.reset()
        wordbuf.startedit()
        wordbuf.append(text + self._okuri)
        self._complete()

    def onrepeat(self, listbox):
        return False


class IInnerFrameListenerImpl(IInnerFrameListener):

    def onclose(self, iframe, context):
        pass


class SkkLineEditor(IWidget):

    def __init__(self, screen):
        self._screen = screen
        self._window = screen.create_window(self)

    def write(self, s):
        self._window.write(s)

    def draw(self, region):
        pass

    def handle_draw(self, context):
        self._window.draw(context)

    def close(self, context):
        self._window.close()


###############################################################################
#
# InputHandler
#
class InputHandler(tff.DefaultHandler,
                   IScreenListenerImpl,
                   IListboxListenerImpl,
                   IInnerFrameListenerImpl,
                   TitleTrait):

    _stack = None
    _prev_length = 0
    _selected_text = None
    _okuri = ""
    _bracket_left = _SKK_MARK_OPEN
    _bracket_right = _SKK_MARK_CLOSE
    _clauses = None
    _iframe = None
    _optimize = False

    def __init__(self, session, screen, termenc, 
                 termprop, mousemode, inputmode):
        self._screen = screen
        try:
            from cStringIO import StringIO
            output = StringIO()
        except ImportError:
            from StringIO import StringIO
            output = StringIO()

        self._mouse_decoder = mouse.MouseDecoder(screen, termprop, mousemode)
        writer = codecs.getwriter(termenc)
        output = writer(output, errors='ignore')
        self._output = output
        self._termenc = termenc
        self._charbuf = CharacterContext()
        self._inputmode = inputmode
        self._wordbuf = word.WordBuffer(termprop)
        self._listbox = Listbox(self, screen, termprop, mousemode, self._mouse_decoder)
        self._termprop = termprop
        self._mousemode = mousemode
        self._stack = []
        self._session = session
        self._screen.setlistener(self)

#        y, x = screen.getyx()
#        self._listbox.setposition(x, y)

        # detects libvte + Ambiguous=narrow environment
        if not termprop.is_cjk and termprop.is_vte():
            pad = u" "
            self._selectmark = _SKK_MARK_SELECT + pad
            self._bracket_left = _SKK_MARK_OPEN + pad
            self._bracket_right = _SKK_MARK_CLOSE + pad
        else:
            self._selectmark = _SKK_MARK_SELECT
            self._bracket_left = _SKK_MARK_OPEN
            self._bracket_right = _SKK_MARK_CLOSE

    def _reset(self):
        self._listbox.close()
        self._inputmode.endabbrev()
        self._wordbuf.reset()
        self._charbuf.reset()
        self._okuri = u""
        self._clauses = None

    def _draincharacters(self):
        charbuf = self._charbuf
        s = charbuf.getbuffer()
        if s == u'n':
            charbuf.put(0x6e)  # n
        s = charbuf.drain()
        return s

    def _iscooking(self):
        if self._clauses:
            return True
        if not self._wordbuf.isempty():
            return True
        if not self._charbuf.isempty():
            return True
        return False

    def _convert_word(self):
        key = self._wordbuf.get()

        if self._inputmode.iskata():
            key = kanadb.to_hira(key)

        result = dictionary.gettango(key)

        self._okuri = u""

        clauses = dictionary.Clauses()
        if len(result) > 5 or key[0] == '@':
            clauses.add(dictionary.Clause(key, result))
        elif not settings.get('cgi-api.enabled'):
            clauses.add(dictionary.Clause(key, [key]))
        elif not dictionary.get_from_cgi_api(clauses, key):
            clauses.add(dictionary.Clause(key, [key]))

        candidates = clauses.getcandidates()
        self._listbox.assign(candidates)
        self._clauses = clauses
        self.settitle(key)
        return True

    def _convert_okuri(self):

        clauses = self._clauses

        buf = self._charbuf.getbuffer()
        if not buf:
            return False
        okuri = self._draincharacters()
        self._okuri = okuri
        buf = buf[0]
        key = self._wordbuf.get()

        if self._inputmode.iskata():
            key = kanadb.to_hira(key)
        result = dictionary.getokuri(key + buf)
        clauses = dictionary.Clauses()
        if result:
            clauses.add(dictionary.Clause(key, result))
        else:
            if self._inputmode.iskata():
                key = kanadb.to_kata(key)
            if not dictionary.get_from_cgi_api(clauses, key):
                clauses.add(dictionary.Clause(key, [key]))
            else:
                self._okuri = u""
            clauses.add(dictionary.Clause(okuri, [okuri]))

        self._clauses = clauses
        self._listbox.assign(clauses.getcandidates())
        self._wordbuf.startedit()

        self.settitle(u'%s - %s' % (key, buf))
        return True

    def _settle(self, context):
        ''' 確定 '''
        clauses = self._clauses
        wordbuf = self._wordbuf
        if clauses:
            key = clauses.getkey()
            remark = clauses.getcurrentremark()
            if key.startswith(u'@') and remark.startswith(u'builtin:'):
                self._dispatch_builtin_command(remark)
                word = u''
            else:
                for clause in clauses:
                    key = clause.getkey()
                    value = clause.getcurrentvalue()
                    dictionary.feedback(key, value)
                word = clauses.getvalue() + self._okuri
            self._clauses = None
            self._okuri = u''
        else:
            s = self._draincharacters()
            word = wordbuf.get()
            if word.startswith(u'@'):
                self._convert_word()
                return
            word += s
            if word.startswith(u'@'):
                word = u''
        if word.startswith('$'):
            command = word[1:]
            self.open_with_command(command)
            word = u''
            return

        title.setmessage(u'＼(^o^)／')
        self._refleshtitle()
        self._listbox.close()
        self._inputmode.endabbrev()
        wordbuf.reset()
        context.putu(word)

        #word_length = self._termprop.wcswidth(word)
        #screen = self._screen
        #y, x = screen.getyx()
        #screen._region.sub(x - word_length, y, word_length, 1)


    def _showpopup(self):
        ''' 次候補 '''
        wordbuf = self._wordbuf
        if wordbuf.has_okuri():
            # 送り有り変換
            self._convert_okuri()
            return
        # 送り無し変換
        s = self._draincharacters()
        wordbuf.append(s)
        self._convert_word()

    def _complete(self):
        charbuf = self._charbuf
        wordbuf = self._wordbuf
        listbox = self._listbox
        key = charbuf.complete()
        completions = wordbuf.suggest(key)
        if completions:
            listbox.assign(completions, -1)

    def _dispatch_builtin_command(self, command):
        self._reset()
        magic, category, key, value = command.split(':')
        if magic == 'builtin':
            if category == 'settings':
                try:
                    value = eval(value)
                except e:
                    logging.exception(e)
                    return False
                if key == 'romanrule':
                    self._charbuf.compile(value)
                elif key == 'use_title':
                    title.setenabled(value)
                settings.set(key, value)
                settings.save()
                return True
            return False
        return False

    def open_wikipedia(self, word):
        import urllib
        url = "http://ja.wikipedia.org/wiki/"
        url += urllib.quote_plus(word.encode('utf-8'))
        command = "w3m '%s'" % url
        self.open_with_command(command)

    def open_with_command(self, command):
        screen = self._screen
        session = self._session
        termprop = self._termprop
        termenc = self._termenc

        height = min(20, int(screen.height * 0.7))
        width = min(60, int(screen.width * 0.7))
        top = int((screen.height - height) / 2)
        left = int((screen.width - width) / 2)

        from mode import InputMode
        inputmode = InputMode(session.tty)
        inputhandler = InputHandler(session,
                                    screen,
                                    termenc,
                                    termprop,
                                    self._mousemode,
                                    inputmode)
        self._iframe = InnerFrame(self._session,
                                  self,
                                  #inputhandler,
                                  self._mouse_decoder,
                                  screen,
                                  top, left, height, width,
                                  command,
                                  termenc,
                                  termprop)

    def destruct_subprocess(self):
        session = self._session
        session.destruct_subprocesses()

    # override
    def handle_char(self, context, c):

        # 0x00 C-SP
        # 0x01 C-a
        # 0x02 C-b
        # 0x03 C-c
        # 0x04 C-d
        # 0x05 C-e
        # 0x06 C-f
        # 0x07 C-g
        # 0x08 BS
        # 0x09 TAB
        # 0x0a C-j
        # 0x0b C-k
        # 0x0c C-l
        # 0x0d CR
        # 0x0e C-n
        # 0x0f C-o
        # 0x10 C-p
        # 0x11 C-q
        # 0x12 C-r
        # 0x13 C-s
        # 0x14 C-t
        # 0x15 C-u
        # 0x16 C-v
        # 0x17 C-w
        # 0x18 C-x
        # 0x19 C-y
        # 0x1a C-z
        # 0x1b ESC
        # 0x1c C-\
        # 0x1d C-]
        # 0x1e C-^
        # 0x1f C-_

        wordbuf = self._wordbuf
        charbuf = self._charbuf
        listbox = self._listbox
        inputmode = self._inputmode
        clauses = self._clauses
        mouse_decoder = self._mouse_decoder

        if not inputmode.getenabled():
            return False

        if mouse_decoder.handle_char(context, c):
            return True

        if clauses and listbox.handle_char(context, c):
            return True

        if inputmode.handle_char(context, c):
            return True

        if charbuf.handle_char(context, c):
            return True

        if c == settings.get('skk-kakutei-key'):  # LF C-j
            if self._iscooking():
                self._settle(context)

        elif c == 0x0d:  # CR C-m
            if self._iscooking():
                self._settle(context)
            else:
                context.write(c)

        elif c == 0x07:  # BEL C-g
            if self._iscooking():
                self._reset()
            else:
                context.write(c)

        elif c == 0x08 or c == 0x7f:  # BS or DEL
            if not charbuf.isempty():
                charbuf.back()
                if not charbuf.getbuffer():
                    listbox.close()
                else:
                    self._complete()
            elif not wordbuf.isempty():
                wordbuf.back()
                if not wordbuf.getbuffer():
                    listbox.close()
                else:
                    self._complete()
            else:
                context.write(c)

        elif c == 0x09:  # TAB C-i
            if not wordbuf.isempty():
                # ワードバッファ編集中
                s = self._draincharacters()
                wordbuf.append(s)
                wordbuf.complete()
                charbuf.reset()
                listbox.movenext()
            else:
                context.write(c)

        elif c == 0x0e:  # C-n
            if listbox.isshown():
                listbox.movenext()
            elif not wordbuf.isempty():
                self._showpopup()
            elif not charbuf.isempty():
                self._showpopup()
            else:
                context.write(c)

        elif c == 0x10:  # C-p
            if listbox.isshown():
                listbox.moveprev()
            elif wordbuf.isempty():
                if charbuf.isempty():
                    context.write(c)

        elif c == settings.get('skk-set-henkan-point-subr'):  # C-q

            if listbox.isshown():
                listbox.close()

            if self._inputmode.isabbrev():
                word = wordbuf.get()
                word = eisuudb.to_zenkaku(word)
                context.putu(word)
                self._inputmode.endabbrev()
                wordbuf.reset()
            elif not wordbuf.isempty():
                s = self._draincharacters()
                word = wordbuf.get()
                str_hankata = kanadb.to_hankata(word + s)
                context.putu(str_hankata)
                wordbuf.reset()
            else:
                context.write(c)

        elif c == 0x17:  # C-w
            if not wordbuf.isempty():
                word = wordbuf.get()
                self.open_wikipedia(word)
            else:
                self._reset()
                context.write(c)

        elif c == 0x1b:  # ESC
            if self._iscooking():
                self._reset()
                self._inputmode.reset()
                context.write(c)
            else:
                context.write(c)

        elif c == 0x20:  # SP
            word = wordbuf.get()
            if word.startswith('$'):
                wordbuf.append(' ')
            elif not wordbuf.isempty():
                s = self._draincharacters()
                wordbuf.append(s)
                if wordbuf.length() > 0:
                    self._showpopup()
            elif not charbuf.isempty():
                s = self._draincharacters()
                wordbuf.startedit()
                wordbuf.append(s)
                if wordbuf.length() > 0:
                    self._settle(context)
            else:
                context.write(c)

        elif c == 0x02:  # C-b
            if not self._moveprevclause():
                context.write(c)

        elif c == 0x06:  # C-f
            if not self._movenextclause():
                context.write(c)

        elif c < 0x20:
            self._reset()
            context.write(c)

        elif c > 0x7f:
            wordbuf.append(unichr(c))

        elif self._inputmode.isabbrev():
            # abbrev mode
            wordbuf.append(unichr(c))
            self._complete()
        elif self._inputmode.ishira() or self._inputmode.iskata():
            # ひらがな変換モード・カタカナ変換モード
            inputmode = self._inputmode
            currentbuffer = charbuf.getbuffer()

            if c == 0x2f and (charbuf.isempty() or currentbuffer != u'z'):  # /
                #
                # / が入力されたとき
                #
                if not self._iscooking():
                    inputmode.startabbrev()
                    wordbuf.reset()
                    wordbuf.startedit()
                    #wordbuf.append(' ')

            elif c == 0x24 and (charbuf.isempty() or currentbuffer != u'z'):  # $
                #
                # $ が入力されたとき
                #
                if not self._iscooking():
                    inputmode.startabbrev()
                    wordbuf.startedit()

            elif c == 0x40 and (charbuf.isempty() or currentbuffer != u'z'):  # @
                #
                # @ が入力されたとき
                #
                wordbuf.append('@')
                self._complete()
                self._inputmode.endabbrev()

            elif c == settings.get('skk-toggle-kana'):  # q
                #
                # q が入力されたとき
                #
                if self._iscooking():
                    s = self._draincharacters()
                    wordbuf.append(s)
                    word = wordbuf.get()
                    self._reset()
                    if inputmode.ishira():
                        s = kanadb.to_kata(word)
                    else:
                        s = kanadb.to_hira(word)
                    context.putu(s)
                else:
                    charbuf.toggle()
                    if inputmode.ishira():
                        inputmode.startkata()
                    elif inputmode.iskata():
                        inputmode.starthira()
                    self._reset()
            elif c == 0x6c and currentbuffer != "z":  # l
                #
                # l が入力されたとき
                #
                if listbox.isshown():
                    self._settle(context)
                inputmode.reset()
                self._reset()
            elif c in (0x2c, 0x2e, 0x3a, 0x5b): # , . : [ ]
#                  c == 0x3b or c == 0x5b or c == 0x5d):  # , . ; : [ ]
                #
                # 区切り文字 ( , . : [ ]) が入力されたとき
                #
                charbuf.reset()
                if listbox.isempty():
                    if not wordbuf.isempty():
                        self._convert_word()
                        charbuf.put(c)
                        s = charbuf.drain()
                        self._okuri += s
                    elif charbuf.put(c):
                        s = charbuf.drain()
                        context.write(ord(s))
                    else:
                        context.write(c)
                else:
                    self._settle(context)
                    if charbuf.put(c):
                        s = charbuf.drain()
                        context.write(ord(s))
                    else:
                        context.write(c)

            elif 0x41 <= c and c <= 0x5a and currentbuffer != "z":
                # A - Z
                # 大文字のとき
                # 先行する入力があるか
                if wordbuf.isempty() or not wordbuf.get():
                    # ない
                    wordbuf.startedit()
                    charbuf.put(c)
                    if charbuf.isfinal():  # 文字バッファに溜める
                        s = charbuf.drain()
                        wordbuf.append(s)
                        self._complete()
                    elif c == 0x4c:  # L
                        if self._iscooking():
                            self._settle(context)
                        self._inputmode.startzen()
                        self._reset()
                    else:
                        self._complete()
                else:
                    # ある
                    s = currentbuffer
                    if s == u'n':
                        charbuf.put(0x6e)  # n
                        s = charbuf.drain()
                        wordbuf.append(s)
                        charbuf.reset()
                    if (not charbuf.put(c)
                            and not charbuf.isfinal()
                            and c == 0x4c):  # L
                        if self._iscooking():
                            self._settle(context)
                        self._inputmode.startzen()
                        self._reset()
                    else:
                        if charbuf.hasnext():
                            s = charbuf.getbuffer()
                            wordbuf.append(s)
                            charbuf.reset()
                            charbuf.put(c)
                        # 先行する入力があるとき、送り仮名マーク('*')をつける
                        wordbuf.startokuri()
                        # キャラクタバッファが終了状態か
                        if charbuf.isfinal():
                            # 送り仮名変換
                            self._convert_okuri()

            #elif (0x61 <= c and c <= 0x7a) or c == 0x2d: # _, a - z, z*
            elif charbuf.put(c):
                # a - z @
                # 小文字のとき
                # 先行する入力があるか
                if wordbuf.isempty():
                    s = charbuf.drain()
                    context.putu(s)
                    if clauses:
                        self._optimize = True
                elif wordbuf.has_okuri():
                    # 送り仮名変換
                    self._convert_okuri()
                else:
                    s = charbuf.drain()
                    wordbuf.append(s)
                    self._complete()
            else:
                wordbuf.append(unichr(c))

        return True  # handled

    def _handle_amb_report(self, context, parameter, intermediate, final):
        if not intermediate:
            if final == 0x57:  # W
                if not parameter:
                    self._termprop.set_amb_as_single()
                elif parameter[0] == 0x32:
                    self._termprop.set_amb_as_double()
                elif parameter[0] == 0x31:
                    self._termprop.set_amb_as_single()
                return True
        return False

    def _movenextclause(self):
        clauses = self._clauses
        if clauses:
            clauses.movenext()
            result = clauses.getcandidates()

            self._listbox.assign(result)

            return True
        return False

    def _moveprevclause(self):
        clauses = self._clauses
        if clauses:
            clauses.moveprev()
            result = clauses.getcandidates()

            self._listbox.assign(result)
            return True
        return False

    def _handle_csi_cursor(self, context, parameter, intermediate, final):
        listbox = self._listbox
        if listbox.isshown():
            if final == 0x43:  # C
                self._movenextclause()
                return True
            elif final == 0x44:  # D
                self._moveprevclause()
                return True
        if final == 0x7e:  # ~
            if parameter and parameter[0] == 0x33 and not intermediate:
                if not self._charbuf.isempty():
                    self._charbuf.back()
                    if not self._charbuf.getbuffer():
                        listbox.close()
                    else:
                        self._complete()
                elif not self._wordbuf.isempty():
                    self._wordbuf.back()
                    if not self._wordbuf.getbuffer():
                        listbox.close()
                    else:
                        self._complete()
                else:
                    return False
            return True
        return False

    def _handle_ss3_cursor(self, context, final):
        if self._listbox.isshown():
            if final == 0x43:  # C
                self._movenextclause()
                return True
            elif final == 0x44:  # D
                self._moveprevclause()
                return True
        return False

    # override
    def handle_csi(self, context, parameter, intermediate, final):
        if not self._inputmode.getenabled():
            return False
        if self._mouse_decoder.handle_csi(context, parameter, intermediate, final):
            return True
        if self._listbox.handle_csi(context, parameter, intermediate, final):
            return True
        if self._handle_csi_cursor(context, parameter, intermediate, final):
            return True
        if self._handle_amb_report(context, parameter, intermediate, final):
            return True
        if not self._wordbuf.isempty():
            return True
        if not self._charbuf.isempty():
            return True
        return False

    def handle_esc(self, context, intermediate, final):
        if not self._inputmode.getenabled():
            return False
        if self._listbox.handle_esc(context, intermediate, final):
            return True
        return False

    def handle_ss3(self, context, final):
        if not self._inputmode.getenabled():
            return False
        if self._listbox.handle_ss3(context, final):
            return True
        if self._handle_ss3_cursor(context, final):
            return True
        if final == 0x5b:  # [
            if self._iscooking():
                self._settle(context)
                self._inputmode.reset()
                self._reset()
            return False
        if not self._wordbuf.isempty():
            return True
        if not self._charbuf.isempty():
            return True
        return False

    def _draw_clauses_with_popup(self, output):
        screen = self._screen
        wcswidth = self._termprop.wcswidth
        listbox = self._listbox
        y, x = screen.getyx()
        cur_width = 0

        clauses = self._clauses
        selected_clause = clauses.getcurrentclause()
        for clause in clauses:
            word = clause.getcurrentvalue()
            if id(clause) == id(selected_clause):
                cur_width += wcswidth(self._selectmark)
                if listbox.is_moved():
                    listbox.set_offset(cur_width, 0)
            cur_width += wcswidth(word)
        if self._okuri:
            cur_width += wcswidth(self._okuri)
        char = self._charbuf.getbuffer()
        cur_width += wcswidth(char)

        if self._prev_length > cur_width:
            length = self._prev_length - cur_width
            if x + cur_width + length < screen.width:
                screen.copyline(output, x + cur_width, y, length)
            else:
                screen.copyline(output, 0, y, screen.width)
                if y + 1 < screen.height:
                    screen.copyline(output, 0, y + 1, screen.width)
        self._prev_length = cur_width

        output.write(u'\x1b[%d;%dH' % (y + 1, x + 1))
        for clause in clauses:
            word = clause.getcurrentvalue()
            if id(clause) == id(selected_clause):
                word = self._selectmark + word
                output.write(u'\x1b[0;1;4;31m')
            else:
                output.write(u'\x1b[0;32m')
            output.write(word)
        if self._okuri:
            output.write(u'\x1b[0;32m' + self._okuri)

    def _draw_word(self, output):
        screen = self._screen
        wcswidth = self._termprop.wcswidth
        listbox = self._listbox
        y, x = screen.getyx()
        cur_width = 0

        word = self._wordbuf.getbuffer()
        char = self._charbuf.getbuffer()

        cur_width += wcswidth(word)
        cur_width += wcswidth(char)

        listbox.setposition(x, y)

        if self._prev_length > cur_width:
            length = self._prev_length - cur_width
            if x + cur_width + length < screen.width:
                screen.copyline(output, x + cur_width, y, length)
            else:
                screen.copyline(output, 0, y, screen.width)
                if y + 1 < screen.height:
                    screen.copyline(output, 0, y + 1, screen.width)
        self._prev_length = cur_width

        output.write(u'\x1b[%d;%dH' % (y + 1, x + 1))
        output.write(u'\x1b[0;1;4;31m' + word)
        output.write(u'\x1b[0;1;32m' + char)

    def _draw_nothing(self, output):
        screen = self._screen
        length = self._prev_length
        if length > 0:
            y, x = screen.getyx()
            if x + length < screen.width:
                screen.copyline(output, x, y, length)
            else:
                screen.copyline(output, 0, y, screen.width)
                if y + 1 < screen.height:
                    screen.copyline(output, 0, y + 1, screen.width)
            output.write('\x1b[%d;%dH' % (y + 1, x + 1))
            self._prev_length = 0

    def handle_resize(self, context, row, col):
        iframe = self._iframe
        try:
            if iframe:
                iframe.close()
        except:
            logging.error("Resize failed")
        finally:
            self._iframe = None

    # override
    def handle_draw(self, context):
        if not self._inputmode.getenabled():
            return False
        output = self._output
        clauses = self._clauses
        iframe = self._iframe
        screen = self._screen
        listbox = self._listbox
        wordbuf = self._wordbuf
        charbuf = self._charbuf

        output.write('\x1b[?25l')

        if self._optimize:
            self._optimize = False
        elif clauses and not listbox.isempty():
            self._draw_clauses_with_popup(output)
        elif not wordbuf.isempty() or not charbuf.isempty():
            self._draw_word(output)
        else:
            self._draw_nothing(output)

        self._refleshtitle()
        screen.cursor.draw(output)

        buf = output.getvalue()
        if buf:
            context.puts(buf)
            output.truncate(0)

        screen.drawwindows(context)

        if not screen.has_active_windows():
            y, x = screen.getyx()
            context.puts('\x1b[%d;%dH' % (y + 1, x + 1))
            if screen.dectcem:
                context.puts('\x1b[?25h')

def test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    test()
