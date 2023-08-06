# Copyright 2013 Sven Bartscher
#
# Licensed under the EUPL, Version 1.1 or – as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
#
# http://ec.europa.eu/idabc/eupl
#
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.

#This file is part of cursgame 0.2.0

"""Provides input facilities

This module contains all stuff needed to get and process input. The
core of this module is the InputHandler. It processes Input and takes
needed actions.

"""

import time
from collections import defaultdict
import curses


def nothing(*args, **kwargs):
    """Takes a arbitrary amount of arguments and return None"""
    pass


class InputHandler:
    """Maps input actions to functions

    The InputHandler waits for input and calls functions depending on
    handler.callbacks. If handler.callbacks looks like this:
    handler.callbacks == {ord('q'): game.log_write('Q!')
    Then "Q!" is written to the log every time q is pressed.

    """
    def __init__(self, blocking):
        self.callbacks = defaultdict(lambda: nothing)
        self._screen = None
        self.blocking = blocking

    @property
    def blocking(self):
        return self._blocking

    @blocking.setter
    def blocking(self, value):
        if self._screen:
            self._screen.nodelay(bool(value))
        self._blocking = value

    @property
    def screen(self):
        """The screen

        This is the screen the handler is listening on for input

        """
        if not self._screen:
            raise RuntimeError("{0} isn't initialized!".format(self))
        return self._screen

    @screen.setter
    def screen(self, value):
        self._screen = value
        try:
            value.nodelay(bool(self.blocking))
        except NameError:
            raise TypeError("screen must be a valid screen object!")

    @screen.deleter
    def screen(self):
        self._screen = None

    def get_input(self):
        """Get input from screen and call callbacks

        The actions which are taken depend on handler.callbacks.
        callbacks is a dictionary mapping of unicode-codes to functions.
        The inp module also contains all the key-constants defined by
        curses. These can be used as keys in handler.callbacks either.

        """
        if self.blocking:
            time.sleep(self.blocking)
        try:
            inp = self.screen.getch()
        except curses.error:
            pass
        else:
            self.callbacks[inp](inp)


class PassiveInput(InputHandler):
    def __init__(self, blocking):
        """We don't need as much initialisation as InputHandler

        This function initializes the PassiveInput in a way like the
        InputHandler, leaving out the stuff that isn't needed for PassiveInput.

        """
        self._screen = None
        self.blocking = blocking

    def get_input(self):
        """This method does nothing

        Since the passive input just replaces the original
        InputHandler this method does nothing. But it is needed to
        make the game continue imediately.

        """
        pass

    def get_key(self):
        """Request input manually.

        May return -1 if blocking is 0 (or false) and no key was pressed.
        Note that this method is not like get_input of the InputHandler waiting
        the time specified in blocking.

        """
        return self.screen.getch()


#Get all key constants from curses
do = globals()
dc = curses.__dict__
for symbol, value in dc.items():
    if symbol.startswith('KEY_'):
        do[symbol] = value
del do, dc
