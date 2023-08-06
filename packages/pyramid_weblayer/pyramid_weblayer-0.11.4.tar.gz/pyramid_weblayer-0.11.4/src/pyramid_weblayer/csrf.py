#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Provides a ``validate_against_csrf`` ``pyramid.events.ContextFound`` subscriber
  that uses a ``CSRFValidator`` utility to validate incoming requests against
  cross site request forgeries.
"""

__all__ = [
    'CSRFError',
    'CSRFValidator'
]

from pyramid.httpexceptions import HTTPUnauthorized

METHODS_WITH_SIDE_EFFECTS = (
    'delete',
    'post', 
    'put',
)

class CSRFError(ValueError):
    """Raised when csrf validation fails."""


class CSRFValidator(object):
    """Validate a request against cross site request forgeries."""
    
    def __init__(self, session_token, target_methods=METHODS_WITH_SIDE_EFFECTS):
        self._session_token = session_token
        self._target_methods = target_methods
    
    def validate(self, request):
        if not request.method.lower() in self._target_methods:
            return
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return
        request_param = request.params.get('_csrf', None)
        if request_param is None or request_param != self._session_token:
            raise CSRFError
    


def validate_against_csrf(event, Validator=CSRFValidator):
    """Event subscriber that uses the session to validate incoming requests."""
    
    request = event.request
    settings = request.registry.settings
    
    # Only validate if enabled.
    if not settings.get('csrf.validate', True):
        return
    
    # Ignore specified routes.
    matched_route = request.matched_route
    ignore_routes = settings.get('csrf.ignore_routes', None)
    if matched_route and ignore_routes:
        if matched_route.name in ignore_routes.split():
            return
    
    # Ignore specified paths.
    ignore_paths = settings.get('csrf.ignore_paths', None)
    if ignore_paths:
        for path in ignore_paths.split():
            if request.path.startswith(path):
                return
    
    session_token = request.session.get_csrf_token()
    try:
        Validator(session_token).validate(request)
    except CSRFError:
        raise HTTPUnauthorized

