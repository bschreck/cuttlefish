# emacs-mode: -*- python-*-
import Live
import MidiRemoteScript
from ControlElement import ControlElement
from ControlSurfaceComponent import ControlSurfaceComponent
from DeviceComponent import DeviceComponent
from PhysicalDisplayElement import PhysicalDisplayElement
from InputControlElement import *
from SessionComponent import SessionComponent
class ControlSurface(object):
    __module__ = __name__
    __doc__ = ' Central base class for scripts based on the new Framework. \n      New scripts need to subclass this class and add special behaviour.\n  '

    def __init__(self, c_instance):
        """ Define and Initialise standard behaviour """
        object.__init__(self)
        self._c_instance = c_instance
        self._midi_map_handle = None
        self._pad_translations = None
        self._suggested_input_port = str('')
        self._suggested_output_port = str('')
        self._modes = []
        self._components = []
        self._displays = []
        self._controls = []
        self._device_component = None
        self._forwarding_registry = {}
        self._timer_callbacks = []
        self._scheduled_messages = []
        self._in_build_midi_map = False
        self._suppress_requests_counter = 0
        self._rebuild_requests_during_suppression = 0
        ControlSurfaceComponent.set_song_and_application(self.song(), self.application())
        ControlElement.set_register_control_callback(self._register_control)
        ControlElement.set_send_midi_callback(self._send_midi)
        InputControlElement.set_mapping_callback(self._install_mapping)
        InputControlElement.set_forwarding_callback(self._install_forwarding)
        InputControlElement.set_translation_callback(self._translate_message)
        ControlSurfaceComponent.set_register_component_callback(self._register_component)
        ControlSurfaceComponent.set_register_timer_notification_callback(self._register_timer_callback)
        ControlSurfaceComponent.set_unregister_timer_notification_callback(self._unregister_timer_callback)
        ControlSurfaceComponent.set_request_rebuild_callback(self.request_rebuild_midi_map)
        SessionComponent.set_highlighting_callback(self._set_session_highlight)
        self.song().add_tracks_listener(self._on_track_list_changed)
        self.song().add_scenes_listener(self._on_scene_list_changed)
        self.song().view.add_selected_track_listener(self._on_selected_track_changed)
        self.song().view.add_selected_scene_listener(self._on_selected_scene_changed)



    def application(self):
        """ Returns a reference to the application that we are running in """
        return Live.Application.get_application()



    def song(self):
        """ Returns a reference to the Live song instance that we control """
        return self._c_instance.song()



    def disconnect(self):
        """ Live -> Script: Called right before we get disconnected from Live """
        for message in self._scheduled_messages:
            if (message['Parameter'] != None):
                message['Message'](message['Parameter'])
            else:
                message['Message']()

        self._scheduled_messages = None
        self._forwarding_registry = None
        for component in self._components:
            component.disconnect()

        for control in self._controls:
            control.disconnect()

        self._controls = None
        self._components = None
        self._displays = None
        self._timer_callbacks = None
        self._device_component = None
        self._pad_translations = None
        ControlElement.release_class_attributes()
        InputControlElement.release_class_attributes()
        ControlSurfaceComponent.release_class_attributes()
        SessionComponent.release_class_attributes()
        self.song().remove_tracks_listener(self._on_track_list_changed)
        self.song().remove_scenes_listener(self._on_scene_list_changed)
        self.song().view.remove_selected_track_listener(self._on_selected_track_changed)
        self.song().view.remove_selected_scene_listener(self._on_selected_scene_changed)



    def can_lock_to_devices(self):
        return (self._device_component != None)



    def lock_to_device(self, device):
        assert (self._device_component != None)
        self._device_component.set_lock_to_device(True)



    def unlock_from_device(self, device):
        assert (self._device_component != None)
        self._device_component.set_lock_to_device(False)



    def set_appointed_device(self, device):
        assert ((device == None) or isinstance(device, Live.Device.Device))
        assert (self._device_component != None)
        self.set_suppress_rebuild_requests(True)
        self._device_component.set_device(device)
        self.set_suppress_rebuild_requests(False)



    def suggest_input_port(self):
        """ Live -> Script: Live can ask for the name of the script's prefered input port """
        return self._suggested_input_port



    def suggest_output_port(self):
        """ Live -> Script: Live can ask for the name of the script's prefered output port """
        return self._suggested_output_port



    def suggest_map_mode(self, cc_no, channel):
        """ Live -> Script: Live can ask for a suitable mapping mode for a given CC """
        assert (cc_no in range(128))
        assert (channel in range(16))
        suggested_map_mode = -1
        for control in self._controls:
            if (isinstance(control, InputControlElement) and ((control.message_type() == MIDI_CC_TYPE) and ((control.message_identifier() == cc_no) and (control.message_channel() == channel)))):
                suggested_map_mode = control.message_map_mode()
                break

        return suggested_map_mode



    def supports_pad_translation(self):
        return (self._pad_translations != None)



    def show_message(self, message):
        """ Displays the given message in Live's status bar """
        self._c_instance.show_message(message)



    def instance_identifier(self):
        return self._c_instance.instance_identifier()



    def connect_script_instances(self, instanciated_scripts):
        """ Called by the Application as soon as all scripts are initialized.
        You can connect yourself to other running scripts here, as we do it
        connect the extension modules (MackieControlXTs).
    """
        pass


    def request_rebuild_midi_map(self):
        """ Script -> Live
        When the internal MIDI controller has changed in a way that you need to rebuild
        the MIDI mappings, request a rebuild by calling this function
        This is processed as a request, to be sure that its not too often called, because
        its time-critical.
    """
        assert (not self._in_build_midi_map)
        if (self._suppress_requests_counter > 0):
            self._rebuild_requests_during_suppression += 1
        else:
            self._c_instance.request_rebuild_midi_map()



    def build_midi_map(self, midi_map_handle):
        """ Live -> Script
        Build DeviceParameter Mappings, that are processed in Audio time, or
        forward MIDI messages explicitly to our receive_midi_functions.
        Which means that when you are not forwarding MIDI, nor mapping parameters, 
        you will never get any MIDI messages at all.
    """
        assert (self._suppress_requests_counter == 0)
        self._in_build_midi_map = True
        self._midi_map_handle = midi_map_handle
        self._forwarding_registry = {}
        for control in self._controls:
            if isinstance(control, InputControlElement):
                control.install_connections()

        self._midi_map_handle = None
        self._in_build_midi_map = False
        if (self._pad_translations != None):
            self._c_instance.set_pad_translation(self._pad_translations)



    def toggle_lock(self):
        """ Script -> Live
        Use this function to toggle the script's lock on devices
    """
        self._c_instance.toggle_lock()



    def refresh_state(self):
        """ Live -> Script
        Send out MIDI to completely update the attached MIDI controller.
        Will be called when requested by the user, after for example having reconnected 
        the MIDI cables...
    """
        for control in self._controls:
            control.clear_send_cache()

        for component in self._components:
            component.update()




    def update_display(self):
        """ Live -> Script
        Aka on_timer. Called every 100 ms and should be used to update display relevant
        parts of the controller
    """
        for message in self._scheduled_messages:
            message['Delay'] -= 1
            if (message['Delay'] == 0):
                if (message['Parameter'] != None):
                    message['Message'](message['Parameter'])
                else:
                    message['Message']()
                del self._scheduled_messages[self._scheduled_messages.index(message)]

        for callback in self._timer_callbacks:
            callback()




    def receive_midi(self, midi_bytes):
        """ Live -> Script
        MIDI messages are only received through this function, when explicitly 
        forwarded in 'build_midi_map'.
    """
        assert (midi_bytes != None)
        assert isinstance(midi_bytes, tuple)
        self.set_suppress_rebuild_requests(True)
        if (len(midi_bytes) is 3):
            msg_type = (midi_bytes[0] & 240)
            forwarding_key = [midi_bytes[0]]
            if (msg_type is not MIDI_PB_TYPE):
                forwarding_key.append(midi_bytes[1])
            recipient = self._forwarding_registry[tuple(forwarding_key)]
            if (recipient != None):
                recipient.receive_value(midi_bytes[2])
        else:
            self.handle_sysex(midi_bytes)
        self.set_suppress_rebuild_requests(False)



    def handle_sysex(self, midi_bytes):
        debug_print('handle_sysex is abstract. Forgot to override it?')
        assert False



    def set_device_component(self, device_component):
        assert (self._device_component == None)
        assert (device_component != None)
        assert isinstance(device_component, DeviceComponent)
        self._device_component = device_component
        self._device_component.set_lock_callback(self._toggle_lock)



    def set_suppress_rebuild_requests(self, suppress_requests):
        """ Set suppression during bigger changes, resetting will rebuild if needed """
        assert (not self._in_build_midi_map)
        assert isinstance(suppress_requests, type(False))
        if suppress_requests:
            self._suppress_requests_counter += 1
        else:
            assert (self._suppress_requests_counter > 0)
            self._suppress_requests_counter -= 1
            if ((self._suppress_requests_counter == 0) and (self._rebuild_requests_during_suppression > 0)):
                self.request_rebuild_midi_map()
                self._rebuild_requests_during_suppression = 0



    def set_pad_translations(self, pad_translations):
        assert (self._pad_translations == None)
        assert (pad_translations != None)
        assert isinstance(pad_translations, tuple)
        assert (len(pad_translations) <= 16)
        for translation in pad_translations:
            assert (translation != None)
            assert isinstance(translation, tuple)
            assert (len(translation) == 4)
            assert (translation[0] in range(4))
            assert (translation[1] in range(4))
            assert (translation[2] in range(128))
            assert (translation[3] in range(16))

        self._pad_translations = pad_translations



    def schedule_message(self, delay_in_ticks, callback, parameter = None):
        """ Schedule a callback to be called after a specified time """
        assert (delay_in_ticks > 0)
        assert (callback != None)
        assert (dir(callback).count('im_func') is 1)
        self._scheduled_messages.append({'Message': callback,
         'Delay': delay_in_ticks,
         'Parameter': parameter})



    def _register_control(self, control):
        """ puts control into the list of controls for triggering updates """
        assert (control != None)
        assert isinstance(control, ControlElement)
        self._controls.append(control)
        if isinstance(control, PhysicalDisplayElement):
            self._displays.append(control)



    def _register_component(self, component):
        """ puts component into the list of controls for triggering updates """
        assert (component != None)
        assert isinstance(component, ControlSurfaceComponent)
        self._components.append(component)



    def _register_timer_callback(self, callback):
        """ Registers a callback that is triggerd on every call of update_display """
        assert (callback != None)
        assert (dir(callback).count('im_func') is 1)
        assert (self._timer_callbacks.count(callback) == 0)
        self._timer_callbacks.append(callback)



    def _unregister_timer_callback(self, callback):
        """ Unregisters a timer callback """
        assert (callback != None)
        assert (dir(callback).count('im_func') is 1)
        assert (self._timer_callbacks.count(callback) == 1)
        self._timer_callbacks.remove(callback)



    def _send_midi(self, midi_event_bytes):
        """ Script -> Live
        Use this function to send MIDI events through Live to the _real_ MIDI devices
        that this script is assigned to.
    """
        self._c_instance.send_midi(midi_event_bytes)



    def _install_mapping(self, control, parameter, feedback_delay = 0):
        assert self._in_build_midi_map
        assert (self._midi_map_handle != None)
        assert ((control != None) and (parameter != None))
        assert isinstance(parameter, Live.DeviceParameter.DeviceParameter)
        assert isinstance(control, InputControlElement)
        assert isinstance(feedback_delay, int)
        feedback_rule = None
        if (control.message_type() is MIDI_NOTE_TYPE):
            feedback_rule = Live.MidiMap.NoteFeedbackRule()
            feedback_rule.note_no = control.message_identifier()
            feedback_rule.vel_map = tuple()
        elif (control.message_type() is MIDI_CC_TYPE):
            feedback_rule = Live.MidiMap.CCFeedbackRule()
            feedback_rule.cc_no = control.message_identifier()
            feedback_rule.cc_value_map = tuple()
        elif (control.message_type() is MIDI_PB_TYPE):
            feedback_rule = Live.MidiMap.PitchBendFeedbackRule()
            feedback_rule.value_pair_map = tuple()
        assert (feedback_rule != None)
        feedback_rule.channel = control.message_channel()
        feedback_rule.delay_in_ms = feedback_delay
        if (control.message_type() is MIDI_NOTE_TYPE):
            Live.MidiMap.map_midi_note_with_feedback_map(self._midi_map_handle, parameter, control.message_channel(), control.message_identifier(), feedback_rule)
        elif (control.message_type() is MIDI_CC_TYPE):
            Live.MidiMap.map_midi_cc_with_feedback_map(self._midi_map_handle, parameter, control.message_channel(), control.message_identifier(), control.message_map_mode(), feedback_rule)
        elif (control.message_type() is MIDI_PB_TYPE):
            Live.MidiMap.map_midi_pitchbend_with_feedback_map(self._midi_map_handle, parameter, control.message_channel(), feedback_rule)
        Live.MidiMap.send_feedback_for_parameter(self._midi_map_handle, parameter)



    def _install_forwarding(self, control):
        assert self._in_build_midi_map
        assert (self._midi_map_handle != None)
        assert (control != None)
        assert isinstance(control, InputControlElement)
        if (control.message_type() is MIDI_NOTE_TYPE):
            Live.MidiMap.forward_midi_note(self._c_instance.handle(), self._midi_map_handle, control.message_channel(), control.message_identifier())
        elif (control.message_type() is MIDI_CC_TYPE):
            Live.MidiMap.forward_midi_cc(self._c_instance.handle(), self._midi_map_handle, control.message_channel(), control.message_identifier())
        elif (control.message_type() is MIDI_PB_TYPE):
            Live.MidiMap.forward_midi_pitchbend(self._midi_map_handle, control.message_channel())
        else:
            assert false
        forwarding_key = [control.status_byte()]
        if (control.message_type() is not MIDI_PB_TYPE):
            forwarding_key.append(control.message_identifier())
        assert (not (tuple(forwarding_key) in self._forwarding_registry.keys())), ('Registry key %s registered twice. Check Midi messages!' % str(forwarding_key))
        self._forwarding_registry[tuple(forwarding_key)] = control
        if (control.message_type() is MIDI_NOTE_TYPE):
            self._forwarding_registry[((control.status_byte() - 16),
             control.message_identifier())] = control



    def _translate_message(self, type, from_identifier, from_channel, to_identifier, to_channel):
        assert (type in (MIDI_CC_TYPE,
         MIDI_NOTE_TYPE))
        assert (from_identifier in range(128))
        assert (from_channel in range(16))
        assert (to_identifier in range(128))
        assert (to_channel in range(16))
        if (type == MIDI_CC_TYPE):
            self._c_instance.set_cc_translation(from_identifier, from_channel, to_identifier, to_channel)
        elif (type == MIDI_NOTE_TYPE):
            self._c_instance.set_note_translation(from_identifier, from_channel, to_identifier, to_channel)
        else:
            assert False



    def _set_session_highlight(self, track_offset, scene_offset, width, height):
        assert (track_offset in range(len(self.song().tracks)))
        assert (scene_offset in range(len(self.song().scenes)))
        assert (width > 0)
        assert (height > 0)
        self._c_instance.set_session_highlight(track_offset, scene_offset, width, height)



    def _on_track_list_changed(self):
        self.set_suppress_rebuild_requests(True)
        for component in self._components:
            component.on_track_list_changed()

        self.set_suppress_rebuild_requests(False)



    def _on_scene_list_changed(self):
        self.set_suppress_rebuild_requests(True)
        for component in self._components:
            component.on_scene_list_changed()

        self.set_suppress_rebuild_requests(False)



    def _on_selected_track_changed(self):
        self.set_suppress_rebuild_requests(True)
        for component in self._components:
            component.on_selected_track_changed()

        self.set_suppress_rebuild_requests(False)



    def _on_selected_scene_changed(self):
        self.set_suppress_rebuild_requests(True)
        for component in self._components:
            component.on_selected_scene_changed()

        self.set_suppress_rebuild_requests(False)



    def _toggle_lock(self):
        assert (self._device_component != None)
        self._c_instance.toggle_lock()



    def _refresh_displays(self):
        """ make sure the displays of the control surface display current data """
        for display in self._displays:
            display.update()





# local variables:
# tab-width: 4
