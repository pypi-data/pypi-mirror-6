from django.http import HttpResponse
from django.template import RequestContext


from cms.models import CMSPlugin

def ajax_render(request, plugin_id):
    plugin = CMSPlugin.objects.get(pk=plugin_id)
    context = RequestContext(request)
    rendered = plugin.render_plugin(context)
    return HttpResponse(rendered)
