from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.contrib.auth import get_user_model, login as django_login, REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.http import is_safe_url
from . import MAX_AGE_OF_SIGNATURE_IN_SECONDS, SESSION_USER_KEY, SESSION_REDIRECT_KEY

# no permissions necessary since this only works for valid signatures
def login(request, signature):
    """
    Automatically logs in a user based on a signed PK of a user object. The
    signature should be generated with the `cloak` management command.

    The signature will only work for 60 seconds.
    """
    signer = TimestampSigner()
    try:
        pk = signer.unsign(signature, max_age=MAX_AGE_OF_SIGNATURE_IN_SECONDS)
    except signing.BadSignature, SignatureExpired:
        return HttpResponseForbidden("Can't log you in")

    user = get_object_or_404(get_user_model(), pk=pk)
    # we *have* to set the backend for this user, so we just use the first one
    user.backend = settings.AUTHENTICATION_BACKENDS[0]
    django_login(request, user)

    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

@login_required
def cloak(request, pk):
    """
    Masquerade as a particular user and redirect based on the
    REDIRECT_FIELD_NAME parameter, or the LOGIN_REDIRECT_URL.
    """
    if request.method != 'POST':
        return HttpResponse("I only respond to POSTs")

    user = get_object_or_404(get_user_model(), pk=pk)
    # check to see if the user is allowed to do this
    can_cloak = False
    try:
        can_cloak = request.user.can_cloak_as(user)
    except AttributeError as e:
        try:
            can_cloak = request.user.is_admin
        except AttributeError as e:
            pass

    request.session[SESSION_USER_KEY] = user.pk
    request.session[SESSION_REDIRECT_KEY] = request.META.get("HTTP_REFERER", settings.LOGIN_REDIRECT_URL)
    return HttpResponseRedirect(request.GET(REDIRECT_FIELD_NAME, settings.LOGIN_REDIRECT_URL))

# no perms neccessary here
def uncloak(request):
    """Undo a masquerade session"""
    if request.method != 'POST':
        return HttpResponse("I only respond to POSTs")

    try:
        del request.session[SESSION_USER_KEY]
    except KeyError:
        pass # who cares

    # figure out where to redirect
    next = request.GET.get(REDIRECT_FIELD_NAME, request.session.get(SESSION_REDIRECT_KEY))
    if next is not None and is_safe_url(next, request.request.get_host()):
        return HttpResponseRedirect(next)
    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
