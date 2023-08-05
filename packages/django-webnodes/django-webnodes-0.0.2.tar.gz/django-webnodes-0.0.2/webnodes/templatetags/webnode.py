from django.template import Library
from django.template import Node
from django.template import TemplateSyntaxError

from ..loading import registry

register = Library()


def _parse_name(bits, parser):
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (registered webnode name)" % bits[0])
    return bits[1]


def _parse_args_kwargs(bits, parser):
    args = []
    kwargs = {}
    bits = bits[2:] if len(bits) > 2 else []
    for bit in bits:
        if '=' in bit:
            k, v = bit.split('=', 1)
            k = k.strip()
            kwargs[k] = parser.compile_filter(v)
        elif bit:
            args.append(parser.compile_filter(bit))
    return (args, kwargs)


class WebNode(Node):
    def __init__(self, name, args, kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs

    def render(self, context):
        values = [self.kwargs[v].resolve(context) for v in self.kwargs]
        resolved_kwargs = dict(zip(self.kwargs.keys(), values))
        resolved_args = [v.resolve(context) for v in self.args]
        webnode = registry.get(self.name)
        if not webnode:
            raise TemplateSyntaxError("webnode '%s' is not exist" % self.name)
        return webnode.render(context, resolved_args, resolved_kwargs)


@register.tag(name='webnode')
def webnode(parser, token):
    bits = token.split_contents()
    name = _parse_name(bits, parser)
    args, kwargs = _parse_args_kwargs(bits, parser)
    return WebNode(name, args, kwargs)
