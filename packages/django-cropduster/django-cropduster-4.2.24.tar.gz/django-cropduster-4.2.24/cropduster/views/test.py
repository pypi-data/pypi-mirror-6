from django.http import HttpResponse

def testing_import(request):
    import ipdb; ipdb.set_trace()
    return HttpResponse("OK", mimetype="text/plain")

def testing_sys_path(request):
    import sys
    return HttpResponse("\n".join(sys.path), mimetype="text/plain")
