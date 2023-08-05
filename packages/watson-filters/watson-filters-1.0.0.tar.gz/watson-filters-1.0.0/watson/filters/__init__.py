# -*- coding: utf-8 -*-
__version__ = '1.0.0'

try:
    # Fix for setup.py version import
    from watson.filters.string import (Trim, Upper, Lower, RegEx, Numbers,
                                       StripTags, HtmlEntities, Date)

    __all__ = [
        'Trim',
        'Upper',
        'Lower',
        'RegEx',
        'Numbers',
        'StripTags',
        'HtmlEntities',
        'Date']
except:
    pass
