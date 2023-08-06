# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page, never_cache
from django.views.decorators.csrf import csrf_exempt


class NeverCacheMixin(object):
	"""
	Mixin that never caches views.
	"""
	@classmethod
	def as_view(cls, **initkwargs):
		view = super(NeverCacheMixin, cls).as_view(**initkwargs)
		return never_cache(view)


class LoginRequiredMixin(object):
	"""
	Mixin that verifies that the user is authenticated.
	"""
	@classmethod
	def as_view(cls, **initkwargs):
		view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
		return login_required(view)


class CSRFExemptMixin(object):
	"""
	Mixin that exempts from the CSRF requirements.
	"""
	@classmethod
	def as_view(cls, **initkwargs):
		view = super(CSRFExemptMixin, cls).as_view(**initkwargs)
		return csrf_exempt(view)


class CacheMixin(object):
	"""
	Mixin that caches the view with the passed cache_timeout value.
	"""
	cache_timeout = 60

	@classmethod
	def as_view(cls, **initkwargs):
		view = super(CacheMixin, cls).as_view(**initkwargs)
		return cache_page(cls.cache_timeout)(view)
