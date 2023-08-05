import re

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils import translation

## from digital.models import Profile


class TimezoneMiddleware(object):
    def process_request(self, request):
        tz = None
        if request.user.is_authenticated():
            try:
                tz = request.user.profile.timezone
            except Profile.DoesNotExist:
                pass
        if tz:
            timezone.activate(tz)
        else:
            timezone.deactivate()


#
# From https://djangosnippets.org/snippets/1220/
#
class RequireLoginMiddleware(object):
    """
    Middleware component that wraps the login_required decorator around
    matching URL patterns. To use, add the class to MIDDLEWARE_CLASSES and
    define LOGIN_REQUIRED_URLS and LOGIN_REQUIRED_URLS_EXCEPTIONS in your
    settings.py. For example:
    ------
    LOGIN_REQUIRED_URLS = (
        r'/topsecret/(.*)$',
    )
    LOGIN_REQUIRED_URLS_EXCEPTIONS = (
        r'/topsecret/login(.*)$',
        r'/topsecret/logout(.*)$',
    )
    ------
    LOGIN_REQUIRED_URLS is where you define URL patterns; each pattern must
    be a valid regex.

    LOGIN_REQUIRED_URLS_EXCEPTIONS is, conversely, where you explicitly
    define any exceptions (like login and logout URLs).
    """

    def __init__(self):
        self.required = tuple(re.compile(url) for url in
                                      settings.LOGIN_REQUIRED_URLS)
        self.exceptions = tuple(re.compile(url) for url in
                                      settings.LOGIN_REQUIRED_URLS_EXCEPTIONS)

    def process_view(self, request, view_func, view_args, view_kwargs):
        # No need to process URLs if user already logged in
        if request.user.is_authenticated():
            return None

        # An exception match should immediately return None
        for url in self.exceptions:
            if url.match(request.path_info):
                return None

        # Requests matching a restricted URL pattern are returned
        # wrapped with the login_required decorator
        for url in self.required:
            if url.match(request.path_info):
                return login_required(view_func)(request,
                                        *view_args, **view_kwargs)

        # Explicitly return None for all non-matching requests
        return None


class GetParamLocaleMiddleware(object):
    """
    This Middleware sets the language from a GET param.
    """
    def process_request(self, request):
        if request.method == 'GET' and request.GET.get('lang'):
            language = request.GET['lang']
            for lang in settings.LANGUAGES:
                if lang[0] == language:
                    translation.activate(language)
                    request.LANGUAGE_CODE = translation.get_language()
