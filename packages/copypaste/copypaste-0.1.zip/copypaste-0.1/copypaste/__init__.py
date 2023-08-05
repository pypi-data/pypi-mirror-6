# -*- coding: utf-8 -*-

import sys

__all__ = (
    'copy',
    'paste',
)


platform = sys.platform
if platform in ('darwin',) or platform.startswith('linux'):
    from copypaste.unix import *
elif platform == 'win32':
    from copypaste.win import *
elif platform == 'cli':
    from copypaste.cli import *
else:
    raise NotImplementedError
