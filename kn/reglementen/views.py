# vim: et:sta:bs=2:sw=4:
import kn.reglementen.entities as Es_regl


from django.template import RequestContext
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response

def reglement_list(request):
    return render_to_response('reglementen/reglement_list.html',
            {'reglementen': Es_regl.all()},
            context_instance=RequestContext(request))

def reglement_detail(request, name):
    reglement = Es_regl.reglement_by_name(name)
    if not reglement:
        raise Http404
    return render_to_response('reglementen/reglement_detail.html',
            {'reglement': reglement},
            context_instance=RequestContext(request))

def version_detail(request, reglement_name, version_name):
    version = Es_regl.version_by_names(reglement_name, version_name)
    return render_to_response('reglementen/version_detail.html',
            {'version': version,
             'content': version.to_html()},
            context_instance=RequestContext(request))
