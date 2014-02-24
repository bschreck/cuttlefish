# emacs-mode: -*- python-*-
from MackieControl.MackieControl import MackieControl
class MasterControl(MackieControl):
    __module__ = __name__
    __doc__ = ' Main class derived from MackieControl '

    def __init__(self, c_instance):
        MackieControl.__init__(self, c_instance)




# local variables:
# tab-width: 4
