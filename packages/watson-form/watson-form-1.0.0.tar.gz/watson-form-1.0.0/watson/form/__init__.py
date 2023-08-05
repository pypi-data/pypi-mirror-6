# -*- coding: utf-8 -*-
__version__ = '1.0.0'

try:
    # Fix for setup.py version import
    from watson.form.types import Form, Multipart

    __all__ = ['Form', 'Multipart']
except:
    pass
