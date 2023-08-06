# -*- coding: utf-8 -*-
__version__ = '1.0.1'

try:
    # Fix for setup.py version import
    from watson.validators.numeric import Range
    from watson.validators.string import Length, Required, RegEx, Csrf

    __all__ = ['Range', 'Length', 'Required', 'RegEx', 'Csrf']
except:  # pragma: no cover
    pass  # pragma: no cover
