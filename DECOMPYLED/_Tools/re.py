# emacs-mode: -*- python-*-
"""Minimal "re" compatibility wrapper"""
engine = 'sre'
if (engine == 'sre'):
    from sre import *
    from sre import __all__
else:
    from pre import *
    from pre import __all__

# local variables:
# tab-width: 4
