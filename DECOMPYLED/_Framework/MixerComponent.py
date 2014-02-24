# emacs-mode: -*- python-*-
import Live
from CompoundComponent import CompoundComponent
from ControlSurfaceComponent import ControlSurfaceComponent
from ChannelStripComponent import ChannelStripComponent
from TrackEQComponent import TrackEQComponent
from TrackFilterComponent import TrackFilterComponent
from ButtonElement import ButtonElement
from EncoderElement import EncoderElement
class MixerComponent(CompoundComponent):
    __module__ = __name__
    __doc__ = ' Class encompassing several channel strips to form a mixer '

    def __init__(self, num_tracks, num_returns = 0, with_eqs = False, with_filters = False):
        assert (num_tracks >= 0)
        assert (num_returns >= 0)
        CompoundComponent.__init__(self)
        self._track_offset = -1
        self._bank_up_button = None
        self._bank_down_button = None
        self._next_track_button = None
        self._prev_track_button = None
        self._prehear_volume_control = None
        self._crossfader_control = None
        self._channel_strips = []
        self._return_strips = []
        self._track_eqs = []
        self._track_filters = []
        for index in range(num_tracks):
            self._channel_strips.append(ChannelStripComponent())
            self.register_components(self._channel_strips[index])
            self._channel_strips[index].set_mixer_callbacks(self._num_solos_pressed, self._num_arms_pressed)
            if with_eqs:
                self._track_eqs.append(TrackEQComponent())
                self.register_components(self._track_eqs[index])
            if with_filters:
                self._track_filters.append(TrackFilterComponent())
                self.register_components(self._track_filters[index])

        for index in range(num_returns):
            self._return_strips.append(ChannelStripComponent())
            self.register_components(self._return_strips[index])

        self._master_strip = ChannelStripComponent()
        self.register_components(self._master_strip)
        self._master_strip.set_track(self.song().master_track)
        self._selected_strip = ChannelStripComponent()
        self.register_components(self._selected_strip)
        self.on_selected_track_changed()
        self._selected_strip.set_mixer_callbacks(self._num_solos_pressed, self._num_arms_pressed)
        self.set_track_offset(0)



    def disconnect(self):
        CompoundComponent.disconnect(self)
        if (self._bank_up_button != None):
            self._bank_up_button.unregister_value_notification(self._bank_up_value)
            self._bank_up_button = None
        if (self._bank_down_button != None):
            self._bank_down_button.unregister_value_notification(self._bank_down_value)
            self._bank_down_button = None
        if (self._next_track_button != None):
            self._next_track_button.unregister_value_notification(self._next_track_value)
            self._next_track_button = None
        if (self._prev_track_button != None):
            self._prev_track_button.unregister_value_notification(self._prev_track_value)
            self._prev_track_button = None
        if (self._prehear_volume_control != None):
            self._prehear_volume_control.release_parameter()
            self._prehear_volume_control = None
        if (self._crossfader_control != None):
            self._crossfader_control.release_parameter()
            self._crossfader_control = None
        self._master_strip = None
        self._selected_strip = None
        self._channel_strips = None
        self._track_eqs = None
        self._track_filters = None



    def channel_strip(self, index):
        assert (index in range(len(self._channel_strips)))
        return self._channel_strips[index]



    def return_strip(self, index):
        assert (index in range(len(self._return_strips)))
        return self._return_strips[index]



    def track_eq(self, index):
        assert (index in range(len(self._track_eqs)))
        return self._track_eqs[index]



    def track_filter(self, index):
        assert (index in range(len(self._track_filters)))
        return self._track_filters[index]



    def master_strip(self):
        return self._master_strip



    def selected_strip(self):
        return self._selected_strip



    def set_prehear_volume_control(self, control):
        assert ((control == None) or isinstance(control, EncoderElement))
        if (self._prehear_volume_control != None):
            self._prehear_volume_control.release_parameter()
        self._prehear_volume_control = control
        self.update()



    def set_crossfader_control(self, control):
        assert ((control == None) or isinstance(control, EncoderElement))
        if (self._crossfader_control != None):
            self._crossfader_control.release_parameter()
        self._crossfader_control = control
        self.update()



    def set_bank_buttons(self, up_button, down_button):
        assert ((up_button == None) or isinstance(up_button, ButtonElement))
        assert ((down_button == None) or isinstance(down_button, ButtonElement))
        do_update = False
        if (up_button is not self._bank_up_button):
            do_update = True
            if (self._bank_up_button != None):
                self._bank_up_button.unregister_value_notification(self._bank_up_value)
            self._bank_up_button = up_button
            if (self._bank_up_button != None):
                self._bank_up_button.register_value_notification(self._bank_up_value)
        if (down_button is not self._bank_down_button):
            do_update = True
            if (self._bank_down_button != None):
                self._bank_down_button.unregister_value_notification(self._bank_down_value)
            self._bank_down_button = down_button
            if (self._bank_down_button != None):
                self._bank_down_button.register_value_notification(self._bank_down_value)
        if do_update:
            self.on_track_list_changed()



    def set_select_buttons(self, next_button, prev_button):
        assert ((next_button == None) or isinstance(next_button, ButtonElement))
        assert ((prev_button == None) or isinstance(prev_button, ButtonElement))
        do_update = False
        if (next_button is not self._next_track_button):
            do_update = True
            if (self._next_track_button != None):
                self._next_track_button.unregister_value_notification(self._next_track_value)
            self._next_track_button = next_button
            if (self._next_track_button != None):
                self._next_track_button.register_value_notification(self._next_track_value)
        if (prev_button is not self._prev_track_button):
            do_update = True
            if (self._prev_track_button != None):
                self._prev_track_button.unregister_value_notification(self._prev_track_value)
            self._prev_track_button = prev_button
            if (self._prev_track_button != None):
                self._prev_track_button.register_value_notification(self._prev_track_value)
        if do_update:
            self.on_selected_track_changed()



    def set_track_offset(self, new_offset):
        assert isinstance(new_offset, int)
        assert (new_offset >= 0)
        if self.is_enabled():
            if (new_offset is not self._track_offset):
                tracks = self._tracks_to_use()
                if (len(tracks) > new_offset):
                    self._track_offset = new_offset
                    self._reassign_tracks()



    def on_enabled_changed(self):
        self.update()



    def on_track_list_changed(self):
        self._reassign_tracks()



    def on_selected_track_changed(self):
        selected_track = self.song().view.selected_track
        if (self._selected_strip != None):
            self._selected_strip.set_track(selected_track)
        if self.is_enabled():
            if (self._next_track_button != None):
                if (selected_track != self.song().master_track):
                    self._next_track_button.turn_on()
                else:
                    self._next_track_button.turn_off()
            if (self._prev_track_button != None):
                if (selected_track != self.song().tracks[0]):
                    self._prev_track_button.turn_on()
                else:
                    self._prev_track_button.turn_off()



    def update(self):
        master_track = self.song().master_track
        if self.is_enabled():
            if (self._prehear_volume_control != None):
                self._prehear_volume_control.connect_to(master_track.mixer_device.cue_volume)
            if (self._crossfader_control != None):
                self._crossfader_control.connect_to(master_track.mixer_device.crossfader)
        else:
            if (self._prehear_volume_control != None):
                self._prehear_volume_control.release_parameter()
            if (self._crossfader_control != None):
                self._crossfader_control.release_parameter()
            if (self._bank_up_button != None):
                self._bank_up_button.turn_off()
            if (self._bank_down_button != None):
                self._bank_down_button.turn_off()
            if (self._next_track_button != None):
                self._next_track_button.turn_off()
            if (self._prev_track_button != None):
                self._prev_track_button.turn_off()
        self._rebuild_callback()



    def _tracks_to_use(self):
        return self.song().tracks



    def _reassign_tracks(self):
        tracks = self._tracks_to_use()
        returns = self.song().return_tracks
        for index in range(len(self._channel_strips)):
            track_index = (self._track_offset + index)
            track = None
            if (len(tracks) > track_index):
                track = tracks[track_index]
            self._channel_strips[index].set_track(track)
            if (len(self._track_eqs) > index):
                self._track_eqs[index].set_track(track)
            if (len(self._track_filters) > index):
                self._track_filters[index].set_track(track)

        for index in range(len(self._return_strips)):
            if (len(returns) > index):
                self._return_strips[index].set_track(returns[index])
            else:
                self._return_strips[index].set_track(None)

        if (self._bank_down_button != None):
            if (self._track_offset > 0):
                self._bank_down_button.turn_on()
            else:
                self._bank_down_button.turn_off()
        if (self._bank_up_button != None):
            if (len(tracks) > (self._track_offset + len(self._channel_strips))):
                self._bank_up_button.turn_on()
            else:
                self._bank_up_button.turn_off()



    def _bank_up_value(self, value):
        assert isinstance(value, int)
        assert (self._bank_up_button != None)
        if self.is_enabled():
            if ((value is not 0) or (not self._bank_up_button.is_momentary())):
                self.set_track_offset((self._track_offset + len(self._channel_strips)))



    def _bank_down_value(self, value):
        assert isinstance(value, int)
        assert (self._bank_down_button != None)
        if self.is_enabled():
            if ((value is not 0) or (not self._bank_down_button.is_momentary())):
                self.set_track_offset(max(0, (self._track_offset - len(self._channel_strips))))



    def _next_track_value(self, value):
        assert (self._next_track_button != None)
        assert (value != None)
        assert isinstance(value, int)
        if self.is_enabled():
            if ((value is not 0) or (not self._next_track_button.is_momentary())):
                selected_track = self.song().view.selected_track
                all_tracks = ((self.song().tracks + self.song().return_tracks) + (self.song().master_track))
                assert (selected_track in all_tracks)
                if (selected_track != all_tracks[-1]):
                    index = list(all_tracks).index(selected_track)
                    self.song().view.selected_track = all_tracks[(index + 1)]



    def _prev_track_value(self, value):
        assert (self._prev_track_button != None)
        assert (value != None)
        assert isinstance(value, int)
        if self.is_enabled():
            if ((value is not 0) or (not self._prev_track_button.is_momentary())):
                selected_track = self.song().view.selected_track
                all_tracks = ((self.song().tracks + self.song().return_tracks) + (self.song().master_track))
                assert (selected_track in all_tracks)
                if (selected_track != all_tracks[0]):
                    index = list(all_tracks).index(selected_track)
                    self.song().view.selected_track = all_tracks[(index - 1)]



    def _num_solos_pressed(self):
        result = 0
        for strip in (tuple(self._channel_strips) + tuple(self._return_strips)):
            if strip.solo_button_pressed():
                result += 1

        return result



    def _num_arms_pressed(self):
        result = 0
        for strip in self._channel_strips:
            if strip.arm_button_pressed():
                result += 1

        return result




# local variables:
# tab-width: 4
