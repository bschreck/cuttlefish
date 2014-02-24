# emacs-mode: -*- python-*-
import Application
import MidiMap
from _Axiom.consts import *
class SliderSection:
    __module__ = __name__
    __doc__ = ' Class representing the sliders and Zone/Group-buttons on the\n      Axiom 49 & 61 Controllers \n  '

    def __init__(self, parent):
        self._SliderSection__parent = parent
        self._SliderSection__mod_pressed = False



    def build_midi_map(self, script_handle, midi_map_handle):
        feedback_rule = MidiMap.CCFeedbackRule()
        feedback_rule.channel = 0
        feedback_rule.cc_no = AXIOM_SLI9
        feedback_rule.cc_value_map = tuple()
        feedback_rule.delay_in_ms = -1.0
        for channel in range(16):
            MidiMap.map_midi_cc_with_feedback_map(midi_map_handle, self._SliderSection__parent.song().master_track.mixer_device.volume, channel, AXIOM_SLI9, MidiMap.MapMode.absolute_14_bit, feedback_rule)

        for channel in range(4):
            MidiMap.forward_midi_cc(script_handle, midi_map_handle, channel, AXIOM_BUT9)
            for slider in range(8):
                track_index = (slider + (channel * 8))
                if (len(self._SliderSection__parent.song().tracks) > track_index):
                    feedback_rule.channel = 0
                    feedback_rule.cc_no = AXIOM_SLIDERS[slider]
                    feedback_rule.cc_value_map = tuple()
                    feedback_rule.delay_in_ms = -1.0
                    MidiMap.map_midi_cc_with_feedback_map(midi_map_handle, self._SliderSection__parent.song().tracks[track_index].mixer_device.volume, channel, AXIOM_SLIDERS[slider], MidiMap.MapMode.absolute_14_bit, feedback_rule)
                    MidiMap.forward_midi_cc(script_handle, midi_map_handle, channel, AXIOM_BUTTONS[slider])
                else:
                    break





    def receive_midi_cc(self, cc_no, cc_value, channel):
        if (list(AXIOM_BUTTONS).count(cc_no) > 0):
            button_index = list(AXIOM_BUTTONS).index(cc_no)
            if (cc_no == AXIOM_BUT9):
                self._SliderSection__mod_pressed = (cc_value == 127)
            elif (button_index in range(8)):
                track_index = (button_index + (8 * channel))
                if (len(self._SliderSection__parent.song().tracks) > track_index):
                    track = self._SliderSection__parent.song().tracks[track_index]
                    if (track and track.can_be_armed):
                        if (not self._SliderSection__mod_pressed):
                            track.mute = (not track.mute)
                        else:
                            track.arm = (not track.arm)
                            if self._SliderSection__parent.song().exclusive_arm:
                                for t in self._SliderSection__parent.song().tracks:
                                    if (t.can_be_armed and (t.arm and (not (t == track)))):
                                        t.arm = False

                            if track.arm:
                                if track.view.select_instrument():
                                    self._SliderSection__parent.song().view.selected_track = track




# local variables:
# tab-width: 4
