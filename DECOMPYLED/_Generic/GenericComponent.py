# emacs-mode: -*- python-*-
class GenericComponent:
    __module__ = __name__
    __doc__ = 'Baseclass for a subcomponent. \n  Just defines some handy shortcuts to the main scripts functions...\n  '

    def __init__(self, parent, controllers):
        self._GenericComponent__parent = parent
        self._GenericComponent__controllers = controllers



    def application(self):
        return self._GenericComponent__parent.application()



    def song(self):
        return self._GenericComponent__parent.song()



    def send_midi(self, midi_event_bytes):
        self._GenericComponent__parent.send_midi(midi_event_bytes)



    def request_rebuild_midi_map(self):
        self._GenericComponent__parent.request_rebuild_midi_map()



    def disconnect(self):
        pass


    def build_midi_map(self, script_handle, midi_map_handle):
        pass


    def refresh_state(self):
        pass


    def update_display(self):
        pass



# local variables:
# tab-width: 4
