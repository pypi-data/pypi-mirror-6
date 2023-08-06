# -*- coding: utf-8 -*-
# Copyright 2012 Mark Hall (Mark.Hall@work.room3b.eu)
# 
# This file is part of the PyWebTools.
# 
# The PyWebTools is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# The PyWebTools are distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with PyWebTools. If not, see <http://www.gnu.org/licenses/>.

u"""
:mod:`pyramid_tools.renderer` -- Genshi renderer for Pyramid
============================================================

This packages provides the :func:`~pywebtools.renderer.renderer` decorator
that provides a flexible rendering intermediary for the Pyramid framework.

IMPORTANT! The required Python packages for this module are not installed
automatically. You must install the following::

  ``pip install mimeparse decorator pyramid``

to be able to use this module.

.. moduleauthor:: Mark Hall <mark.hall@mail.room3b.eu>
"""

import csv
import json
import mimeparse

from copy import copy
from decorator import decorator
from genshi.template import TemplateLoader, loader
from pyramid.httpexceptions import HTTPNotAcceptable
from pyramid.request import Request
from pyramid.response import Response
from StringIO import StringIO

from .htmlfiller import HTMLFormFiller

_genshi_loader = None
_template_defaults = {}

class RendererException(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return self.value

def init(settings, template_defaults=None):
    global _genshi_loader, _template_defaults
    if 'genshi.template_path' not in settings:
        raise RendererException('genshi.template_path not set in the configuration')
    if template_defaults:
        _template_defaults = template_defaults
    auto_reload = ('pyramid.reload_templates' in settings and settings['pyramid.reload_templates'] == 'true')
    template_paths = []
    for template_path in [tp for line in settings['genshi.template_path'].strip().split('\n') for tp in line.split(',')]:
        if template_path.strip() != '':
            if ':' in template_path:
                template_paths.append(loader.package(template_path[0:template_path.find(':')], template_path[template_path.find(':') + 1:]))
            else:
                template_paths.append(template_path)
    _genshi_loader = TemplateLoader(template_paths,
                                    auto_reload=auto_reload)

def request_from_args(*args):
    for arg in args:
        if isinstance(arg, Request):
            return arg
    raise RendererException('No request found')
    
def template_defaults(request, content_type):
    global _template_defaults
    if content_type and content_type in _template_defaults:
        td = copy(_template_defaults[content_type])
    else:
        td = {}
    td['r'] = request
    return td

def match_response_type(content_types, request):
    accept_header = unicode(request.accept)
    if request.matchdict and 'ext' in request.matchdict and request.matchdict['ext']:
        if request.matchdict['ext'] == 'html':
            accept_header = 'text/html'
        elif request.matchdict['ext'] == 'json':
            accept_header = 'application/json'
        elif request.matchdict['ext'] == 'csv':
            accept_header = 'text/csv'
        elif request.matchdict['ext'] == 'xml':
            accept_header = 'application/xml'
    response_type = mimeparse.best_match(content_types.keys(), accept_header)
    return response_type

def handle_html_response(request, response_template, result):
    template = _genshi_loader.load(response_template)
    if 'e' in result:
        template = template.generate(**result) | HTMLFormFiller(data=result['e'].params)
    else:
        result['e'] = None
        template = template.generate(**result)
    response = Response(template.render('xhtml'))
    return response

def handle_json_response(request, result):
    del result['r']
    if 'e' in result:
        result['e'] = result['e'].error_dict
    response = Response(json.dumps(result))
    return response

def handle_csv_response(request, result):
    f = StringIO()
    writer = csv.DictWriter(f, result['columns'], extrasaction='ignore')
    writer.writeheader()
    for row in result['rows']:
        writer.writerow(row)
    response = Response(f.getvalue())
    f.close()
    return response

def handle_xml_response(request, response_template, result):
    template = _genshi_loader.load(response_template)
    template = template.generate(**result)
    response = Response(template.render('xml'))
    return response

def render(content_types={}, allow_cache=True):
    def wrapper(f, *args, **kwargs):
        request = request_from_args(*args)
        response_type = match_response_type(content_types, request)
        if not response_type or response_type not in content_types:
            raise HTTPNotAcceptable()
        result = template_defaults(request, response_type)
        result.update(f(*args, **kwargs))
        response_template = content_types[response_type]
        if response_type == 'application/json':
            response = handle_json_response(request, result)
            response.cache_control = 'no-cache'
            response.pragma = 'no-cache'
            response.expires = '0'
        elif response_type == 'text/html':
            response = handle_html_response(request, response_template, result)
        elif response_type == 'text/csv':
            response = handle_csv_response(request, result)
        elif response_type == 'application/xml':
            response = handle_xml_response(request, response_template, result)
        response.content_type = response_type
        request.response.merge_cookies(response)
        if not allow_cache:
            response.cache_control = 'no-cache'
            response.pragma = 'no-cache'
            response.expires = '0'
        return response
    return decorator(wrapper)
