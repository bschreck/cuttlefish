# emacs-mode: -*- python-*-
class ControlElement(object):
    __module__ = __name__
    __doc__ = ' Base class for all classes representing control elements on a controller '
    _register_control_callback = None
    _send_midi_callback = None

    def set_register_control_callback(callback):
        """ set callback for sending midi """
        assert (dir(callback).count('im_func') is 1)
        ControlElement._register_control_callback = callback


    set_register_control_callback = staticmethod(set_register_control_callback)

    def set_send_midi_callback(callback):
        """ set callback for sending midi """
        assert (dir(callback).count('im_func') is 1)
        ControlElement._send_midi_callback = callback


    set_send_midi_callback = staticmethod(set_send_midi_callback)

    def release_class_attributes():
        """ release all set objects to not have dependencies """
        ControlElement._send_midi_callback = None
        ControlElement._register_control_callback = None


    release_class_attributes = staticmethod(release_class_attributes)

    def __init__(self):
        assert (ControlElement._register_control_callback != None)
        assert (ControlElement._send_midi_callback != None)
        object.__init__(self)
        self._send_midi = ControlElement._send_midi_callback
        ControlElement._register_control_callback(self)



    def disconnect(self):
        self.reset()



    def send_midi(self, message):
        assert (message != None)
        assert isinstance(message, tuple)
        self._send_midi(message)



    def clear_send_cache(self):
        pass


    def reset(self):
        debug_print('reset is abstract. Forgot to override it?')
        assert False




# local variables:
# tab-width: 4
