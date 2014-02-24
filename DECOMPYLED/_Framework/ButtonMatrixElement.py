# emacs-mode: -*- python-*-
from NotifyingControlElement import NotifyingControlElement
from ButtonElement import ButtonElement
class ButtonMatrixElement(NotifyingControlElement):
    __module__ = __name__
    __doc__ = ' Class representing a 2-dimensional set of buttons '

    def __init__(self):
        NotifyingControlElement.__init__(self)
        self._buttons = []
        self._button_coordinates = {}
        self._max_row_width = 0



    def disconnect(self):
        NotifyingControlElement.disconnect(self)
        self._buttons = None
        self._button_coordinates = None



    def add_row(self, buttons):
        assert (buttons != None)
        assert isinstance(buttons, tuple)
        index = 0
        for button in buttons:
            assert (button != None)
            assert isinstance(button, ButtonElement)
            assert (not (button in self._button_coordinates.keys()))
            button.register_value_notification(self._button_value, identify_sender=True)
            self._button_coordinates[button] = (index,
             len(self._buttons))
            index += 1

        if (self._max_row_width < len(buttons)):
            self._max_row_width = len(buttons)
        self._buttons.append(buttons)



    def width(self):
        return self._max_row_width



    def height(self):
        return len(self._buttons)



    def send_value(self, column, row, value):
        assert (value in range(128))
        assert (column in range(self.width()))
        assert (row in range(self.height()))
        if (len(self._buttons[row]) > column):
            button = self._buttons[row][column]
            button.send_value(value)



    def reset(self):
        for button_row in self._buttons:
            for button in button_row:
                button.reset()





    def _button_value(self, value, sender):
        assert isinstance(value, int)
        assert (sender in self._button_coordinates.keys())
        assert isinstance(self._button_coordinates[sender], tuple)
        coordinates = tuple(self._button_coordinates[sender])
        for entry in self._value_notifications:
            callback = entry['Callback']
            callback(value, coordinates[0], coordinates[1], sender.is_momentary())





# local variables:
# tab-width: 4
