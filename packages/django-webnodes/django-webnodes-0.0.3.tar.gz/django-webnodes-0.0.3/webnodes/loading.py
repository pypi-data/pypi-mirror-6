from django.conf import settings


class WidgetsCache(object):
    """
    Widgets registry class
    contains all registered widget instances
    """

    def __init__(self):
        """
        initialize widgets cache
        """
        self.widgets = {}

    def register(self, name, widget):
        """
        registering widget instance using custom name
        """
        if name in self.widgets:
            raise KeyError('Widget "%s" is already registered' % name)
        self.widgets[name] = widget

    def unregister(self, widget):
        """
        unregistering widget instance using custom name or widget isinstance
        """
        if isinstance(widget, (str, unicode)):
            self.widgets.pop(str(widget))
        for k, v in self.widgets.items():
            if isinstance(v, widget):
                self.widgets.pop(k)

    def get(self, name):
        """
        returns widget instance by name
        """
        return self.widgets.get(name)

registry = WidgetsCache()


def autodiscover():
    for app in settings.INSTALLED_APPS:
        # Just loading the module will do the trick
        __import__(app, {}, {}, ['webnodes'])
