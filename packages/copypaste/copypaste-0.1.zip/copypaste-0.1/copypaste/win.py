# -*- coding: utf-8 -*-

"""Copy + Paste support for Windows.
"""

import win32clipboard

__all__ = (
    'copy',
    'paste',
)


def copy(string):
    """Copy given string into system clipboard.
    """
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(string)
    win32clipboard.CloseClipboard()


def paste():
    """Returns system clipboard contents.
    """
    win32clipboard.OpenClipboard()
    text = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()
    return text
