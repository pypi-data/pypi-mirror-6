from django.forms.widgets import MediaDefiningClass
from django.forms.widgets import Widget
from django.template.loader import get_template

from loading import registry


class WidgetMeta(MediaDefiningClass):
    """
    initializes widget classes
    automatically adds widget instance into registry
    """

    def __init__(mcs, name, bases, attrs):
        MediaDefiningClass.__init__(mcs, name, bases, attrs)
        if 'template' not in attrs:
            mcs.template = None
        mcs.template_instance = None
        if name is not 'WebNode':
            registry.register(name, mcs())


class WebNode(Widget):
    """
    base webnode class
    """
    __metaclass__ = WidgetMeta
    template = None

    def __init__(self, *args, **kwargs):
        super(Widget, self).__init__(*args, **kwargs)
        self.template_instance = None

    def get_context(self):
        """
        returns context dictionary
        """
        return {}

    def render(self, context, args=[], kwargs={}):
        """
        main render method
        uses "template" class property for rendering
        or needs to be overriden for custom non-template webnotes
        """
        if not self.template_instance:
            if not self.template:
                raise RuntimeError('Abstract method WebNode.render()\
                        is not implemented')
            self.template_instance = get_template(self.template)
        context.push()
        _context = self.get_context(*args, **kwargs)
        context.update(_context)
        result = self.template_instance.render(context)
        context.pop()
        return result
