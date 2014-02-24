# emacs-mode: -*- python-*-
class DisplayDataSource(object):
    __module__ = __name__
    __doc__ = ' Data object that is fed with a specific string and notifies its observers '

    def __init__(self):
        object.__init__(self)
        self._display_string = ''
        self._update_callback = None



    def set_update_callback(self, update_callback):
        assert ((update_callback == None) or (dir(update_callback).count('im_func') is 1))
        self._update_callback = update_callback



    def set_display_string(self, new_string):
        assert (new_string != None)
        assert (isinstance(new_string, str) or isinstance(new_string, unicode))
        if (self._display_string != new_string):
            self._display_string = new_string
            self.update()



    def update(self):
        if (self._update_callback != None):
            self._update_callback()



    def display_string(self):
        return self._display_string




# local variables:
# tab-width: 4
