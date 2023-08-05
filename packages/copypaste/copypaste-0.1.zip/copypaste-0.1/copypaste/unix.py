# -*- coding: utf-8 -*-

"""Copy + Paste support for UNIX like systems.
"""

import sys
from subprocess import Popen, PIPE

__all__ = (
    'copy',
    'paste',
)


platform = sys.platform
if platform == 'darwin':
    copy_cmd = ['pbcopy']
    paste_cmd = ['pbpaste']
else:
    copy_cmd = ['xclip', '-selection', 'clipboard']
    paste_cmd = ['xclip', '-selection', 'clipboard', '-o']


def copy(string, cmd=copy_cmd, stdin=PIPE):
    """Copy given string into system clipboard.
    """
    Popen(cmd, stdin=stdin).communicate(string.encode('utf-8'))


def paste(cmd=paste_cmd, stdout=PIPE):
    """Returns system clipboard contents.
    """
    return Popen(cmd, stdout=stdout).communicate()[0].decode('utf-8')
