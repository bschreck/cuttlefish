# emacs-mode: -*- python-*-
from ModeSelectorComponent import ModeSelectorComponent
from ControlSurfaceComponent import ControlSurfaceComponent
from ButtonElement import ButtonElement
from InputControlElement import InputControlElement
class ChannelTranslationSelector(ModeSelectorComponent):
    __module__ = __name__
    __doc__ = " Class switches modes by translating the given controls' message channel "

    def __init__(self, num_modes = 0):
        ModeSelectorComponent.__init__(self)
        self._controls_to_translate = None
        self._initial_num_modes = num_modes



    def disconnect(self):
        ModeSelectorComponent.disconnect(self)
        self._controls_to_translate = None



    def set_controls_to_translate(self, controls):
        assert (self._controls_to_translate == None)
        assert (controls != None)
        assert isinstance(controls, tuple)
        for control in controls:
            assert isinstance(control, InputControlElement)

        self._controls_to_translate = controls



    def set_mode_buttons(self, buttons):
        assert (buttons != None)
        assert isinstance(buttons, tuple)
        assert ((len(buttons) - 1) in range(16))
        for button in buttons:
            assert isinstance(button, ButtonElement)
            identify_sender = True
            button.register_value_notification(self._mode_value, identify_sender)
            self._modes_buttons.append(button)

        self.set_mode(0)



    def number_of_modes(self):
        result = self._initial_num_modes
        if ((result == 0) and (self._modes_buttons != None)):
            result = len(self._modes_buttons)
        return result



    def update(self):
        if (self._controls_to_translate != None):
            for control in self._controls_to_translate:
                control.use_default_message()
                if self.is_enabled():
                    control.set_channel(((control.message_channel() + self._mode_index) % 16))

            self._rebuild_callback()




# local variables:
# tab-width: 4
