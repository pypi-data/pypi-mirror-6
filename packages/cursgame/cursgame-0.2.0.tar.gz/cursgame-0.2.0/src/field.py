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

"""Contains the Field class

This module cotains the Field class. This class is used to hold te
objects on one position on the map. Its API is much like a stack.

"""

from .color import WHITE


class Field(list):
    """Holds objects on a field

    On every coordinate of the map is a Field instance.
    It holds the objects on the corresponding coordinate.
    It can be handled like a list.

    """
    def __init__(self, x, y, defstr=chr(183)):
        self.x, self.y = x, y
        self.defstr = defstr

    def uppest(self):
        """Returns the visible object of the field

        In most cases this is just field[-1].
        Returns None if the field is empty.

        """
        try:
            upper = self[-1]
        except IndexError:
            return None
        else:
            return upper

    def __str__(self):
        """Provides a basic look for empty fields"""
        try:
            upper = self[-1]
        except IndexError:
            return self.defstr
        else:
            return str(upper)

    def color(self):
        """Provides a generic color for empty fields"""
        try:
            upper = self[-1]
        except IndexError:
            return WHITE
        else:
            return upper.color()

    def __repr__(self):
        return "Field({0})".format(super().__repr__())
