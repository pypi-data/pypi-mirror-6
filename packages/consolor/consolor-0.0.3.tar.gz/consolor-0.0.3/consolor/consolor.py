# -*- coding: utf-8 -*-
"""
consolor

Copyright (c) 2013-2014, Friedrich Paetzke (f.paetzke@gmail.com)
All rights reserved.

"""
from __future__ import print_function


_TURN_OFF_CHARACTER_ATTS = '\033[0m'
_TURN_BOLD_MODE_ON = '\033[1m'
_TURN_UNDERLINE_MODE_ON = '\033[4m'
_TURN_BLINKING_MODE_ON = '\033[5m'
_UPDATE_LINE = '\033[2K\r'


class Color:
    Black = '\033[0;30m'
    Red = '\033[0;31m'
    Green = '\033[0;32m'
    Brown = '\033[0;33m'
    Blue = '\033[0;34m'
    Purple = '\033[0;35m'
    Cyan = '\033[0;36m'
    LightGrey = '\033[0;37m'
    DarkGrey = '\033[1;30m'
    LightRed = '\033[1;31m'
    LightGreen = '\033[1;32m'
    Yellow = '\033[1;33m'
    LightBlue = '\033[1;34m'
    LightPurple = '\033[1;35m'
    LightCyan = '\033[1;36m'
    White = '\033[1;37m'
    Reset = _TURN_OFF_CHARACTER_ATTS


class BgColor:
    Black = '\033[40;1m'
    Red = '\033[41;1m'
    Green = '\033[42;1m'
    Brown = '\033[43;1m'
    Blue = '\033[44;1m'
    Purple = '\033[45;1m'
    Cyan = '\033[46;1m'
    Grey = '\033[47;1m'
    Reset = _TURN_OFF_CHARACTER_ATTS


def print_line(s, bold=False, underline=False, blinking=False, color=None, bgcolor=None, end='\n'):
    """
    Prints a string with the given formatting.

    """
    s = get_line(s, bold=bold, underline=underline, blinking=blinking, color=color, bgcolor=bgcolor)
    print(s, end=end)


def get_line(s, bold=False, underline=False, blinking=False, color=None, bgcolor=None,
             update_line=False):
    """
    Returns a string with the given formatting.

    """
    parts = []

    if update_line:
        parts.append(_UPDATE_LINE)

    for val in [bgcolor, color]:
        if val:
            parts.append(val)

    if bold:
        parts.append(_TURN_BOLD_MODE_ON)
    if underline:
        parts.append(_TURN_UNDERLINE_MODE_ON)
    if blinking:
        parts.append(_TURN_BLINKING_MODE_ON)

    parts.append(s)
    parts.append(_TURN_OFF_CHARACTER_ATTS)

    result = ''.join(parts)
    return result


def update_line(s, bold=False, underline=False, blinking=False, color=None, bgcolor=None):
    """
    Overwrites the output of the current line and prints s on the same line
    without a new line.

    """
    s = get_line(s, bold=bold, underline=underline, blinking=blinking, color=color, bgcolor=bgcolor,
                 update_line=True)
    print(s, end='')
