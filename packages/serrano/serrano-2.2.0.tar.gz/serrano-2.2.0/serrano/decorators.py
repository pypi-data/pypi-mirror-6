from functools import wraps
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth import authenticate, login


def get_token(request):
    "Attempts to retrieve a token from the request."
    if 'token' in request.REQUEST:
        return request.REQUEST['token']
    if 'HTTP_API_TOKEN' in request.META:
        return request.META['HTTP_API_TOKEN']
    return ''


def check_auth(func):
    @wraps(func)
    def inner(self, request, *args, **kwargs):
        auth_required = getattr(settings, 'SERRANO_AUTH_REQUIRED', False)

        user = getattr(request, 'user', None)

        # Attempt to authenticate if a token is present
        if not user or not user.is_authenticated():
            token = get_token(request)
            user = authenticate(token=token)
            if user:
                login(request, user)
            elif auth_required:
                return HttpResponse(status=401)
        return func(self, request, *args, **kwargs)
    return inner
