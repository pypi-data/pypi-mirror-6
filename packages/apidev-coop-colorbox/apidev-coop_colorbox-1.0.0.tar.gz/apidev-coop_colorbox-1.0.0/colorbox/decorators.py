# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseForbidden
from django.core.exceptions import PermissionDenied
import logging
logger = logging.getLogger("colorbox")

def popup_redirect(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            response = view_func(request, *args, **kwargs)
        except Http404:
            return HttpResponseNotFound()
        except PermissionDenied:
            return HttpResponseForbidden()    
        except Exception, msg:
            logger.exception(u"exception in popup: {0}".format(msg))
            raise
        if response.status_code == 302:
            script = u'<script>$.colorbox.close(); window.location="%s";</script>' % response['Location']
            return HttpResponse(script)
        elif response.status_code != 200:
            return HttpResponse(status_code=response.status_code)
        else:
            return response
    return wrapper

def popup_close(view_func):
    def wrapper(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        if not response:
            script = '<script>$.colorbox.close(); window.location=window.location;</script>'
            response = HttpResponse(script)
        return response
    return wrapper

class HttpResponseClosePopup(HttpResponse):
    def __init__(self):
        super(HttpResponseClosePopup, self).__init__("close_popup")
