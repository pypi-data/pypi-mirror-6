import logging

from django.core.urlresolvers import resolve, reverse

from django_auth_policy.forms import StrictPasswordChangeForm
from django_auth_policy.utils import update_session
from django_auth_policy.settings import (CHANGE_PASSWORD_VIEW_NAME,
    LOGIN_VIEW_NAME, LOGOUT_VIEW_NAME)


logger = logging.getLogger(__name__)


class AuthenticationPolicyMiddleware(object):
    """ This middleware enforces the following policy:
    - Change of password when password has expired;
    - Change of password when user has a temporary password;
    - Logout disabled users;

    This is enforced using middleware to prevent users from accessing any page
    handled by Django without the policy being enforced.
    """
    change_password_path = reverse(CHANGE_PASSWORD_VIEW_NAME)
    login_path = reverse(LOGIN_VIEW_NAME)
    logout_path = reverse(LOGOUT_VIEW_NAME)

    def process_request(self, request):
        assert hasattr(request, 'user'), (
            'AuthenticationPolicyMiddleware needs a user attribute on '
            'request, add AuthenticationMiddleware before '
            'AuthenticationPolicyMiddleware in MIDDLEWARE_CLASSES')

        if not request.user.is_authenticated():
            return None

        # Log out disabled users
        if not request.user.is_active:
            logger.warning('Log out inactive user, user=%s', request.user)
            view_func, args, kwargs = resolve(self.logout_path)
            return view_func(request, *args, **kwargs)

        # Do not do password change for certain URLs
        if request.path in (self.change_password_path, self.login_path,
                            self.logout_path):
            return None

        # Check for 'enforce_password_change' in session set by login view
        if request.session.get('password_change_enforce', False):
            return self.password_change(request)

        return None

    def process_response(self, request, response):
        if not hasattr(request, 'user') or not request.user.is_authenticated():
            return response

        # When password change is enforced, check if this is still required
        # for next request
        if not request.session.get('password_change_enforce', False):
            return response

        update_session(request.session, request.user)

        return response

    def password_change(self, request):
        """ Return 'password_change' view.
        This resolves the view with the name 'password_change'.

        Overwrite this method when needed.
        """
        view_func, args, kwargs = resolve(self.change_password_path)

        assert issubclass(kwargs['password_change_form'],
                          StrictPasswordChangeForm), (
            "Use django_auth_policy StrictPasswordChangeForm for password "
            "changes.")

        # Provide extra context to be used in the password_change template
        is_exp = request.session.get('password_is_expired', False)
        is_tmp = request.session.get('password_is_temporary', False)
        if not 'extra_context' in kwargs:
            kwargs['extra_context'] = {}
        kwargs['extra_context']['is_enforced'] = True
        kwargs['extra_context']['is_temporary'] = is_tmp
        kwargs['extra_context']['is_expired'] = is_exp
        return view_func(request, *args, **kwargs)
