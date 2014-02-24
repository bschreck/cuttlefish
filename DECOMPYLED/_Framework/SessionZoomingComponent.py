# emacs-mode: -*- python-*-
import Live
from CompoundComponent import CompoundComponent
from ControlSurfaceComponent import ControlSurfaceComponent
from SessionComponent import SessionComponent
from ButtonElement import ButtonElement
from ButtonMatrixElement import ButtonMatrixElement
class SessionZoomingComponent(CompoundComponent):
    __module__ = __name__
    __doc__ = ' Class using a matrix of buttons to choose blocks of clips in the session '

    def __init__(self, session):
        assert isinstance(session, SessionComponent)
        CompoundComponent.__init__(self)
        self._session = session
        self._buttons = None
        self._zoom_button = None
        self._scene_bank_buttons = None
        self._nav_up_button = None
        self._nav_down_button = None
        self._nav_left_button = None
        self._nav_right_button = None
        self._scene_bank_index = 0
        self._is_zoomed_out = False
        self._empty_value = 0
        self._stopped_value = 100
        self._playing_value = 127
        self._selected_value = 64
        self.register_components(self._session)
        self._session.set_offset_callback(self._on_session_offset_changes)



    def disconnect(self):
        CompoundComponent.disconnect(self)
        self._session = None
        self._buttons = None
        self._zoom_button = None
        self._scene_bank_buttons = None
        self._nav_up_button = None
        self._nav_down_button = None
        self._nav_left_button = None
        self._nav_right_button = None



    def on_enabled_changed(self):
        self.update()
        self._session.set_show_highlight(self.is_enabled())



    def set_button_matrix(self, buttons):
        assert isinstance(buttons, ButtonMatrixElement)
        if (self._buttons != None):
            self._buttons.unregister_value_notification(self._matrix_value)
            self._buttons.reset()
        self._buttons = buttons
        if (self._buttons != None):
            self._buttons.register_value_notification(self._matrix_value)
            self.update()



    def set_zoom_button(self, button):
        assert isinstance(button, ButtonElement)
        if (self._zoom_button != None):
            self._zoom_button.unregister_value_notification(self._zoom_value)
            self._zoom_button.reset()
        self._zoom_button = button
        if (self._zoom_button != None):
            self._zoom_button.register_value_notification(self._zoom_value)



    def set_nav_buttons(self, up, down, left, right):
        assert isinstance(up, ButtonElement)
        assert isinstance(down, ButtonElement)
        assert isinstance(left, ButtonElement)
        assert isinstance(right, ButtonElement)
        if (self._nav_up_button != None):
            self._nav_up_button.unregister_value_notification(self._nav_up_value)
            self._nav_up_button.reset()
        self._nav_up_button = up
        if (self._nav_up_button != None):
            self._nav_up_button.register_value_notification(self._nav_up_value)
        if (self._nav_down_button != None):
            self._nav_down_button.unregister_value_notification(self._nav_down_value)
            self._nav_down_button.reset()
        self._nav_down_button = down
        if (self._nav_down_button != None):
            self._nav_down_button.register_value_notification(self._nav_down_value)
        if (self._nav_left_button != None):
            self._nav_left_button.unregister_value_notification(self._nav_left_value)
            self._nav_left_button.reset()
        self._nav_left_button = left
        if (self._nav_left_button != None):
            self._nav_left_button.register_value_notification(self._nav_left_value)
        if (self._nav_right_button != None):
            self._nav_right_button.unregister_value_notification(self._nav_right_value)
            self._nav_right_button.reset()
        self._nav_right_button = right
        if (self._nav_right_button != None):
            self._nav_right_button.register_value_notification(self._nav_right_value)



    def set_scene_bank_buttons(self, buttons):
        assert isinstance(buttons, tuple)
        if (self._scene_bank_buttons != None):
            for button in self._scene_bank_buttons:
                button.unregister_value_notification(self._scene_bank_value)
                button.reset()

        self._scene_bank_buttons = buttons
        if (self._scene_bank_buttons != None):
            for button in self._scene_bank_buttons:
                button.register_value_notification(self._scene_bank_value, identify_sender=True)




    def set_empty_value(self, value):
        assert (value in range(128))
        self._empty_value = value



    def set_playing_value(self, value):
        assert (value in range(128))
        self._playing_value = value



    def set_stopped_value(self, value):
        assert (value in range(128))
        self._stopped_value = value



    def set_selected_value(self, value):
        assert (value in range(128))
        self._selected_value = value



    def update(self):
        if self.is_enabled():
            if (self._is_zoomed_out and (self._buttons != None)):
                song = self.song()
                width = self._session.width()
                height = self._session.height()
                for x in range(self._buttons.width()):
                    for y in range(self._buttons.height()):
                        value_to_send = self._empty_value
                        scene_bank_offset = ((self._scene_bank_index * self._buttons.height()) * height)
                        track_offset = (x * width)
                        scene_offset = ((y * height) + scene_bank_offset)
                        if ((track_offset in range(len(song.tracks))) and (scene_offset in range(len(song.scenes)))):
                            value_to_send = self._stopped_value
                            if ((self._session.track_offset() in range(((width * (x - 1)) + 1), (width * (x + 1)))) and ((self._session.scene_offset() - scene_bank_offset) in range(((height * (y - 1)) + 1), (height * (y + 1))))):
                                value_to_send = self._selected_value
                            else:
                                playing = False
                                for track in range(track_offset, (track_offset + width)):
                                    for scene in range(scene_offset, (scene_offset + height)):
                                        if ((track in range(len(song.tracks))) and (scene in range(len(song.scenes)))):
                                            slot = song.scenes[scene].clip_slots[track]
                                            if (slot.has_clip and slot.clip.is_playing):
                                                value_to_send = self._playing_value
                                                playing = True
                                                break

                                    if playing:
                                        break

                        self._buttons.send_value(x, y, value_to_send)


            if (self._scene_bank_buttons != None):
                for index in range(len(self._scene_bank_buttons)):
                    if (self._is_zoomed_out and (index == self._scene_bank_index)):
                        self._scene_bank_buttons[index].turn_on()
                    else:
                        self._scene_bank_buttons[index].turn_off()




    def _on_session_offset_changes(self):
        if self._is_zoomed_out:
            self._scene_bank_index = int(((self._session.scene_offset() / self._session.height()) / self._buttons.height()))
        self.update()



    def _zoom_value(self, value):
        assert (self._zoom_button != None)
        assert (value in range(128))
        if self.is_enabled():
            if self._zoom_button.is_momentary():
                self._is_zoomed_out = (value > 0)
            else:
                self._is_zoomed_out = (not self._is_zoomed_out)
            if self._is_zoomed_out:
                self._scene_bank_index = int(((self._session.scene_offset() / self._session.height()) / self._buttons.height()))
            else:
                self._scene_bank_index = 0
            self._session.set_enabled((not self._is_zoomed_out))
            self.update()



    def _matrix_value(self, value, x, y, is_momentary):
        assert (self._buttons != None)
        assert (value in range(128))
        assert (x in range(self._buttons.width()))
        assert (y in range(self._buttons.height()))
        assert isinstance(is_momentary, type(False))
        if (self.is_enabled() and self._is_zoomed_out):
            if ((value != 0) or (not is_momentary)):
                track_offset = (x * self._session.width())
                scene_offset = ((y + (self._scene_bank_index * self._buttons.height())) * self._session.height())
                if ((track_offset in range(len(self.song().tracks))) and (scene_offset in range(len(self.song().scenes)))):
                    self._session.set_offsets(track_offset, scene_offset)



    def _nav_up_value(self, value):
        assert (self._nav_up_button != None)
        assert (value in range(128))
        if (self.is_enabled() and self._is_zoomed_out):
            if ((value != 0) or (not self._nav_up_button.is_momentary())):
                height = self._session.height()
                track_offset = self._session.track_offset()
                scene_offset = self._session.scene_offset()
                if (scene_offset > 0):
                    new_scene_offset = scene_offset
                    if ((scene_offset % height) > 0):
                        new_scene_offset -= (scene_offset % height)
                    else:
                        new_scene_offset = max(0, (scene_offset - height))
                    self._session.set_offsets(track_offset, new_scene_offset)



    def _nav_down_value(self, value):
        assert (self._nav_down_button != None)
        assert (value in range(128))
        if (self.is_enabled() and self._is_zoomed_out):
            if ((value != 0) or (not self._nav_down_button.is_momentary())):
                height = self._session.height()
                track_offset = self._session.track_offset()
                scene_offset = self._session.scene_offset()
                new_scene_offset = ((scene_offset + height) - (scene_offset % height))
                self._session.set_offsets(track_offset, new_scene_offset)



    def _nav_left_value(self, value):
        assert (self._nav_left_button != None)
        assert (value in range(128))
        if (self.is_enabled() and self._is_zoomed_out):
            if ((value != 0) or (not self._nav_left_button.is_momentary())):
                width = self._session.width()
                track_offset = self._session.track_offset()
                scene_offset = self._session.scene_offset()
                if (track_offset > 0):
                    new_track_offset = track_offset
                    if ((track_offset % width) > 0):
                        new_track_offset -= (track_offset % width)
                    else:
                        new_track_offset = max(0, (track_offset - width))
                    self._session.set_offsets(new_track_offset, scene_offset)



    def _nav_right_value(self, value):
        assert (self._nav_right_button != None)
        assert (value in range(128))
        if (self.is_enabled() and self._is_zoomed_out):
            if ((value != 0) or (not self._nav_right_button.is_momentary())):
                width = self._session.width()
                track_offset = self._session.track_offset()
                scene_offset = self._session.scene_offset()
                new_track_offset = ((track_offset + width) - (track_offset % width))
                self._session.set_offsets(new_track_offset, scene_offset)



    def _scene_bank_value(self, value, sender):
        assert (sender in self._scene_bank_buttons)
        assert (value in range(128))
        if (self.is_enabled() and self._is_zoomed_out):
            if ((value != 0) or (not sender.is_momentary())):
                button_offset = list(self._scene_bank_buttons).index(sender)
                scene_offset = ((button_offset * self._buttons.height()) * self._session.height())
                if (scene_offset in range(len(self.song().scenes))):
                    self._scene_bank_index = button_offset
                    self.update()




# local variables:
# tab-width: 4
