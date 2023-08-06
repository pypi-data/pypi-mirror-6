# -*- coding: utf-8 -*-
#    Asymmetric Base Framework - A collection of utilities for django frameworks
#    Copyright (C) 2013  Asymmetric Ventures Inc.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; version 2 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
from __future__ import absolute_import, division, print_function, unicode_literals

from collections import OrderedDict

try:
	from django.apps import AppConfig
except ImportError:
	AppConfig = object

from jinja2.utils import contextfunction

from asymmetricbase.jinja import get_jinja_env
from asymmetricbase.jinja.global_functions import jinja_getattr

@contextfunction
def jinja_context_getattr(context, attr_string):
	"""
	Tries to get attribute by name from context
	"""
	return jinja_getattr(context.environment, context, attr_string)

@contextfunction
def jinja_batch_context_getattr(context, *args, **kwargs):
	new_args = []
	new_kwargs = {}
	if args:
		for arg in args:
			new_args.append(jinja_context_getattr(context, arg))
		return new_args
	if kwargs:
		for k, v in kwargs.items():
			new_kwargs[k] = jinja_context_getattr(context, v)
		return new_kwargs

@contextfunction
def jinja_resolve_contextattributes(context, __obj, **kwargs):
	from .utils import ContextAttribute
	
	if isinstance(__obj, ContextAttribute):
		return __obj(context, **kwargs)
	
	elif isinstance(__obj, (list, tuple)):
		return (jinja_resolve_contextattributes(context, item, **kwargs) for item in __obj)
	
	elif isinstance(__obj, (set, frozenset)):
		return { jinja_resolve_contextattributes(context, item, **kwargs) for item in __obj }
	
	elif isinstance(__obj, (dict, OrderedDict)):
		return { k : jinja_resolve_contextattributes(context, item, **kwargs) for k, item in __obj.items() }
	
	return __obj

@contextfunction
def jinja_vtable(ctx, table, header = '', tail = '', title = ''):
	return ctx.environment.get_template_module('asymmetricbase/displaymanager/base.djhtml', ctx).vtable(table, header, tail, title)

@contextfunction
def jinja_gridlayout(ctx, layout):
	return ctx.environment.get_template_module('asymmetricbase/displaymanager/base.djhtml', ctx).gridlayout(layout)

@contextfunction
def jinja_display(ctx, layout):
	return ctx.environment.get_template_module('asymmetricbase/displaymanager/base.djhtml', ctx).display(layout)

class DisplayManagerAppConfig(AppConfig):
	def ready(self):
		get_jinja_env().globals.update({
			'context_getattr' : jinja_context_getattr,
			'batch_context_getattr' : jinja_batch_context_getattr,
			'resolve_contextattributes' : jinja_resolve_contextattributes,
			'vtable' : jinja_vtable,
			'gridlayout' : jinja_gridlayout,
			'display' : jinja_display,
		})
