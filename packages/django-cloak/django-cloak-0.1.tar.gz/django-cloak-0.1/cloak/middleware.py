from django.contrib.auth import get_user_model 
from . import SESSION_USER_KEY

class CloakMiddleware(object):
    """
    This middleware class checks to see if a cloak session variable is
    set, and overrides the request.user object with the cloaked user
    """
    def process_request(self, request):
        request.user.is_cloaked = False
        if SESSION_USER_KEY in request.session:
            try:
                request.user = get_user_model().objects.get(pk=request.session[SESSION_USER_KEY])
                request.user.is_cloaked = True
            except User.DoesNotExist:
                pass
