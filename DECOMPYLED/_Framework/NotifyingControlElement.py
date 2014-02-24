# emacs-mode: -*- python-*-
from ControlElement import ControlElement
class NotifyingControlElement(ControlElement):
    __module__ = __name__
    __doc__ = ' Class representing control elements that can send values '

    def __init__(self):
        ControlElement.__init__(self)
        self._value_notifications = []



    def disconnect(self):
        ControlElement.disconnect(self)
        self._value_notifications = []



    def register_value_notification(self, callback, identify_sender = False):
        """ Registers a callback that is triggerd when a message is received """
        assert (callback != None)
        assert (dir(callback).count('im_func') is 1)
        for notification in self._value_notifications:
            assert (notification['Callback'] != callback)

        self._value_notifications.append({'Callback': callback,
         'Identify': identify_sender})



    def unregister_value_notification(self, callback):
        """ Unregisters a forwarding callback """
        assert (callback != None)
        assert (dir(callback).count('im_func') is 1)
        entry_removed = False
        for notification in self._value_notifications:
            if (notification['Callback'] == callback):
                self._value_notifications.remove(notification)
                entry_removed = True

        assert entry_removed




# local variables:
# tab-width: 4
