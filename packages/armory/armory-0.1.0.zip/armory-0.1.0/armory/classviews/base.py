from django.views.generic import View
from django.http import HttpResponse
from django.template import RequestContext, Template
from django.shortcuts import render
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import resolve
from dict2xml import dict2xml
import json
import re


class BaseView(View):
    """
    This is the base object for Class Based Views in Armory
    """
    template_variables = {}
    templates = {
        'base_template': 'shell.html',
        'ajax_template': 'ajax.html',
        'app_template': 'app.html',
    }
    def dispatch(self, request, *args, **kwargs):
        self.current_site = get_current_site(request)
        self.app_name = resolve(request.path).app_name
        view = self.__class__.__name__
        if view[-4:] == 'View':
            view = view[:-4]
        view = re.sub('(.)([A-Z]{1})', r'\1_\2', view).lower()
        self.view = view
        if self.app_name:
            self.view_template = ['%s/%s.html' % (self.app_name, view)]
        else:
            self.view_template = ['%s.html' % view]
        return super(BaseView, self).dispatch(request, *args, **kwargs)
        
    def make_template_variables(self, request):
        self.current_site = get_current_site(request)
        self.request = request
        self.app_name = resolve(request.path).app_name
        request.tvars = {}
        view_name = self.__class__.__name__
        if view_name[-4:] == 'View':
            view_name = view_name[:-4]
        view_name = re.sub('(.)([A-Z]{1})', r'\1_\2', view_name).lower()
        self.view_name = view_name
        css_page_namespace = 'view-%s' % self.view_name.replace('_', '-')
        css_app_namespace = 'app-%s' % self.app_name
        self.request.tvars['css_namespace'] = '%s %s' % (css_page_namespace, css_app_namespace)

    def to_template(self, data = None, template = None, ci = None, ct = None, status = None):
        if not data:
            data = {}
        if not template:
            template = self.view_template
        if not ci:
            ci = RequestContext(self.request)
        response = render(self.request, template_name = template, dictionary = data, context_instance = ci, content_type = ct)
        if status:
            response.status_code = status
        return response


    def to_json(self, data = None, status = 200):
        if not data: data = {}
        response = Template("{{ json|safe }}")
        context = RequestContext(self.request, {'json' : json.dumps(data)})
        return HttpResponse(response.render(context), content_type="application/json")


    def to_xml(self, data = None, status = 200):
        if not data: data = {}
        temp = Template("<xml>{{ xml_data|safe }}</xml>")
        rc = RequestContext(self.request, {'xml_data' : dict2xml(data)})
        return HttpResponse(temp.render(rc), content_type="application/xhtml+xml")


class SessionWrapper(object):
    class SessionInterface(object):
        def __init__(self, session):
            self.session = session
        def __getattr__(self, attr):
            return getattr(self.session, attr)
        def store(self, key, value):
            self.session[key] = value
            self.session.save()

    session = SessionInterface(self.request.session)

