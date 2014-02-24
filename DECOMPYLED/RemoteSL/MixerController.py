# emacs-mode: -*- python-*-
import Live
from RemoteSLComponent import RemoteSLComponent
from consts import *
SLIDER_MODE_VOLUME = 0
SLIDER_MODE_PAN = 1
SLIDER_MODE_SEND = 2
FORW_REW_JUMP_BY_AMOUNT = 1
class MixerController(RemoteSLComponent):
    __module__ = __name__
    __doc__ = "Represents the 'right side' of the RemoteSL:\n  The sliders with the two button rows, and the transport buttons.\n  All controls will be handled by this script: The sliders are mapped to volume/pan/sends\n  of the underlying tracks, so that 8 tracks can be controlled at once. \n  Banks can be switched via the up/down bottons next to the right display.\n  "

    def __init__(self, remote_sl_parent, display_controller):
        RemoteSLComponent.__init__(self, remote_sl_parent)
        self._MixerController__display_controller = display_controller
        self._MixerController__parent = remote_sl_parent
        self._MixerController__forward_button_down = False
        self._MixerController__rewind_button_down = False
        self._MixerController__strip_offset = 0
        self._MixerController__slider_mode = SLIDER_MODE_VOLUME
        self._MixerController__strips = [ MixerChannelStrip(self) for i in range(NUM_CONTROLS_PER_ROW) ]
        self._MixerController__assigned_tracks = []
        self.song().add_tracks_listener(self._MixerController__on_tracks_added_or_deleted)
        self.song().add_record_mode_listener(self._MixerController__on_record_mode_changed)
        self._MixerController__reassign_strips()



    def disconnect(self):
        self.song().remove_tracks_listener(self._MixerController__on_tracks_added_or_deleted)
        self.song().remove_record_mode_listener(self._MixerController__on_record_mode_changed)
        for track in self._MixerController__assigned_tracks:
            if (track and track.name_has_listener(self._MixerController__on_track_name_changed)):
                track.remove_name_listener(self._MixerController__on_track_name_changed)




    def slider_mode(self):
        return self._MixerController__slider_mode



    def receive_midi_cc(self, cc_no, cc_value):
        if (cc_no in mx_display_button_ccs):
            self._MixerController__handle_page_up_down_ccs(cc_no, cc_value)
        elif (cc_no in mx_select_button_ccs):
            self._MixerController__handle_select_button_ccs(cc_no, cc_value)
        elif (cc_no in mx_first_button_row_ccs):
            channel_strip = self._MixerController__strips[(cc_no - MX_FIRST_BUTTON_ROW_BASE_CC)]
            if (cc_value == CC_VAL_BUTTON_PRESSED):
                channel_strip.first_button_pressed()
        elif (cc_no in mx_second_button_row_ccs):
            channel_strip = self._MixerController__strips[(cc_no - MX_SECOND_BUTTON_ROW_BASE_CC)]
            if (cc_value == CC_VAL_BUTTON_PRESSED):
                channel_strip.second_button_pressed()
        elif (cc_no in mx_slider_row_ccs):
            channel_strip = self._MixerController__strips[(cc_no - MX_SLIDER_ROW_BASE_CC)]
            channel_strip.slider_moved(cc_value)
        elif (cc_no in ts_ccs):
            self._MixerController__handle_transport_ccs(cc_no, cc_value)
        else:
            assert False, 'unknown FX midi message'



    def build_midi_map(self, script_handle, midi_map_handle):
        for s in self._MixerController__strips:
            cc_no = (MX_SLIDER_ROW_BASE_CC + self._MixerController__strips.index(s))
            if (s.assigned_track() and s.slider_parameter()):
                map_mode = Live.MidiMap.MapMode.absolute
                parameter = s.slider_parameter()
                Live.MidiMap.map_midi_cc(midi_map_handle, parameter, SL_MIDI_CHANNEL, cc_no, map_mode)
            else:
                Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, SL_MIDI_CHANNEL, cc_no)

        for cc_no in (mx_forwarded_ccs + ts_ccs):
            Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, SL_MIDI_CHANNEL, cc_no)

        for note in (mx_forwarded_notes + ts_notes):
            Live.MidiMap.forward_midi_note(script_handle, midi_map_handle, SL_MIDI_CHANNEL, note)




    def refresh_state(self):
        self._MixerController__update_selected_row_leds()
        self._MixerController__on_record_mode_changed()



    def update_display(self):
        if self._MixerController__rewind_button_down:
            self.song().jump_by(-FORW_REW_JUMP_BY_AMOUNT)
        if self._MixerController__forward_button_down:
            self.song().jump_by(FORW_REW_JUMP_BY_AMOUNT)



    def __reassign_strips(self):
        track_index = self._MixerController__strip_offset
        track_names = []
        parameters = []
        for track in self._MixerController__assigned_tracks:
            if (track and track.name_has_listener(self._MixerController__on_track_name_changed)):
                track.remove_name_listener(self._MixerController__on_track_name_changed)

        self._MixerController__assigned_tracks = []
        all_tracks = ((self.song().tracks + self.song().return_tracks) + (self.song().master_track))
        for s in self._MixerController__strips:
            if (track_index < len(all_tracks)):
                track = all_tracks[track_index]
                s.set_assigned_track(track)
                track_names.append(track.name)
                parameters.append(s.slider_parameter())
                track.add_name_listener(self._MixerController__on_track_name_changed)
                self._MixerController__assigned_tracks.append(track)
            else:
                s.set_assigned_track(None)
                track_names.append('')
                parameters.append(None)
            track_index += 1

        self._MixerController__display_controller.setup_right_display(track_names, parameters)
        self.request_rebuild_midi_map()



    def __handle_page_up_down_ccs(self, cc_no, cc_value):
        all_tracks = ((self.song().tracks + self.song().return_tracks) + (self.song().master_track))
        if (cc_no == MX_DISPLAY_PAGE_UP):
            if (cc_value == CC_VAL_BUTTON_PRESSED):
                if ((len(all_tracks) > NUM_CONTROLS_PER_ROW) and (self._MixerController__strip_offset < (len(all_tracks) - NUM_CONTROLS_PER_ROW))):
                    self._MixerController__strip_offset += NUM_CONTROLS_PER_ROW
                    self._MixerController__validate_strip_offset()
                    self._MixerController__reassign_strips()
        elif (cc_no == MX_DISPLAY_PAGE_DOWN):
            if (cc_value == CC_VAL_BUTTON_PRESSED):
                if ((len(all_tracks) > NUM_CONTROLS_PER_ROW) and (self._MixerController__strip_offset > 0)):
                    self._MixerController__strip_offset -= NUM_CONTROLS_PER_ROW
                    self._MixerController__validate_strip_offset()
                    self._MixerController__reassign_strips()
        else:
            assert False, 'unknown Display midi message'



    def __handle_select_button_ccs(self, cc_no, cc_value):
        if (cc_no == MX_SELECT_SLIDER_ROW):
            if (cc_value == CC_VAL_BUTTON_PRESSED):
                self._MixerController__set_slider_mode(SLIDER_MODE_VOLUME)
        elif (cc_no == MX_SELECT_FIRST_BUTTON_ROW):
            if (cc_value == CC_VAL_BUTTON_PRESSED):
                self._MixerController__set_slider_mode(SLIDER_MODE_PAN)
        elif (cc_no == MX_SELECT_SECOND_BUTTON_ROW):
            if (cc_value == CC_VAL_BUTTON_PRESSED):
                self._MixerController__set_slider_mode(SLIDER_MODE_SEND)
        else:
            assert False, 'unknown select row midi message'



    def __handle_transport_ccs(self, cc_no, cc_value):
        if (cc_no == TS_REWIND_CC):
            if (cc_value == CC_VAL_BUTTON_PRESSED):
                self._MixerController__rewind_button_down = True
                self.song().jump_by(-FORW_REW_JUMP_BY_AMOUNT)
            else:
                self._MixerController__rewind_button_down = False
        elif (cc_no == TS_FORWARD_CC):
            if (cc_value == CC_VAL_BUTTON_PRESSED):
                self._MixerController__forward_button_down = True
                self.song().jump_by(FORW_REW_JUMP_BY_AMOUNT)
            else:
                self._MixerController__forward_button_down = False
        elif (cc_no == TS_STOP_CC):
            if (cc_value == CC_VAL_BUTTON_PRESSED):
                self.song().stop_playing()
        elif (cc_no == TS_PLAY_CC):
            if (cc_value == CC_VAL_BUTTON_PRESSED):
                self.song().start_playing()
        elif (cc_no == TS_LOOP_CC):
            if (cc_value == CC_VAL_BUTTON_PRESSED):
                self.song().loop = (not self.song().loop)
        elif (cc_no == TS_RECORD_CC):
            if (cc_value == CC_VAL_BUTTON_PRESSED):
                self.song().record_mode = (not self.song().record_mode)
        else:
            assert False, 'unknown Transport CC'



    def __on_tracks_added_or_deleted(self):
        self._MixerController__validate_strip_offset()
        self._MixerController__validate_slider_mode()
        self._MixerController__reassign_strips()



    def __on_track_name_changed(self):
        self._MixerController__reassign_strips()



    def __validate_strip_offset(self):
        all_tracks = ((self.song().tracks + self.song().return_tracks) + (self.song().master_track))
        self._MixerController__strip_offset = min(self._MixerController__strip_offset, (len(all_tracks) - 1))
        self._MixerController__strip_offset = max(0, self._MixerController__strip_offset)



    def __validate_slider_mode(self):
        if ((self._MixerController__slider_mode - SLIDER_MODE_SEND) >= len(self.song().return_tracks)):
            self._MixerController__slider_mode = SLIDER_MODE_VOLUME



    def __set_slider_mode(self, new_mode):
        if ((self._MixerController__slider_mode >= SLIDER_MODE_SEND) and (new_mode >= SLIDER_MODE_SEND)):
            if (((self._MixerController__slider_mode - SLIDER_MODE_SEND) + 1) < len(self.song().return_tracks)):
                self._MixerController__slider_mode += 1
            else:
                self._MixerController__slider_mode = SLIDER_MODE_SEND
            self._MixerController__update_selected_row_leds()
            self._MixerController__reassign_strips()
        elif (self._MixerController__slider_mode != new_mode):
            self._MixerController__slider_mode = new_mode
            self._MixerController__update_selected_row_leds()
            self._MixerController__reassign_strips()



    def __update_selected_row_leds(self):
        if (self._MixerController__slider_mode == SLIDER_MODE_VOLUME):
            self.send_midi(((CC_STATUS + SL_MIDI_CHANNEL),
             MX_SELECT_SLIDER_ROW,
             CC_VAL_BUTTON_PRESSED))
            self.send_midi(((CC_STATUS + SL_MIDI_CHANNEL),
             MX_SELECT_FIRST_BUTTON_ROW,
             CC_VAL_BUTTON_RELEASED))
            self.send_midi(((CC_STATUS + SL_MIDI_CHANNEL),
             MX_SELECT_SECOND_BUTTON_ROW,
             CC_VAL_BUTTON_RELEASED))
        elif (self._MixerController__slider_mode == SLIDER_MODE_PAN):
            self.send_midi(((CC_STATUS + SL_MIDI_CHANNEL),
             MX_SELECT_SLIDER_ROW,
             CC_VAL_BUTTON_RELEASED))
            self.send_midi(((CC_STATUS + SL_MIDI_CHANNEL),
             MX_SELECT_FIRST_BUTTON_ROW,
             CC_VAL_BUTTON_PRESSED))
            self.send_midi(((CC_STATUS + SL_MIDI_CHANNEL),
             MX_SELECT_SECOND_BUTTON_ROW,
             CC_VAL_BUTTON_RELEASED))
        elif (self._MixerController__slider_mode >= SLIDER_MODE_SEND):
            self.send_midi(((CC_STATUS + SL_MIDI_CHANNEL),
             MX_SELECT_SLIDER_ROW,
             CC_VAL_BUTTON_RELEASED))
            self.send_midi(((CC_STATUS + SL_MIDI_CHANNEL),
             MX_SELECT_FIRST_BUTTON_ROW,
             CC_VAL_BUTTON_RELEASED))
            self.send_midi(((CC_STATUS + SL_MIDI_CHANNEL),
             MX_SELECT_SECOND_BUTTON_ROW,
             CC_VAL_BUTTON_PRESSED))



    def __on_record_mode_changed(self):
        if self.song().record_mode:
            self.send_midi(((CC_STATUS + SL_MIDI_CHANNEL),
             TS_RECORD_CC,
             CC_VAL_BUTTON_PRESSED))
        else:
            self.send_midi(((CC_STATUS + SL_MIDI_CHANNEL),
             TS_RECORD_CC,
             CC_VAL_BUTTON_RELEASED))



    def is_arm_exclusive(self):
        return self._MixerController__parent.song().exclusive_arm



    def set_selected_track(self, track):
        if track:
            self._MixerController__parent.song().view.selected_track = track



    def track_about_to_arm(self, track):
        if (track and self._MixerController__parent.song().exclusive_arm):
            for t in self._MixerController__parent.song().tracks:
                if (t.can_be_armed and (t.arm and (not (t == track)))):
                    t.arm = False




