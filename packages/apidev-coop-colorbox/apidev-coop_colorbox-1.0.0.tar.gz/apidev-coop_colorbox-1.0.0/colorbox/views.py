# -*- coding: utf-8 -*-

from django.views.generic.edit import FormView
from decorators import popup_redirect
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied

class PopupRedirectView(FormView):
    template_name = "colorbox/popup_form_base.html"
    form_url = ""
    title = ""
    form_class = None
    success_url = ""
    staff_only = True
    
    def get_context_data(self, **kwargs):
        context = super(PopupRedirectView, self).get_context_data(**kwargs)
        context['form_url'] = self.get_form_url()
        context['title'] = self.get_title()
        return context

    def get_form_url(self):
        return self.form_url
    
    def get_title(self):
        return self.title
    
    @method_decorator(popup_redirect)
    def dispatch(self, *args, **kwargs):
        if self.staff_only:
            if not self.request.user.is_staff:
                raise PermissionDenied
        return super(PopupRedirectView, self).dispatch(*args, **kwargs)
    
class AdminPopupRedirectView(PopupRedirectView):
    staff_only = True
    
    #@method_decorator(popup_redirect)
    def dispatch(self, *args, **kwargs):
        if self.staff_only:
            if not self.request.user.is_staff:
                raise PermissionDenied()
        return super(AdminPopupRedirectView, self).dispatch(*args, **kwargs)