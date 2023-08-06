from django.template import RequestContext
from django.shortcuts import render_to_response


from cms.models import CMSPlugin

def ajax_render(request, plugin_id):
    plugin = CMSPlugin.objects.get(pk=plugin_id)
    context = RequestContext(request)
    rendered = plugin.render_plugin(context)
    return render_to_response('cms_ajax_text_plugin/view.html',
            {'content': rendered}, context)
