# Create your views here.
from django.views.generic.base import TemplateView
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext

class MultiSessionFormView(TemplateView):
    form_class = None
    template_name = None
    multisessionform = None
    
    def get_context_data(self, **kwargs):
        context = super(MultiSessionFormView, self).get_context_data(**kwargs)
        return context
    
    def dispatch(self, request, *args, **kwargs):
        if not self.form_class:
            raise ImproperlyConfigured("No form_class defined")
        if not self.template_name:
            raise ImproperlyConfigured("No template_name defined")
        try:
            self.multisessionform = self.form_class.multisessionform_factory()
        except:
            raise ImproperlyConfigured("%s does not use the MultiSessionFormMixin" % self.form_class.__name__)

        try:
            self.pk = self.kwargs['pk']
        except:
            self.pk = None
                    
        try:
            self.form_field = self.kwargs['form_field']
        except:
            self.form_field = None
        
        return super(MultiSessionFormView, self).dispatch(request, *args, **kwargs)
        
    
    def get(self, request, *args, **kwargs):
        if self.pk:
            try:
                model_object = self.form_class.objects.get(pk = self.pk, user = request.user) 
                if self.form_field:
                    form = self.multisessionform(self.form_field, instance = model_object)
                else:
                    return HttpResponseRedirect(model_object.get_absolute_url())
            except:
                model_object = self.form_class()
                return HttpResponseRedirect(model_object.get_absolute_url()) 
        else:
            model_object = None
            form = self.multisessionform(self.form_field)
        try:
            complete = model_object.is_complete()
        except:
            complete = None
        
        
        return self.render_to_response(self.get_context_data(user = request.user, form = form, model = model_object, complete = complete))
        
    def post(self, request, *args, **kwargs):
        if self.pk:
            try:
                model_object = self.form_class.objects.get(pk = self.pk, user = request.user) 
                form = self.multisessionform(self.form_field, request.POST, instance = model_object)
                if form.is_valid():
                    msf_form = form.save()
                    return HttpResponseRedirect(model_object.get_absolute_url(request.GET.get('next',self.form_field)))
            except:
                model_object = self.form_class()
                return HttpResponseRedirect(model_object.get_absolute_url()) 
        else:
            model_object = self.form_class()
            form = self.multisessionform(self.form_field, request.POST)
            if form.is_valid():
                msf_form = form.save(commit = False)
                msf_form.user = request.user
                msf_form.save()
                
                return HttpResponseRedirect(msf_form.get_absolute_url())

        try:
            complete = model_object.is_complete()
        except:
            complete = None
        return self.render_to_response(self.get_context_data(user = request.user, form = form, model = model_object, complete = complete))