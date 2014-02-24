# emacs-mode: -*- python-*-
import Live
from CompoundComponent import CompoundComponent
from ControlSurfaceComponent import ControlSurfaceComponent
from ClipSlotComponent import ClipSlotComponent
from ButtonElement import ButtonElement
class SceneComponent(CompoundComponent):
    __module__ = __name__
    __doc__ = ' Class representing a scene in Live '

    def __init__(self, num_slots):
        assert (num_slots != None)
        assert isinstance(num_slots, int)
        assert (num_slots >= 0)
        CompoundComponent.__init__(self)
        self._scene = None
        self._clip_slots = []
        for index in range(num_slots):
            new_slot = ClipSlotComponent()
            self._clip_slots.append(new_slot)
            self.register_components(new_slot)

        self._launch_button = None
        self._track_offset = 0



    def disconnect(self):
        CompoundComponent.disconnect(self)
        self._scene = None
        self._clip_slots = None
        if (self._launch_button != None):
            self._launch_button.unregister_value_notification(self._launch_value)
            self._launch_button = None



    def on_enabled_changed(self):
        self.update()



    def on_track_list_changed(self):
        self.update()



    def set_scene(self, scene):
        assert ((scene == None) or isinstance(scene, Live.Scene.Scene))
        if (scene != self._scene):
            self._scene = scene
            self.update()



    def set_launch_button(self, button):
        assert ((button == None) or isinstance(button, ButtonElement))
        if (button != self._launch_button):
            if (self._launch_button != None):
                self._launch_button.unregister_value_notification(self._launch_value)
            self._launch_button = button
            if (self._launch_button != None):
                self._launch_button.register_value_notification(self._launch_value)



    def set_track_offset(self, offset):
        assert (offset != None)
        assert isinstance(offset, int)
        assert (offset in range(len(self.song().tracks)))
        if (offset != self._track_offset):
            self._track_offset = offset
            self.update()



    def clip_slot(self, index):
        assert (index != None)
        assert isinstance(index, int)
        assert (index in range(len(self._clip_slots)))
        return self._clip_slots[index]



    def update(self):
        if ((self._scene != None) and self.is_enabled()):
            for slot in self._clip_slots:
                clip_index = (self._track_offset + self._clip_slots.index(slot))
                if (len(self._scene.clip_slots) > clip_index):
                    slot.set_clip_slot(self._scene.clip_slots[clip_index])
                else:
                    slot.set_clip_slot(None)

        else:
            for slot in self._clip_slots:
                slot.set_clip_slot(None)




    def _launch_value(self, value):
        assert (self._launch_button != None)
        assert (value != None)
        assert isinstance(value, int)
        if ((self._scene != None) and self.is_enabled()):
            if ((value is not 0) or (not self._launch_button.is_momentary())):
                self._scene.fire()




# local variables:
# tab-width: 4
