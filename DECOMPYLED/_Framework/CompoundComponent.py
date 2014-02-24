# emacs-mode: -*- python-*-
from ControlSurfaceComponent import ControlSurfaceComponent
class CompoundComponent(ControlSurfaceComponent):
    __module__ = __name__
    __doc__ = ' Base class for classes encompasing other components to form complex components '

    def __init__(self):
        ControlSurfaceComponent.__init__(self)
        self._sub_components = []



    def disconnect(self):
        self._sub_components = None



    def register_components(self, component):
        assert (component != None)
        assert isinstance(component, ControlSurfaceComponent)
        assert (list(self._sub_components).count(component) is 0)
        self._sub_components.append(component)
        component.set_enabled(self.is_enabled())



    def set_enabled(self, enable):
        assert isinstance(enable, type(False))
        if (self.is_enabled() != enable):
            for component in self._sub_components:
                component.set_enabled(enable)

            ControlSurfaceComponent.set_enabled(self, enable)




# local variables:
# tab-width: 4
