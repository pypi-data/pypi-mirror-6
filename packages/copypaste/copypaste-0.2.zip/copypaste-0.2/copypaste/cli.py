# -*- coding: utf-8 -*-

"""Copy + Paste support for IronPython.
"""

import clr
clr.AddReference('PresentationCore')
import System.Windows.Clipboard as clipboard

__all__ = (
    'copy',
    'paste',
)


def copy(string):
    """Copy given string into system clipboard.
    """
    clipboard.SetText(string)


def paste():
    """Returns system clipboard contents.
    """
    return clipboard.GetText()
