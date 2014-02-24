# emacs-mode: -*- python-*-
import Live
from ControlSurfaceComponent import ControlSurfaceComponent
from ButtonElement import ButtonElement
class ClipSlotComponent(ControlSurfaceComponent):
    __module__ = __name__
    __doc__ = ' Class representing a ClipSlot within Live '

    def __init__(self):
        ControlSurfaceComponent.__init__(self)
        self._clip_slot = None
        self._launch_button = None
        self._triggered_to_play_value = 126
        self._triggered_to_record_value = 121
        self._started_value = 127
        self._recording_value = 120
        self._stopped_value = 0



    def disconnect(self):
        if (self._clip_slot != None):
            if self.has_clip():
                self._clip_slot.clip.remove_playing_status_listener(self._on_playing_state_changed)
                self._clip_slot.clip.remove_is_recording_listener(self._on_recording_state_changed)
            self._clip_slot.remove_has_clip_listener(self._on_clip_state_changed)
            self._clip_slot.remove_is_triggered_listener(self._on_slot_triggered_changed)
            self._clip_slot = None
        if (self._launch_button != None):
            self._launch_button.unregister_value_notification(self._launch_value)
            self._launch_button = None



    def on_enabled_changed(self):
        self.update()



    def set_clip_slot(self, clip_slot):
        assert ((clip_slot == None) or isinstance(clip_slot, Live.ClipSlot.ClipSlot))
        if (clip_slot != self._clip_slot):
            if (self._clip_slot != None):
                if self.has_clip():
                    self._clip_slot.clip.remove_playing_status_listener(self._on_playing_state_changed)
                    self._clip_slot.clip.remove_is_recording_listener(self._on_recording_state_changed)
                self._clip_slot.remove_is_triggered_listener(self._on_slot_triggered_changed)
                self._clip_slot.remove_has_clip_listener(self._on_clip_state_changed)
            self._clip_slot = clip_slot
            if (self._clip_slot != None):
                if self.has_clip():
                    self._clip_slot.clip.add_playing_status_listener(self._on_playing_state_changed)
                    self._clip_slot.clip.add_is_recording_listener(self._on_recording_state_changed)
                self._clip_slot.add_is_triggered_listener(self._on_slot_triggered_changed)
                self._clip_slot.add_has_clip_listener(self._on_clip_state_changed)
        self.update()



    def set_launch_button(self, button):
        assert ((button == None) or isinstance(button, ButtonElement))
        if (button != self._launch_button):
            if (self._launch_button != None):
                self._launch_button.unregister_value_notification(self._launch_value)
            self._launch_button = button
            if (self._launch_button != None):
                self._launch_button.register_value_notification(self._launch_value)
            self.update()



    def set_triggered_to_play_value(self, value):
        assert (value != None)
        assert isinstance(value, int)
        assert (value in range(-1, 128))
        self._triggered_to_play_value = value



    def set_triggered_to_record_value(self, value):
        assert (value != None)
        assert isinstance(value, int)
        assert (value in range(-1, 128))
        self._triggered_to_record_value = value



    def set_started_value(self, value):
        assert (value != None)
        assert isinstance(value, int)
        assert (value in range(-1, 128))
        self._started_value = value



    def set_recording_value(self, value):
        assert (value != None)
        assert isinstance(value, int)
        assert (value in range(-1, 128))
        self._recording_value = value



    def set_stopped_value(self, value):
        assert (value != None)
        assert isinstance(value, int)
        assert (value in range(-1, 128))
        self._stopped_value = value



    def has_clip(self):
        assert (self._clip_slot != None)
        return self._clip_slot.has_clip



    def update(self):
        if (self.is_enabled() and (self._launch_button != None)):
            self._launch_button.turn_off()
            value_to_send = -1
            if (self._clip_slot != None):
                if self.has_clip():
                    value_to_send = self._stopped_value
                    if self._clip_slot.clip.is_triggered:
                        if self._clip_slot.clip.will_record_on_start:
                            value_to_send = self._triggered_to_record_value
                        else:
                            value_to_send = self._triggered_to_play_value
                    elif self._clip_slot.clip.is_playing:
                        if self._clip_slot.clip.is_recording:
                            value_to_send = self._recording_value
                        else:
                            value_to_send = self._started_value
                elif self._clip_slot.is_triggered:
                    if self._clip_slot.will_record_on_start:
                        value_to_send = self._triggered_to_record_value
                    else:
                        value_to_send = self._triggered_to_play_value
                if (value_to_send in range(128)):
                    self._launch_button.send_value(value_to_send)



    def _on_clip_state_changed(self):
        assert (self._clip_slot != None)
        if self.has_clip():
            if (not self._clip_slot.clip.playing_status_has_listener(self._on_playing_state_changed)):
                self._clip_slot.clip.add_playing_status_listener(self._on_playing_state_changed)
            if (not self._clip_slot.clip.is_recording_has_listener(self._on_recording_state_changed)):
                self._clip_slot.clip.add_is_recording_listener(self._on_recording_state_changed)
        self.update()



    def _on_playing_state_changed(self):
        assert self.has_clip()
        self.update()



    def _on_recording_state_changed(self):
        assert self.has_clip()
        self.update()



    def _on_slot_triggered_changed(self):
        if (not self.has_clip()):
            self.update()



    def _launch_value(self, value):
        assert (self._launch_button != None)
        assert (value in range(128))
        if (self.is_enabled() and (self._clip_slot != None)):
            if (self._launch_button.is_momentary() and self.has_clip()):
                self._clip_slot.clip.set_fire_button_state((value != 0))
            elif ((value != 0) or (not self._launch_button.is_momentary())):
                self._clip_slot.fire()




# local variables:
# tab-width: 4
