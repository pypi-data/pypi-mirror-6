from django.http import HttpResponse
from django.http import Http404
from django.template import Context
from django.views.generic.base import View
from ..loading import registry


class WebNode(View):
    def get(self, request, node_name):
        webnode = registry.get(node_name)
        if not webnode:
            raise Http404("webnode '%s' is not exist" % node_name)
        kwargs = request.REQUEST
        return HttpResponse(webnode.render(Context(), kwargs=kwargs))
