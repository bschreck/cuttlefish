# emacs-mode: -*- python-*-
import Live
from GenericComponent import GenericComponent
from consts import *
from Devices import *
class GenericDeviceControl(GenericComponent):
    __module__ = __name__
    __doc__ = ' Class representing the Encoder section on the Midi controller '

    def __init__(self, parent, controllers, map_mode, function_dict):
        self._GenericDeviceControl__parent = parent
        self._GenericDeviceControl__parameter_controllers = controllers
        self._GenericDeviceControl__function_dict = function_dict
        if map_mode:
            self._GenericDeviceControl__map_mode = map_mode
        else:
            self._GenericDeviceControl__map_mode = Live.MidiMap.MapMode.absolute
        self._GenericDeviceControl__device = self._GenericDeviceControl__parent.song().appointed_device
        self._GenericDeviceControl__device_locked = False
        self._GenericDeviceControl__show_bank = False
        self._GenericDeviceControl__bank = 0



    def build_midi_map(self, script_handle, midi_map_handle):
        assignment_necessary = True
        if (not (self._GenericDeviceControl__device == None)):
            device_parameters = self._GenericDeviceControl__device.parameters
            device_bank = 0
            param_bank = 0
            if (number_of_parameter_banks(self._GenericDeviceControl__device) > self._GenericDeviceControl__bank):
                for index in range(8):
                    bank_key = ('BANK' + str((index + 1)))
                    if (bank_key in self._GenericDeviceControl__function_dict.keys()):
                        cc_no = self._GenericDeviceControl__function_dict[bank_key]
                        status = STATUS_OFF
                        if (index == self._GenericDeviceControl__bank):
                            status = STATUS_ON
                        if (cc_no in range(128)):
                            self._GenericDeviceControl__parent.send_midi((CC_STATUS,
                             cc_no,
                             status))

                self._GenericDeviceControl__report_bank()
                if self._GenericDeviceControl__can_switch_banks():
                    if (self._GenericDeviceControl__device.class_name in DEVICE_DICT.keys()):
                        device_bank = DEVICE_DICT[self._GenericDeviceControl__device.class_name]
                        param_bank = device_bank[self._GenericDeviceControl__bank]
                elif (self._GenericDeviceControl__device.class_name in DEVICE_BOB_DICT.keys()):
                    device_bank = DEVICE_BOB_DICT[self._GenericDeviceControl__device.class_name]
                    param_bank = device_bank[0]
                feedback_rule = Live.MidiMap.CCFeedbackRule()
                for encoder in range(8):
                    parameter_index = (encoder + (self._GenericDeviceControl__bank * 8))
                    mapping_details = self._GenericDeviceControl__parameter_controllers[encoder]
                    mapping_cc = -1
                    mapping_channel = -1
                    if (not isinstance(mapping_details, tuple)):
                        mapping_cc = mapping_details
                        mapping_channel = self._GenericDeviceControl__parent.global_channel()
                    else:
                        mapping_cc = mapping_details[0]
                        mapping_channel = mapping_details[1]
                        if (not (mapping_channel in range(16))):
                            mapping_channel = self._GenericDeviceControl__parent.global_channel()
                    if ((mapping_cc in range(128)) and (mapping_channel in range(16))):
                        feedback_rule.channel = 0
                        feedback_rule.cc_no = mapping_cc
                        feedback_rule.cc_value_map = tuple()
                        feedback_rule.delay_in_ms = -1.0
                        parameter = 0
                        if param_bank:
                            if (param_bank[encoder] != ''):
                                parameter = get_parameter_by_name(self._GenericDeviceControl__device, param_bank[encoder])
                        elif (len(device_parameters) > parameter_index):
                            parameter = device_parameters[parameter_index]
                        else:
                            break
                        if parameter:
                            Live.MidiMap.map_midi_cc_with_feedback_map(midi_map_handle, parameter, mapping_channel, mapping_cc, self._GenericDeviceControl__map_mode, feedback_rule)
                            Live.MidiMap.send_feedback_for_parameter(midi_map_handle, parameter)
                    else:
                        break

        else:
            self.disconnect()
        if self._GenericDeviceControl__function_dict:
            for channel in range(NUM_CHANNELS):
                for cc in list(self._GenericDeviceControl__function_dict.values()):
                    if (cc >= 0):
                        Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, channel, cc)





    def receive_midi_cc(self, cc_no, cc_value):
        if (cc_value > 0):
            if (list(self._GenericDeviceControl__function_dict.values()).count(cc_no) > 0):
                new_bank = self._GenericDeviceControl__bank
                bank_changed = False
                if (cc_no == self._GenericDeviceControl__function_dict['TOGGLELOCK']):
                    self._GenericDeviceControl__device_locked = False
                    self._GenericDeviceControl__parent.toggle_lock()
                if (cc_no == self._GenericDeviceControl__function_dict['NEXTBANK']):
                    if (number_of_parameter_banks(self._GenericDeviceControl__device) > (self._GenericDeviceControl__bank + 1)):
                        new_bank += 1
                        bank_changed = True
                if (cc_no == self._GenericDeviceControl__function_dict['PREVBANK']):
                    if (self._GenericDeviceControl__bank > 0):
                        new_bank -= 1
                        bank_changed = True
                if (cc_no == self._GenericDeviceControl__function_dict['BANK1']):
                    if (number_of_parameter_banks(self._GenericDeviceControl__device) > 0):
                        new_bank = 0
                        bank_changed = True
                if (cc_no == self._GenericDeviceControl__function_dict['BANK2']):
                    if (number_of_parameter_banks(self._GenericDeviceControl__device) > 1):
                        new_bank = 1
                        bank_changed = True
                if (cc_no == self._GenericDeviceControl__function_dict['BANK3']):
                    if (number_of_parameter_banks(self._GenericDeviceControl__device) > 2):
                        new_bank = 2
                        bank_changed = True
                if (cc_no == self._GenericDeviceControl__function_dict['BANK4']):
                    if (number_of_parameter_banks(self._GenericDeviceControl__device) > 3):
                        new_bank = 3
                        bank_changed = True
                if (cc_no == self._GenericDeviceControl__function_dict['BANK5']):
                    if (number_of_parameter_banks(self._GenericDeviceControl__device) > 4):
                        new_bank = 4
                        bank_changed = True
                if (cc_no == self._GenericDeviceControl__function_dict['BANK6']):
                    if (number_of_parameter_banks(self._GenericDeviceControl__device) > 5):
                        new_bank = 5
                        bank_changed = True
                if (cc_no == self._GenericDeviceControl__function_dict['BANK7']):
                    if (number_of_parameter_banks(self._GenericDeviceControl__device) > 6):
                        new_bank = 6
                        bank_changed = True
                if (cc_no == self._GenericDeviceControl__function_dict['BANK8']):
                    if (number_of_parameter_banks(self._GenericDeviceControl__device) > 7):
                        new_bank = 7
                        bank_changed = True
                if bank_changed:
                    self._GenericDeviceControl__show_bank = True
                    if self._GenericDeviceControl__device_locked:
                        self._GenericDeviceControl__device.store_chosen_bank(self._GenericDeviceControl__parent.instance_identifier(), new_bank)
                    else:
                        self._GenericDeviceControl__bank = new_bank
                        self._GenericDeviceControl__parent.request_rebuild_midi_map()



    def __report_bank(self):
        if self._GenericDeviceControl__show_bank:
            self._GenericDeviceControl__show_bank = False
            if self._GenericDeviceControl__can_switch_banks():
                if (self._GenericDeviceControl__device.class_name in DEVICE_DICT.keys()):
                    if (self._GenericDeviceControl__device.class_name in BANK_NAME_DICT.keys()):
                        bank_names = BANK_NAME_DICT[self._GenericDeviceControl__device.class_name]
                        if (bank_names and (len(bank_names) > self._GenericDeviceControl__bank)):
                            bank_name = bank_names[self._GenericDeviceControl__bank]
                            self._GenericDeviceControl__show_bank_select(bank_name)
                    else:
                        self._GenericDeviceControl__show_bank_select('Best of Parameters')
                else:
                    self._GenericDeviceControl__show_bank_select(('Bank' + str((self._GenericDeviceControl__bank + 1))))
            else:
                self._GenericDeviceControl__show_bank_select('Best of Parameters')



    def lock_to_device(self, device):
        if device:
            self._GenericDeviceControl__device_locked = True
            if (not (device == self._GenericDeviceControl__device)):
                self._GenericDeviceControl__bank = 0
            self._GenericDeviceControl__show_bank = False
            self._GenericDeviceControl__device = device
            self._GenericDeviceControl__parent.request_rebuild_midi_map()



    def unlock_from_device(self, device):
        if (device and (device == self._GenericDeviceControl__device)):
            self._GenericDeviceControl__device_locked = False
            if (not (self._GenericDeviceControl__parent.song().appointed_device == self._GenericDeviceControl__device)):
                self._GenericDeviceControl__parent.request_rebuild_midi_map()



    def set_appointed_device(self, device):
        if self._GenericDeviceControl__device_locked:
            self._GenericDeviceControl__device_locked = False
        if (not (device == self._GenericDeviceControl__device)):
            self._GenericDeviceControl__bank = 0
        self._GenericDeviceControl__show_bank = False
        self._GenericDeviceControl__device = device
        self._GenericDeviceControl__parent.request_rebuild_midi_map()



    def restore_bank(self, bank):
        if (self._GenericDeviceControl__can_switch_banks() and (self._GenericDeviceControl__device_locked and ((self._GenericDeviceControl__bank != bank) and (self._GenericDeviceControl__device and (number_of_parameter_banks(self._GenericDeviceControl__device) > bank))))):
            self._GenericDeviceControl__bank = bank
            self._GenericDeviceControl__parent.request_rebuild_midi_map()



    def disconnect(self):
        for mapping_info in self._GenericDeviceControl__parameter_controllers:
            cc_no = -1
            if (not isinstance(mapping_info, tuple)):
                cc_no = mapping_info
            else:
                cc_no = mapping_info[0]
            if (cc_no in range(128)):
                self._GenericDeviceControl__parent.send_midi((CC_STATUS,
                 cc_no,
                 STATUS_OFF))

        for cc_no in list(self._GenericDeviceControl__function_dict.values()):
            if (cc_no in range(128)):
                self._GenericDeviceControl__parent.send_midi((CC_STATUS,
                 cc_no,
                 STATUS_OFF))




    def __can_switch_banks(self):
        result = False
        if (('NEXTBANK' in self._GenericDeviceControl__function_dict.keys()) and ('PREVBANK' in self._GenericDeviceControl__function_dict.keys())):
            next_cc = self._GenericDeviceControl__function_dict['NEXTBANK']
            prev_cc = self._GenericDeviceControl__function_dict['PREVBANK']
            if ((next_cc in range(128)) and (prev_cc in range(128))):
                result = True
        if (not result):
            for i in range(8):
                bank_key = ('BANK' + str((i + 1)))
                if (bank_key in self._GenericDeviceControl__function_dict.keys()):
                    if (self._GenericDeviceControl__function_dict[bank_key] in range(128)):
                        result = True
                        break

        return result



    def __show_bank_select(self, bank_name):
        if self._GenericDeviceControl__device:
            self._GenericDeviceControl__parent.show_message(str(((self._GenericDeviceControl__device.name + ' Bank: ') + bank_name)))




# local variables:
# tab-width: 4
