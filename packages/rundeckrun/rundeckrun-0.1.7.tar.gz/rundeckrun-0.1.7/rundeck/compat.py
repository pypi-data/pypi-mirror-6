"""
:summary: Python version compatibility

:license: Creative Commons Attribution-ShareAlike 3.0 Unported
:author: Mark LaPerriere
:contact: rundeckrun@mindmind.com
:copyright: Mark LaPerriere 2013
"""
__docformat__ = "restructuredtext en"

import sys

# for testing string types
StringType = tuple(set([type(''), type(u'')]))  # not sure if this is a good idea, but it works


# maketrans function of string library in 2.x or static method of str type in 3.x
try:
    from string import maketrans
except ImportError:
    # python 3
    maketrans = str.maketrans


# compatible url quoting
try:
    from urllib import quote as url_quote
except ImportError:
    # python 3
    from urllib.parse import quote as url_quote
