# emacs-mode: -*- python-*-
import Live
from ControlSurfaceComponent import ControlSurfaceComponent
from ButtonElement import ButtonElement
class ModeSelectorComponent(ControlSurfaceComponent):
    __module__ = __name__
    __doc__ = ' Class for switching between modes, handle several functions with few controls '

    def __init__(self):
        ControlSurfaceComponent.__init__(self)
        self._modes_buttons = []
        self._mode_toggle = None
        self._mode_index = -1



    def disconnect(self):
        if (self._mode_toggle != None):
            self._mode_toggle.unregister_value_notification(self._toggle_value)
            self._mode_toggle = None
        self._modes_buttons = None



    def on_enabled_changed(self):
        self.update()



    def set_mode_toggle(self, button):
        assert ((button == None) or isinstance(button, ButtonElement))
        if (self._mode_toggle != None):
            self._mode_toggle.unregister_value_notification(self._toggle_value)
        self._mode_toggle = button
        if (self._mode_toggle != None):
            self._mode_toggle.register_value_notification(self._toggle_value)



    def set_mode(self, mode):
        assert isinstance(mode, int)
        assert (mode in range(self.number_of_modes()))
        if (self._mode_index != mode):
            self._mode_index = mode
            self.update()



    def number_of_modes(self):
        debug_print('number_of_modes is abstract. Forgot to override it?')
        assert False



    def update(self):
        debug_print('update is abstract. Forgot to override it?')
        assert False



    def _mode_value(self, value, sender):
        assert (len(self._modes_buttons) > 0)
        assert isinstance(value, int)
        assert isinstance(sender, ButtonElement)
        assert (self._modes_buttons.count(sender) == 1)
        if ((value is not 0) or (not sender.is_momentary())):
            self.set_mode(self._modes_buttons.index(sender))



    def _toggle_value(self, value):
        assert (self._mode_toggle != None)
        assert isinstance(value, int)
        if ((value is not 0) or (not self._mode_toggle.is_momentary())):
            self.set_mode(((self._mode_index + 1) % self.number_of_modes()))




# local variables:
# tab-width: 4
