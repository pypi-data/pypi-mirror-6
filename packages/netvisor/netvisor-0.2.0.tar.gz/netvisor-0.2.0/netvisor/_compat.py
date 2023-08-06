# -*- coding: utf-8 -*-
"""
    netvisor._compat
    ~~~~~~~~~~~~~~~~

    :copyright: (c) 2013-2014 by Fast Monkeys Oy.
    :license: MIT, see LICENSE for more details.
"""
import sys

PY2 = sys.version_info[0] == 2


if not PY2:
    text_type = str
else:
    text_type = unicode