class MixerChannelStrip:
    __module__ = __name__
    __doc__ = 'Represents one of the 8 track related strips in the Mixer controls (one slider, \n  two buttons)\n  '

    def __init__(self, mixer_controller_parent):
        self._MixerChannelStrip__mixer_controller = mixer_controller_parent



    def song(self):
        return self._MixerChannelStrip__mixer_controller.song()



    def assigned_track(self):
        return self._MixerChannelStrip__assigned_track



    def set_assigned_track(self, track):
        self._MixerChannelStrip__assigned_track = track



    def slider_parameter(self):
        slider_mode = self._MixerChannelStrip__mixer_controller.slider_mode()
        if self._MixerChannelStrip__assigned_track:
            if (slider_mode == SLIDER_MODE_VOLUME):
                return self._MixerChannelStrip__assigned_track.mixer_device.volume
            elif (slider_mode == SLIDER_MODE_PAN):
                return self._MixerChannelStrip__assigned_track.mixer_device.panning
            elif (slider_mode >= SLIDER_MODE_SEND):
                send_index = (slider_mode - SLIDER_MODE_SEND)
                if (send_index < len(self._MixerChannelStrip__assigned_track.mixer_device.sends)):
                    return self._MixerChannelStrip__assigned_track.mixer_device.sends[send_index]
                else:
                    return None
        else:
            return None



    def slider_moved(self, cc_value):
        assert ((self._MixerChannelStrip__assigned_track is None) or (self.slider_parameter() is None)), 'should only be reached when the slider was not realtime mapped '



    def first_button_pressed(self):
        if self._MixerChannelStrip__assigned_track:
            if (self._MixerChannelStrip__assigned_track in (self.song().tracks + self.song().return_tracks)):
                self._MixerChannelStrip__assigned_track.mute = (not self._MixerChannelStrip__assigned_track.mute)



    def second_button_pressed(self):
        if ((self._MixerChannelStrip__assigned_track in self.song().tracks) and self._MixerChannelStrip__assigned_track.can_be_armed):
            self._MixerChannelStrip__mixer_controller.track_about_to_arm(self._MixerChannelStrip__assigned_track)
            self._MixerChannelStrip__assigned_track.arm = (not self._MixerChannelStrip__assigned_track.arm)
            if self._MixerChannelStrip__assigned_track.arm:
                if self._MixerChannelStrip__assigned_track.view.select_instrument():
                    self._MixerChannelStrip__mixer_controller.set_selected_track(self._MixerChannelStrip__assigned_track)




# local variables:
# tab-width: 4
