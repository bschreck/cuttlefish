# emacs-mode: -*- python-*-
from DisplayDataSource import DisplayDataSource
class LogicalDisplaySegment(object):
    __module__ = __name__
    __doc__ = ' Class representing a specific segment of a display on the controller '

    def adjust_string(original, length):
        """ Brings the string to the given length by either removing characters or adding
        spaces. The algorithm is adopted from ede's old implementation for the Mackie.
    """
        assert (original != None)
        assert (length != None)
        assert (isinstance(original, str) or isinstance(original, unicode))
        assert isinstance(length, int)
        assert (length > 0)
        resulting_string = original
        if (len(resulting_string) < length):
            resulting_string = resulting_string.ljust(length)
        elif (len(resulting_string) > length):
            unit_db = (resulting_string.endswith('dB') and (resulting_string.find('.') != -1))
            if ((len(resulting_string.strip()) > length) and unit_db):
                resulting_string = resulting_string[:-2]
            if (len(resulting_string) > length):
                for um in [' ',
                 'i',
                 'o',
                 'u',
                 'e',
                 'a']:
                    while ((len(resulting_string) > length) and (resulting_string.rfind(um, 1) != -1)):
                        um_pos = resulting_string.rfind(um, 1)
                        resulting_string = (resulting_string[:um_pos] + resulting_string[(um_pos + 1):])


                resulting_string = resulting_string[:length]
        return resulting_string


    adjust_string = staticmethod(adjust_string)

    def __init__(self, width, update_callback):
        assert (update_callback != None)
        assert (width != None)
        assert (dir(update_callback).count('im_func') is 1)
        assert isinstance(width, int)
        object.__init__(self)
        self._update_callback = update_callback
        self._width = width
        self._position_identifier = ()
        self._data_source = None



    def disconnect(self):
        self._update_callback = None
        self._position_identifier = None
        if (self._data_source != None):
            self._data_source.set_update_callback(None)
            self._data_source = None



    def set_data_source(self, data_source):
        assert (data_source != None)
        assert isinstance(data_source, DisplayDataSource)
        if (self._data_source != None):
            self._data_source.set_update_callback(None)
        self._data_source = data_source
        if (self._data_source != None):
            self._data_source.set_update_callback(self.update)



    def set_position_identifier(self, position_identifier):
        assert (position_identifier != None)
        assert isinstance(position_identifier, tuple)
        self._position_identifier = position_identifier



    def position_identifier(self):
        return self._position_identifier



    def update(self):
        self._update_callback()



    def display_string(self):
        resulting_string = (' ' * self._width)
        if (self._data_source != None):
            resulting_string = LogicalDisplaySegment.adjust_string(self._data_source.display_string(), self._width)
        return resulting_string




# local variables:
# tab-width: 4
