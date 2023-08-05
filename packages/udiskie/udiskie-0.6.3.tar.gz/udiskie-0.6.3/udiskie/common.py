"""
Common DBus utilities.
"""
__all__ = ['DBusProperties',
           'DBusProxy',
           'DBusService',
           'DBusException',
           'Emitter']

from dbus import Interface, SystemBus
from dbus.exceptions import DBusException
from dbus.mainloop.glib import DBusGMainLoop

class DBusProperties(object):
    """
    Dbus property map abstraction.

    Properties of the object can be accessed as attributes.

    """
    def __init__(self, dbus_object, interface):
        """Initialize a proxy object with standard DBus property interface."""
        self.__proxy = Interface(
                dbus_object,
                dbus_interface='org.freedesktop.DBus.Properties')
        self.__interface = interface

    def __getattr__(self, property):
        """Retrieve the property via the DBus proxy."""
        return self.__proxy.Get(self.__interface, property)

class DBusProxy(object):
    """
    DBus proxy object.

    Provides property and method bindings.

    """
    def __init__(self, proxy, interface):
        self.Exception = DBusException
        self.object_path = proxy.object_path
        self.property = DBusProperties(proxy, interface)
        self.method = Interface(proxy, interface)
        self._bus = proxy._bus

class DBusService(object):
    """
    Abstract base class for UDisksX service wrapper classes.
    """
    mainloop = None

    @classmethod
    def connect_service(cls, bus=None, mainloop=None):
        """
        Connect to the service object on dbus.

        :param dbus.Bus bus: connection to system bus
        :param dbus.mainloop.NativeMainLoop mainloop: system bus event loop
        :raises dbus.DBusException: if unable to connect to service.

        The mainloop parameter is only relevant if no bus is given. In this
        case if ``mainloop is True``, use the default (glib) mainloop
        provided by dbus-python.

        """
        if bus is None:
            mainloop = mainloop or cls.mainloop
            if mainloop is True:
                mainloop = DBusGMainLoop()
            bus = SystemBus(mainloop=mainloop or cls.mainloop)
        obj = bus.get_object(cls.BusName, cls.ObjectPath)
        return DBusProxy(obj, cls.Interface)

    @classmethod
    def create(cls, bus=None, mainloop=None):
        return cls(cls.connect_service(bus, mainloop or cls.mainloop))


class Emitter(object):
    """
    Event emitter class.

    Provides a simple event engine featuring a known finite set of events.

    """
    def __init__(self, event_names=(), *args, **kwargs):
        """
        Initialize with empty lists of event handlers.

        :param iterable event_names: names of known events.

        """
        super(Emitter, self).__init__(*args, **kwargs)
        self.event_handlers = {}
        for evt in event_names:
            self.event_handlers[evt] = []

    def trigger(self, event, *args):
        """Trigger event handlers."""
        for handler in self.event_handlers[event]:
            handler(*args)

    def connect(self, handler, event=None):
        """Connect an event handler."""
        if event:
            self.event_handlers[event].append(handler)
        else:
            for event in self.event_handlers:
                if hasattr(handler, event):
                    self.connect(getattr(handler, event), event)

    def disconnect(self, handler, event=None):
        """Disconnect an event handler."""
        if event:
            self.event_handlers.remove(handler)
        else:
            for event in self.event_handlers:
                if hasattr(handler, event):
                    self.disconnect(getattr(handler, event), event)

