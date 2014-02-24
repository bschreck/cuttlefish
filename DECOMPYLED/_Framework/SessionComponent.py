# emacs-mode: -*- python-*-
import Live
from CompoundComponent import CompoundComponent
from ControlSurfaceComponent import ControlSurfaceComponent
from SceneComponent import SceneComponent
from MixerComponent import MixerComponent
from ButtonElement import ButtonElement
class SessionComponent(CompoundComponent):
    __module__ = __name__
    __doc__ = " Class encompassing several scene to cover a defined section of Live's session "
    _session_highlighting_callback = None

    def set_highlighting_callback(callback):
        """ set callback for setting the session highlight """
        assert (dir(callback).count('im_func') is 1)
        SessionComponent._session_highlighting_callback = callback


    set_highlighting_callback = staticmethod(set_highlighting_callback)

    def release_class_attributes():
        """ release all set objects to not have dependencies """
        SessionComponent._session_highlighting_callback = None


    release_class_attributes = staticmethod(release_class_attributes)

    def __init__(self, num_tracks, num_scenes):
        assert (SessionComponent._session_highlighting_callback != None)
        assert isinstance(num_tracks, int)
        assert (num_tracks >= 0)
        assert isinstance(num_scenes, int)
        assert (num_scenes >= 0)
        CompoundComponent.__init__(self)
        self._track_offset = -1
        self._scene_offset = -1
        self._num_tracks = num_tracks
        self._bank_up_button = None
        self._bank_down_button = None
        self._bank_right_button = None
        self._bank_left_button = None
        self._stop_all_button = None
        self._next_scene_button = None
        self._prev_scene_button = None
        self._stop_track_clip_buttons = None
        self._offset_callback = None
        self._highlighting_callback = SessionComponent._session_highlighting_callback
        self._show_highlight = ((num_tracks > 0) and (num_scenes > 0))
        self._selected_scene = SceneComponent(self._num_tracks)
        self.on_selected_scene_changed()
        self.register_components(self._selected_scene)
        self._scenes = []
        for index in range(num_scenes):
            self._scenes.append(SceneComponent(self._num_tracks))
            self.register_components(self._scenes[index])

        self._mixer = None
        self.set_offsets(0, 0)



    def disconnect(self):
        CompoundComponent.disconnect(self)
        self._master_strip = None
        self._channel_strips = None
        self._offset_callback = None
        if (self._bank_up_button != None):
            self._bank_up_button.unregister_value_notification(self._bank_up_value)
            self._bank_up_button = None
        if (self._bank_down_button != None):
            self._bank_down_button.unregister_value_notification(self._bank_down_value)
            self._bank_down_button = None
        if (self._bank_right_button != None):
            self._bank_right_button.unregister_value_notification(self._bank_right_value)
            self._bank_right_button = None
        if (self._bank_left_button != None):
            self._bank_left_button.unregister_value_notification(self._bank_left_value)
            self._bank_left_button = None
        if (self._stop_all_button != None):
            self._stop_all_button.unregister_value_notification(self._stop_all_value)
            self._stop_all_button = None
        if (self._next_scene_button != None):
            self._next_scene_button.unregister_value_notification(self._next_scene_value)
            self._next_scene_button = None
        if (self._prev_scene_button != None):
            self._prev_scene_button.unregister_value_notification(self._prev_scene_value)
            self._prev_scene_button = None
        self._stop_track_clip_buttons = None



    def scene(self, index):
        assert isinstance(index, int)
        assert ((index >= 0) and (index < len(self._scenes)))
        return self._scenes[index]



    def selected_scene(self):
        return self._selected_scene



    def set_scene_bank_buttons(self, up_button, down_button):
        assert ((up_button == None) or isinstance(up_button, ButtonElement))
        assert ((down_button == None) or isinstance(down_button, ButtonElement))
        do_update = False
        if (up_button is not self._bank_up_button):
            do_update = True
            if (self._bank_up_button != None):
                self._bank_up_button.unregister_value_notification(self._bank_up_value)
            self._bank_up_button = up_button
            if (self._bank_up_button != None):
                self._bank_up_button.register_value_notification(self._bank_up_value)
        if (down_button is not self._bank_down_button):
            do_update = True
            if (self._bank_down_button != None):
                self._bank_down_button.unregister_value_notification(self._bank_down_value)
            self._bank_down_button = down_button
            if (self._bank_down_button != None):
                self._bank_down_button.register_value_notification(self._bank_down_value)
        if do_update:
            self.update()



    def set_track_bank_buttons(self, right_button, left_button):
        assert ((right_button == None) or isinstance(right_button, ButtonElement))
        assert ((left_button == None) or isinstance(left_button, ButtonElement))
        do_update = False
        if (right_button is not self._bank_right_button):
            do_update = True
            if (self._bank_right_button != None):
                self._bank_right_button.unregister_value_notification(self._bank_right_value)
            self._bank_right_button = right_button
            if (self._bank_right_button != None):
                self._bank_right_button.register_value_notification(self._bank_right_value)
        if (left_button is not self._bank_left_button):
            do_update = True
            if (self._bank_left_button != None):
                self._bank_left_button.unregister_value_notification(self._bank_left_value)
            self._bank_left_button = left_button
            if (self._bank_left_button != None):
                self._bank_left_button.register_value_notification(self._bank_left_value)
        if do_update:
            self.update()



    def set_stop_all_clips_button(self, button):
        assert ((button == None) or isinstance(button, ButtonElement))
        if (self._stop_all_button != None):
            self._stop_all_button.unregister_value_notification(self._stop_all_value)
        self._stop_all_button = button
        if (self._stop_all_button != None):
            self._stop_all_button.register_value_notification(self._stop_all_value)



    def set_stop_track_clip_buttons(self, buttons):
        assert ((buttons == None) or (isinstance(buttons, tuple) and (len(buttons) == self._num_tracks)))
        if (self._stop_track_clip_buttons != None):
            for button in self._stop_track_clip_buttons:
                button.unregister_value_notification(self._stop_track_value)

        self._stop_track_clip_buttons = buttons
        if (self._stop_track_clip_buttons != None):
            for button in self._stop_track_clip_buttons:
                assert isinstance(button, ButtonElement)
                button.register_value_notification(self._stop_track_value, identify_sender=True)




    def set_select_buttons(self, next_button, prev_button):
        assert ((next_button == None) or isinstance(next_button, ButtonElement))
        assert ((prev_button == None) or isinstance(prev_button, ButtonElement))
        do_update = False
        if (next_button is not self._next_scene_button):
            do_update = True
            if (self._next_scene_button != None):
                self._next_scene_button.unregister_value_notification(self._next_scene_value)
            self._next_scene_button = next_button
            if (self._next_scene_button != None):
                self._next_scene_button.register_value_notification(self._next_scene_value)
        if (prev_button is not self._prev_scene_button):
            do_update = True
            if (self._prev_scene_button != None):
                self._prev_scene_button.unregister_value_notification(self._prev_scene_value)
            self._prev_scene_button = prev_button
            if (self._prev_scene_button != None):
                self._prev_scene_button.register_value_notification(self._prev_scene_value)
        if do_update:
            self.on_selected_scene_changed()



    def set_mixer(self, mixer):
        assert ((mixer == None) or isinstance(mixer, MixerComponent))
        self._mixer = mixer
        if (self._mixer != None):
            self._mixer.set_track_offset(self.track_offset())



    def set_offsets(self, track_offset, scene_offset):
        assert isinstance(track_offset, int)
        assert (track_offset >= 0)
        assert isinstance(scene_offset, int)
        assert (scene_offset >= 0)
        do_update = False
        if (track_offset is not self._track_offset):
            if (len(self.song().tracks) > track_offset):
                do_update = True
                self._track_offset = track_offset
                if (self._mixer != None):
                    self._mixer.set_track_offset(self.track_offset())
        if (scene_offset is not self._scene_offset):
            if (len(self.song().scenes) > scene_offset):
                do_update = True
                self._scene_offset = scene_offset
        if do_update:
            self._reassign_scenes()
            if (self._offset_callback != None):
                self._offset_callback()
            if (self._show_highlight and ((self.width() > 0) and (self.height() > 0))):
                self._highlighting_callback(self._track_offset, self._scene_offset, self.width(), self.height())



    def set_offset_callback(self, callback):
        assert (callback != None)
        assert (dir(callback).count('im_func') is 1)
        self._offset_callback = callback



    def set_show_highlight(self, show_highlight):
        assert isinstance(show_highlight, type(False))
        if (self._show_highlight != show_highlight):
            self._show_highlight = show_highlight
            if self._show_highlight:
                self._highlighting_callback(self._track_offset, self._scene_offset, self.width(), self.height())
            else:
                self._highlighting_callback(-1, -1, -1, -1)



    def on_enabled_changed(self):
        self.update()



    def on_scene_list_changed(self):
        self._reassign_scenes()



    def on_track_list_changed(self):
        if (self.track_offset() >= len(self.song().tracks)):
            self.set_offsets((self.track_offset() - 1), self.scene_offset())



    def on_selected_scene_changed(self):
        if (self.scene_offset() >= len(self.song().scenes)):
            self.set_offsets(self.track_offset(), (self.scene_offset() - 1))
        if (self._selected_scene != None):
            self._selected_scene.set_scene(self.song().view.selected_scene)
            self.update()



    def width(self):
        return self._num_tracks



    def height(self):
        return len(self._scenes)



    def track_offset(self):
        return self._track_offset



    def scene_offset(self):
        return self._scene_offset



    def update(self):
        if self.is_enabled():
            scenes = self.song().scenes
            tracks = self.song().tracks
            selected_scene = self.song().view.selected_scene
            if (self._bank_down_button != None):
                if (self._scene_offset > 0):
                    self._bank_down_button.turn_on()
                else:
                    self._bank_down_button.turn_off()
            if (self._bank_up_button != None):
                increment = 1
                if (len(scenes) > (self._scene_offset + increment)):
                    self._bank_up_button.turn_on()
                else:
                    self._bank_up_button.turn_off()
            if (self._bank_left_button != None):
                if (self._track_offset > 0):
                    self._bank_left_button.turn_on()
                else:
                    self._bank_left_button.turn_off()
            if (self._bank_right_button != None):
                increment = 1
                if (len(tracks) > (self._track_offset + increment)):
                    self._bank_right_button.turn_on()
                else:
                    self._bank_right_button.turn_off()
            if (self._next_scene_button != None):
                if (selected_scene != self.song().scenes[-1]):
                    self._next_scene_button.turn_on()
                else:
                    self._next_scene_button.turn_off()
            if (self._prev_scene_button != None):
                if (selected_scene != self.song().scenes[0]):
                    self._prev_scene_button.turn_on()
                else:
                    self._prev_scene_button.turn_off()
        else:
            if (self._bank_up_button != None):
                self._bank_up_button.turn_off()
            if (self._bank_down_button != None):
                self._bank_down_button.turn_off()
            if (self._bank_right_button != None):
                self._bank_right_button.turn_off()
            if (self._bank_left_button != None):
                self._bank_left_button.turn_off()
            if (self._next_scene_button != None):
                self._next_scene_button.turn_off()
            if (self._prev_scene_button != None):
                self._prev_scene_button.turn_off()



    def _reassign_scenes(self):
        scenes = self.song().scenes
        for index in range(len(self._scenes)):
            scene_index = (self._scene_offset + index)
            if (len(scenes) > scene_index):
                self._scenes[index].set_scene(scenes[scene_index])
                self._scenes[index].set_track_offset(self._track_offset)
            else:
                self._scenes[index].set_scene(None)

        if (self._selected_scene != None):
            self._selected_scene.set_track_offset(self._track_offset)
        self.update()



    def _bank_up_value(self, value):
        assert isinstance(value, int)
        assert (self._bank_up_button != None)
        if self.is_enabled():
            if ((value is not 0) or (not self._bank_up_button.is_momentary())):
                increment = 1
                self.set_offsets(self._track_offset, (self._scene_offset + increment))



    def _bank_down_value(self, value):
        assert isinstance(value, int)
        assert (self._bank_down_button != None)
        if self.is_enabled():
            if ((value is not 0) or (not self._bank_down_button.is_momentary())):
                increment = 1
                self.set_offsets(self._track_offset, max(0, (self._scene_offset - increment)))



    def _bank_right_value(self, value):
        assert isinstance(value, int)
        assert (self._bank_right_button != None)
        if self.is_enabled():
            if ((value is not 0) or (not self._bank_right_button.is_momentary())):
                increment = 1
                self.set_offsets((self._track_offset + increment), self._scene_offset)



    def _bank_left_value(self, value):
        assert isinstance(value, int)
        assert (self._bank_left_button != None)
        if self.is_enabled():
            if ((value is not 0) or (not self._bank_left_button.is_momentary())):
                increment = 1
                self.set_offsets(max(0, (self._track_offset - increment)), self._scene_offset)



    def _stop_all_value(self, value):
        assert (self._stop_all_button != None)
        assert isinstance(value, int)
        if self.is_enabled():
            if ((value is not 0) or (not self._stop_all_button.is_momentary())):
                self.song().stop_all_clips()



    def _next_scene_value(self, value):
        assert (self._next_scene_button != None)
        assert (value != None)
        assert isinstance(value, int)
        if self.is_enabled():
            if ((value is not 0) or (not self._next_scene_button.is_momentary())):
                selected_scene = self.song().view.selected_scene
                all_scenes = self.song().scenes
                if (selected_scene != all_scenes[-1]):
                    index = list(all_scenes).index(selected_scene)
                    self.song().view.selected_scene = all_scenes[(index + 1)]



    def _prev_scene_value(self, value):
        assert (self._prev_scene_button != None)
        assert (value != None)
        assert isinstance(value, int)
        if self.is_enabled():
            if ((value is not 0) or (not self._prev_scene_button.is_momentary())):
                selected_scene = self.song().view.selected_scene
                all_scenes = self.song().scenes
                if (selected_scene != all_scenes[0]):
                    index = list(all_scenes).index(selected_scene)
                    self.song().view.selected_scene = all_scenes[(index - 1)]



    def _stop_track_value(self, value, sender):
        assert (self._stop_track_clip_buttons != None)
        assert (list(self._stop_track_clip_buttons).count(sender) == 1)
        assert (value in range(128))
        if self.is_enabled():
            if ((value is not 0) or (not sender.is_momentary())):
                track_index = (list(self._stop_track_clip_buttons).index(sender) + self.track_offset())
                if (track_index in range(len(self.song().tracks))):
                    slots = self.song().tracks[track_index].clip_slots
                    found_triggered = False
                    found_playing = False
                    for slot in slots:
                        if slot.has_clip:
                            if slot.clip.is_triggered:
                                found_triggered = True
                                found_playing |= slot.clip.is_playing
                                slot.clip.stop()
                            if slot.clip.is_playing:
                                found_playing = True
                                slot.clip.stop()
                        if (found_triggered and found_playing):
                            break





# local variables:
# tab-width: 4
