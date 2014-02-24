# emacs-mode: -*- python-*-
from consts import *
class RemoteSLComponent:
    __module__ = __name__
    __doc__ = 'Baseclass for a subcomponent of the RemoteSL. \n  Just defines some handy shortcuts to the main scripts functions...\n  for more details about the methods, see the RemoteSLs doc strings\n  '

    def __init__(self, remote_sl_parent):
        self._RemoteSLComponent__parent = remote_sl_parent



    def application(self):
        return self._RemoteSLComponent__parent.application()



    def song(self):
        return self._RemoteSLComponent__parent.song()



    def send_midi(self, midi_event_bytes):
        self._RemoteSLComponent__parent.send_midi(midi_event_bytes)



    def request_rebuild_midi_map(self):
        self._RemoteSLComponent__parent.request_rebuild_midi_map()



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
