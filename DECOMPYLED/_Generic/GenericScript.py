# emacs-mode: -*- python-*-
import Live
import MidiRemoteScript
from consts import *
from GenericDeviceControl import GenericDeviceControl
from GenericTransportControl import GenericTransportControl
from GenericMixerControl import GenericMixerControl
class GenericScript:
    __module__ = __name__
    __doc__ = ' A generic script class with predefined behaviour. \n      It can be customised to use/not use certain controls on instantiation.\n  '

    def __init__(self, c_instance, macro_map_mode, volume_map_mode, device_controls, transport_controls, volume_controls, trackarm_controls, bank_controls, descriptions = None, mixer_options = None):
        self._GenericScript__c_instance = c_instance
        self._GenericScript__macro_map_mode = macro_map_mode
        self._GenericScript__volume_map_mode = volume_map_mode
        self._GenericScript__suggested_input_port = str('')
        self._GenericScript__suggested_output_port = str('')
        self._GenericScript__global_channel = 0
        self._GenericScript__pad_translation = ()
        if descriptions:
            if (list(descriptions.keys()).count('INPUTPORT') > 0):
                self._GenericScript__suggested_input_port = descriptions['INPUTPORT']
            if (list(descriptions.keys()).count('OUTPUTPORT') > 0):
                self._GenericScript__suggested_output_port = descriptions['OUTPUTPORT']
            if (list(descriptions.keys()).count('CHANNEL') > 0):
                self._GenericScript__global_channel = descriptions['CHANNEL']
                if (self._GenericScript__global_channel < 0):
                    self._GenericScript__global_channel = 0
            if (list(descriptions.keys()).count('PAD_TRANSLATION') > 0):
                self._GenericScript__pad_translation = descriptions['PAD_TRANSLATION']
        self._GenericScript__device = 0
        self._GenericScript__transport = 0
        self._GenericScript__mixer = 0
        if device_controls:
            self._GenericScript__device = GenericDeviceControl(self, device_controls, macro_map_mode, bank_controls)
        if transport_controls:
            self._GenericScript__transport = GenericTransportControl(self, transport_controls)
        if (volume_controls and trackarm_controls):
            self._GenericScript__mixer = GenericMixerControl(self, volume_controls, volume_map_mode, trackarm_controls, mixer_options)
        self.song().add_tracks_listener(self._GenericScript__on_tracks_changed)
        self._GenericScript__transport_controls = transport_controls
        self._GenericScript__trackarm_controls = trackarm_controls
        self._GenericScript__bank_controls = bank_controls
        self._GenericScript__volume_controls = volume_controls
        self._GenericScript__device_controls = device_controls



    def application(self):
        """returns a reference to the application that we are running in
    """
        return Live.Application.get_application()



    def song(self):
        """returns a reference to the Live song instance that we control
    """
        return self._GenericScript__c_instance.song()



    def disconnect(self):
        """Live -> Script 
    Called right before we get disconnected from Live.
    """
        self.song().remove_tracks_listener(self._GenericScript__on_tracks_changed)
        if self._GenericScript__device:
            self._GenericScript__device.disconnect()
        if self._GenericScript__transport:
            self._GenericScript__transport.disconnect()
        if self._GenericScript__mixer:
            self._GenericScript__mixer.disconnect()



    def can_lock_to_devices(self):
        return True



    def suggest_input_port(self):
        """Live -> Script
    Live can ask the script for an input port name to find a suitable one.
    """
        return self._GenericScript__suggested_input_port



    def suggest_output_port(self):
        """Live -> Script
    Live can ask the script for an output port name to find a suitable one.
    """
        return self._GenericScript__suggested_output_port



    def suggest_map_mode(self, cc_no, channel):
        """Live -> Script
    Live can ask the script for a suitable mapping mode for a given CC.
    """
        suggested_map_mode = -1
        if (list(self._GenericScript__volume_controls).count(cc_no) > 0):
            suggested_map_mode = self._GenericScript__volume_map_mode
        elif (list(self._GenericScript__device_controls).count(cc_no) > 0):
            suggested_map_mode = self._GenericScript__macro_map_mode
        return suggested_map_mode



    def supports_pad_translation(self):
        return (len(self._GenericScript__pad_translation) > 0)



    def global_channel(self):
        return self._GenericScript__global_channel



    def show_message(self, message):
        self._GenericScript__c_instance.show_message(message)



    def instance_identifier(self):
        return self._GenericScript__c_instance.instance_identifier()



    def restore_bank(self, bank):
        if self._GenericScript__device:
            self._GenericScript__device.restore_bank(bank)



    def connect_script_instances(self, instanciated_scripts):
        """Called by the Application as soon as all scripts are initialized.
    You can connect yourself to other running scripts here, as we do it
    connect the extension modules (MackieControlXTs).
    """
        pass


    def request_rebuild_midi_map(self):
        """Script -> Live
    When the internal MIDI controller has changed in a way that you need to rebuild
    the MIDI mappings, request a rebuild by calling this function
    This is processed as a request, to be sure that its not too often called, because
    its time-critical.
    """
        self._GenericScript__c_instance.request_rebuild_midi_map()



    def send_midi(self, midi_event_bytes):
        """Script -> Live
    Use this function to send MIDI events through Live to the _real_ MIDI devices
    that this script is assigned to.
    """
        self._GenericScript__c_instance.send_midi(midi_event_bytes)



    def toggle_lock(self):
        """Script -> Live
    Use this function to toggle the script's lock on devices
    """
        self._GenericScript__c_instance.toggle_lock()



    def refresh_state(self):
        """Live -> Script
    Send out MIDI to completely update the attached MIDI controller.
    Will be called when requested by the user, after for example having reconnected 
    the MIDI cables...
    """
        pass


    def build_midi_map(self, midi_map_handle):
        """Live -> Script
    Build DeviceParameter Mappings, that are processed in Audio time, or
    forward MIDI messages explicitly to our receive_midi_functions.
    Which means that when you are not forwarding MIDI, nor mapping parameters, you will 
    never get any MIDI messages at all.
    """
        script_handle = self._GenericScript__c_instance.handle()
        if self._GenericScript__device:
            self._GenericScript__device.build_midi_map(script_handle, midi_map_handle)
        if self._GenericScript__transport:
            self._GenericScript__transport.build_midi_map(script_handle, midi_map_handle)
        if self._GenericScript__mixer:
            self._GenericScript__mixer.build_midi_map(script_handle, midi_map_handle)
        if (len(self._GenericScript__pad_translation) > 0):
            self._GenericScript__c_instance.set_pad_translation(self._GenericScript__pad_translation)



    def update_display(self):
        """Live -> Script
    Aka on_timer. Called every 100 ms and should be used to update display relevant
    parts of the controller
    """
        if self._GenericScript__transport:
            self._GenericScript__transport.refresh_state()



    def receive_midi(self, midi_bytes):
        """Live -> Script
    MIDI messages are only received through this function, when explicitly 
    forwarded in 'build_midi_map'.
    """
        if ((midi_bytes[0] & 240) == CC_STATUS):
            channel = (midi_bytes[0] & 15)
            cc_no = midi_bytes[1]
            cc_value = midi_bytes[2]
            if (list(self._GenericScript__transport_controls.values()).count(cc_no) > 0):
                if self._GenericScript__transport:
                    self._GenericScript__transport.receive_midi_cc(cc_no, cc_value)
            if (list(self._GenericScript__trackarm_controls).count(cc_no) > 0):
                if self._GenericScript__mixer:
                    self._GenericScript__mixer.receive_midi_cc(cc_no, cc_value)
            if (list(self._GenericScript__bank_controls.values()).count(cc_no) > 0):
                if self._GenericScript__device:
                    self._GenericScript__device.receive_midi_cc(cc_no, cc_value)
        elif (midi_bytes[0] == 240):
            pass



    def lock_to_device(self, device):
        if self._GenericScript__device:
            self._GenericScript__device.lock_to_device(device)



    def unlock_from_device(self, device):
        if self._GenericScript__device:
            self._GenericScript__device.unlock_from_device(device)



    def __on_tracks_changed(self):
        self.request_rebuild_midi_map()



    def set_appointed_device(self, device):
        """Live -> Script
    Live can tell the script which device to use if it is not locked
    This is a substitute mechanism for the listeners used by older scripts
    """
        self._GenericScript__device.set_appointed_device(device)




# local variables:
# tab-width: 4
