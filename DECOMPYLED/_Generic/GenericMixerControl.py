# emacs-mode: -*- python-*-
import Live
from GenericComponent import GenericComponent
from consts import *
class GenericMixerControl(GenericComponent):
    __module__ = __name__
    __doc__ = ' Class representing the track mixer in Live '

    def __init__(self, parent, volume_controllers, map_mode, arm_controllers, mixer_options):
        self._GenericMixerControl__parent = parent
        self._GenericMixerControl__volume_controllers = volume_controllers
        self._GenericMixerControl__arm_controllers = arm_controllers
        self._GenericMixerControl__mixer_options = mixer_options
        self._GenericMixerControl__tracks_with_mapped_arm_button = ()
        self._GenericMixerControl__arm_buttons_toggle = ((self._GenericMixerControl__mixer_options is None) or (not ('NOTOGGLE' in self._GenericMixerControl__mixer_options.keys())))
        if map_mode:
            self._GenericMixerControl__map_mode = map_mode
        else:
            self._GenericMixerControl__map_mode = Live.MidiMap.MapMode.absolute



    def build_midi_map(self, script_handle, midi_map_handle):
        for track in self._GenericMixerControl__tracks_with_mapped_arm_button:
            if track:
                track.remove_arm_listener(self._GenericMixerControl__on_arm_changed)

        self._GenericMixerControl__tracks_with_mapped_arm_button = ()
        self._GenericMixerControl__map_track_volumes(script_handle, midi_map_handle)
        self._GenericMixerControl__map_track_arms(script_handle, midi_map_handle)
        self._GenericMixerControl__map_track_sends(script_handle, midi_map_handle)
        self._GenericMixerControl__map_track_pans(script_handle, midi_map_handle)



    def __map_track_volumes(self, script_handle, midi_map_handle):
        feedback_rule = Live.MidiMap.CCFeedbackRule()
        for slider in range(len(self._GenericMixerControl__volume_controllers)):
            mapping_details = self._GenericMixerControl__volume_controllers[slider]
            mapping_cc = 0
            mapping_channel = 0
            if (not isinstance(mapping_details, tuple)):
                mapping_cc = mapping_details
                mapping_channel = self._GenericMixerControl__parent.global_channel()
            elif (len(mapping_details) > 1):
                mapping_cc = mapping_details[0]
                if (mapping_details[1] >= 0):
                    mapping_channel = mapping_details[1]
                else:
                    mapping_channel = self._GenericMixerControl__parent.global_channel()
            if (mapping_cc >= 0):
                parameter_to_map = 0
                feedback_rule.channel = 0
                feedback_rule.cc_value_map = tuple()
                feedback_rule.delay_in_ms = -1.0
                feedback_rule.cc_no = mapping_cc
                if (len(self._GenericMixerControl__parent.song().tracks) > slider):
                    parameter_to_map = self._GenericMixerControl__parent.song().tracks[slider].mixer_device.volume
                else:
                    self._GenericMixerControl__parent.send_midi(((CC_STATUS + mapping_channel),
                     mapping_cc,
                     STATUS_OFF))
                    continue
                Live.MidiMap.map_midi_cc_with_feedback_map(midi_map_handle, parameter_to_map, mapping_channel, mapping_cc, self._GenericMixerControl__map_mode, feedback_rule)
                Live.MidiMap.send_feedback_for_parameter(midi_map_handle, parameter_to_map)

        if self._GenericMixerControl__mixer_options:
            if (('MASTERVOLUME' in self._GenericMixerControl__mixer_options) and (self._GenericMixerControl__mixer_options['MASTERVOLUME'] >= 0)):
                cc_no = self._GenericMixerControl__mixer_options['MASTERVOLUME']
                parameter_to_map = self._GenericMixerControl__parent.song().master_track.mixer_device.volume
                if parameter_to_map:
                    feedback_rule.channel = 0
                    feedback_rule.cc_value_map = tuple()
                    feedback_rule.delay_in_ms = -1.0
                    feedback_rule.cc_no = cc_no
                    Live.MidiMap.map_midi_cc_with_feedback_map(midi_map_handle, parameter_to_map, self._GenericMixerControl__parent.global_channel(), cc_no, self._GenericMixerControl__map_mode, feedback_rule)
                    Live.MidiMap.send_feedback_for_parameter(midi_map_handle, parameter_to_map)



    def __map_track_arms(self, script_handle, midi_map_handle):
        feedback_rule = Live.MidiMap.CCFeedbackRule()
        for button in range(len(self._GenericMixerControl__arm_controllers)):
            if (len(self._GenericMixerControl__parent.song().tracks) > button):
                if (self._GenericMixerControl__arm_controllers[button] >= 0):
                    Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, 0, self._GenericMixerControl__arm_controllers[button])
                    track = self._GenericMixerControl__parent.song().tracks[button]
                    if track:
                        status = STATUS_OFF
                        if track.arm:
                            status = STATUS_ON
                        self._GenericMixerControl__parent.send_midi((CC_STATUS,
                         self._GenericMixerControl__arm_controllers[button],
                         status))
                        track.add_arm_listener(self._GenericMixerControl__on_arm_changed)
                        self._GenericMixerControl__tracks_with_mapped_arm_button += (track)




    def __map_track_sends(self, script_handle, midi_map_handle):
        feedback_rule = Live.MidiMap.CCFeedbackRule()
        if self._GenericMixerControl__mixer_options:
            if (('NUMSENDS' in self._GenericMixerControl__mixer_options.keys()) and (self._GenericMixerControl__mixer_options['NUMSENDS'] > 0)):
                for send in range(self._GenericMixerControl__mixer_options['NUMSENDS']):
                    send_key = ('SEND' + str((send + 1)))
                    if ((send_key in self._GenericMixerControl__mixer_options.keys()) and (len(self._GenericMixerControl__parent.song().return_tracks) > send)):
                        send_ccs = self._GenericMixerControl__mixer_options[send_key]
                        counter = 0
                        for mapping_details in send_ccs:
                            mapping_cc = 0
                            mapping_channel = 0
                            if (not isinstance(mapping_details, tuple)):
                                mapping_cc = mapping_details
                                mapping_channel = self._GenericMixerControl__parent.global_channel()
                            elif (len(mapping_details) > 1):
                                mapping_cc = mapping_details[0]
                                if (mapping_details[1] >= 0):
                                    mapping_channel = mapping_details[1]
                                else:
                                    mapping_channel = self._GenericMixerControl__parent.global_channel()
                            if ((mapping_cc >= 0) and ((len(self._GenericMixerControl__parent.song().tracks) > counter) and self._GenericMixerControl__parent.song().tracks[counter])):
                                parameter_to_map = self._GenericMixerControl__parent.song().tracks[counter].mixer_device.sends[send]
                                if parameter_to_map:
                                    feedback_rule.channel = 0
                                    feedback_rule.cc_value_map = tuple()
                                    feedback_rule.delay_in_ms = -1.0
                                    feedback_rule.cc_no = mapping_cc
                                    Live.MidiMap.map_midi_cc_with_feedback_map(midi_map_handle, parameter_to_map, mapping_channel, mapping_cc, self._GenericMixerControl__map_mode, feedback_rule)
                                    Live.MidiMap.send_feedback_for_parameter(midi_map_handle, parameter_to_map)
                                counter += 1





    def __map_track_pans(self, script_handle, midi_map_handle):
        feedback_rule = Live.MidiMap.CCFeedbackRule()
        if (self._GenericMixerControl__mixer_options and ('PANS' in self._GenericMixerControl__mixer_options.keys())):
            counter = 0
            for mapping_details in self._GenericMixerControl__mixer_options['PANS']:
                mapping_cc = -1
                mapping_channel = self._GenericMixerControl__parent.global_channel()
                if (not isinstance(mapping_details, tuple)):
                    mapping_cc = mapping_details
                elif (len(mapping_details) > 0):
                    mapping_cc = mapping_details[0]
                    mapping_channel = mapping_details[1]
                if (mapping_cc >= 0):
                    if (len(self._GenericMixerControl__parent.song().tracks) > counter):
                        parameter_to_map = self._GenericMixerControl__parent.song().tracks[counter].mixer_device.panning
                        feedback_rule.channel = 0
                        feedback_rule.cc_value_map = tuple()
                        feedback_rule.delay_in_ms = -1.0
                        feedback_rule.cc_no = mapping_cc
                        Live.MidiMap.map_midi_cc_with_feedback_map(midi_map_handle, parameter_to_map, mapping_channel, mapping_cc, self._GenericMixerControl__map_mode, feedback_rule)
                        Live.MidiMap.send_feedback_for_parameter(midi_map_handle, parameter_to_map)
                    else:
                        self._GenericMixerControl__parent.send_midi(((CC_STATUS + mapping_channel),
                         mapping_cc,
                         STATUS_OFF))
                        continue
                counter += 1




    def disconnect(self):
        global_channel = self._GenericMixerControl__parent.global_channel()
        for track in self._GenericMixerControl__tracks_with_mapped_arm_button:
            if track:
                track.remove_arm_listener(self._GenericMixerControl__on_arm_changed)

        status = STATUS_OFF
        for cc_no in self._GenericMixerControl__arm_controllers:
            if (cc_no >= 0):
                self._GenericMixerControl__parent.send_midi(((CC_STATUS + global_channel),
                 cc_no,
                 status))

        for mapping_info in self._GenericMixerControl__volume_controllers:
            cc_no = -1
            channel = global_channel
            if (not isinstance(mapping_info, tuple)):
                cc_no = mapping_info
            else:
                cc_no = mapping_info[0]
                channel = mapping_info[1]
            if (cc_no >= 0):
                self._GenericMixerControl__parent.send_midi(((CC_STATUS + channel),
                 cc_no,
                 status))

        if self._GenericMixerControl__mixer_options:
            if ('PANS' in self._GenericMixerControl__mixer_options.keys()):
                for mapping_details in self._GenericMixerControl__mixer_options['PANS']:
                    mapping_cc = -1
                    mapping_channel = self._GenericMixerControl__parent.global_channel()
                    if (not isinstance(mapping_details, tuple)):
                        mapping_cc = mapping_details
                    elif (len(mapping_details) > 0):
                        mapping_cc = mapping_details[0]
                        mapping_channel = mapping_details[1]
                    if (mapping_cc >= 0):
                        self._GenericMixerControl__parent.send_midi(((CC_STATUS + mapping_channel),
                         mapping_cc,
                         status))

            if (('NUMSENDS' in self._GenericMixerControl__mixer_options.keys()) and (self._GenericMixerControl__mixer_options['NUMSENDS'] > 0)):
                for send in range(self._GenericMixerControl__mixer_options['NUMSENDS']):
                    send_key = ('SEND' + str((send + 1)))
                    if ((send_key in self._GenericMixerControl__mixer_options.keys()) and self._GenericMixerControl__mixer_options[send_key]):
                        for mapping_info in self._GenericMixerControl__mixer_options[send_key]:
                            cc_no = -1
                            channel = global_channel
                            if (not isinstance(mapping_info, tuple)):
                                cc_no = mapping_info
                            else:
                                cc_no = mapping_info[0]
                                channel = mapping_info[1]
                            if (cc_no >= 0):
                                self._GenericMixerControl__parent.send_midi(((CC_STATUS + channel),
                                 cc_no,
                                 status))


            if (('MASTERVOLUME' in self._GenericMixerControl__mixer_options.keys()) and (self._GenericMixerControl__mixer_options['MASTERVOLUME'] >= 0)):
                self._GenericMixerControl__parent.send_midi(((CC_STATUS + global_channel),
                 self._GenericMixerControl__mixer_options['MASTERVOLUME'],
                 status))



    def receive_midi_cc(self, cc_no, cc_value):
        if (list(self._GenericMixerControl__arm_controllers).count(cc_no) > 0):
            index = list(self._GenericMixerControl__arm_controllers).index(cc_no)
            if (len(self._GenericMixerControl__parent.song().tracks) > index):
                track = self._GenericMixerControl__parent.song().tracks[index]
                if (track and track.can_be_armed):
                    if ((cc_value > 0) or self._GenericMixerControl__arm_buttons_toggle):
                        track.arm = (not track.arm)
                        if self._GenericMixerControl__parent.song().exclusive_arm:
                            for t in self._GenericMixerControl__parent.song().tracks:
                                if (t.can_be_armed and (t.arm and (not (t == track)))):
                                    t.arm = False

                        if track.arm:
                            if track.view.select_instrument():
                                self._GenericMixerControl__parent.song().view.selected_track = track



    def __on_arm_changed(self):
        for button in range(len(self._GenericMixerControl__arm_controllers)):
            cc_no = self._GenericMixerControl__arm_controllers[button]
            if ((cc_no >= 0) and (len(self._GenericMixerControl__parent.song().tracks) > button)):
                status = STATUS_OFF
                if self._GenericMixerControl__parent.song().tracks[button].arm:
                    status = STATUS_ON
                self._GenericMixerControl__parent.send_midi((CC_STATUS,
                 cc_no,
                 status))





# local variables:
# tab-width: 4
