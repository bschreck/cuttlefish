# emacs-mode: -*- python-*-
import Live
from ControlElement import ControlElement
class ControlSurfaceComponent(object):
    __module__ = __name__
    __doc__ = ' Base class for all classes encapsulating functions in Live '
    _register_component_callback = None
    _register_timer_notification_callback = None
    _unregister_timer_notification_callback = None
    _request_rebuild_callback = None
    _applicaton = None
    _song = None

    def set_song_and_application(song, application):
        assert isinstance(song, Live.Song.Song)
        assert isinstance(application, Live.Application.Application)
        ControlSurfaceComponent._application = application
        ControlSurfaceComponent._song = song


    set_song_and_application = staticmethod(set_song_and_application)

    def set_register_component_callback(callback):
        """ set callback for registering a timer notification """
        assert (dir(callback).count('im_func') is 1)
        ControlSurfaceComponent._register_component_callback = callback


    set_register_component_callback = staticmethod(set_register_component_callback)

    def set_register_timer_notification_callback(callback):
        """ set callback for registering a timer notification """
        assert (dir(callback).count('im_func') is 1)
        ControlSurfaceComponent._register_timer_notification_callback = callback


    set_register_timer_notification_callback = staticmethod(set_register_timer_notification_callback)

    def set_unregister_timer_notification_callback(callback):
        """ set callback for registering a timer notification """
        assert (dir(callback).count('im_func') is 1)
        ControlSurfaceComponent._unregister_timer_notification_callback = callback


    set_unregister_timer_notification_callback = staticmethod(set_unregister_timer_notification_callback)

    def set_request_rebuild_callback(callback):
        """ set callback for requesting midi map rebuilds """
        assert (dir(callback).count('im_func') is 1)
        ControlSurfaceComponent._request_rebuild_callback = callback


    set_request_rebuild_callback = staticmethod(set_request_rebuild_callback)

    def release_class_attributes():
        """ release all set objects to not have dependencies """
        ControlSurfaceComponent._register_timer_notification_callback = None
        ControlSurfaceComponent._unregister_timer_notification_callback = None
        ControlSurfaceComponent._request_rebuild_callback = None
        ControlSurfaceComponent._register_component_callback = None


    release_class_attributes = staticmethod(release_class_attributes)

    def __init__(self):
        assert (ControlSurfaceComponent._register_component_callback != None)
        assert (ControlSurfaceComponent._song != None)
        assert (ControlSurfaceComponent._application != None)
        assert (ControlSurfaceComponent._register_timer_notification_callback != None)
        assert (ControlSurfaceComponent._unregister_timer_notification_callback != None)
        assert (ControlSurfaceComponent._request_rebuild_callback != None)
        object.__init__(self)
        self._is_enabled = True
        self._song_instance = ControlSurfaceComponent._song
        self._application_instance = ControlSurfaceComponent._application
        self._rebuild_callback = ControlSurfaceComponent._request_rebuild_callback
        self._register_timer_callback = ControlSurfaceComponent._register_timer_notification_callback
        self._unregister_timer_callback = ControlSurfaceComponent._unregister_timer_notification_callback
        ControlSurfaceComponent._register_component_callback(self)



    def disconnect(self):
        debug_print('disconnect is abstract. Forgot to override it?')
        assert False



    def update(self):
        debug_print('update is abstract. Forgot to override it?')
        assert False



    def set_enabled(self, enable):
        assert isinstance(enable, type(False))
        self._is_enabled = enable
        self.on_enabled_changed()



    def application(self):
        return self._application



    def song(self):
        return self._song



    def is_enabled(self):
        return self._is_enabled



    def on_enabled_changed(self):
        debug_print('on_enabled_changed is abstract. Forgot to override it?')
        assert False



    def on_track_list_changed(self):
        """ Called by the control surface if tracks are added/removed, to be overridden """
        pass


    def on_scene_list_changed(self):
        """ Called by the control surface if scenes are added/removed, to be overridden """
        pass


    def on_selected_track_changed(self):
        """ Called by the control surface when a track is selected, to be overridden """
        pass


    def on_selected_scene_changed(self):
        """ Called by the control surface when a scene is selected, to be overridden """
        pass



# local variables:
# tab-width: 4
