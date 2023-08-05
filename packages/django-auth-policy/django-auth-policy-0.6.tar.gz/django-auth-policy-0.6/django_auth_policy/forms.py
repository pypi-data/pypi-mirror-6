import logging
try:
    from collections import OrderedDict
except ImportError:
    # python 2.6 or earlier, use backport
    from ordereddict import OrderedDict

from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm

from django_auth_policy.models import PasswordChange, LoginAttempt
from django_auth_policy.validators import (password_min_length,
                                           password_complexity,
                                           password_user_attrs,
                                           password_disallowed_terms)
from django_auth_policy.checks import (disable_expired_users,
                                       locked_username,
                                       locked_remote_addr)


logger = logging.getLogger(__name__)


# Authentication form error messages
auth_error_messages = {
    'invalid_login': _("Please enter a correct username and password. "
                       "Note that both fields may be case-sensitive."),
    'inactive': _("This account is inactive."),
    'username_locked_out': _('Your account has been locked. Contact your '
                             'user administrator for more information.'),
    'address_locked_out': _('Your account has been locked. Contact your '
                            'user administrator for more information.')
}


def pre_auth_checks(username, password, remote_addr, host,
                    error_messages=auth_error_messages):
    """ Raises ValidationError on failed login attempts
    Returns valid user instance or None
    """
    logger.info('Authentication attempt, username=%s, address=%s',
                username, remote_addr)

    if not username and not password:
        return None

    username_len = LoginAttempt._meta.get_field('username').max_length
    attempt = LoginAttempt(
        username=username[:username_len],
        source_address=remote_addr,
        hostname=host[:100],
        successful=False,
        lockout=True)

    if not username:
        logger.warning(u'Authentication failure, address=%s, '
                       'no username supplied.',
                       remote_addr)
        attempt.save()
        raise forms.ValidationError(
            error_messages['invalid_login'], code='invalid_login')

    if not password:
        logger.warning(u'Authentication failure, username=%s, '
                       'address=%s, no password supplied.',
                       username, remote_addr)
        attempt.save()
        raise forms.ValidationError(
            error_messages['invalid_login'], code='invalid_login')

    if locked_username(username):
        logger.warning(u'Authentication failure, username=%s, address=%s, '
                       'username locked', username, remote_addr)
        attempt.save()
        raise forms.ValidationError(
            error_messages['username_locked_out'], code='username_locked_out')

    if locked_remote_addr(remote_addr):
        logger.warning(u'Authentication failure, username=%s, address=%s, '
                       'address locked', username, remote_addr)
        attempt.save()
        raise forms.ValidationError(
            error_messages['address_locked_out'], code='address_locked_out')

    disable_expired_users()

    return attempt


def post_auth_checks(user, attempt, error_messages=auth_error_messages):

    attempt.user = user

    if user is None:
        logger.warning(u'Authentication failure, username=%s, '
                       'address=%s, invalid authentication.',
                       attempt.username, attempt.source_address)
        attempt.save()
        raise forms.ValidationError(
            error_messages['invalid_login'], code='invalid_login')

    if not user.is_active:
        logger.warning(u'Authentication failure, username=%s, '
                       'address=%s, user inactive.',
                       attempt.username, attempt.source_address)
        attempt.save()
        raise forms.ValidationError(
            error_messages['inactive'], code='inactive')

    # Authentication was successful
    logger.info(u'Authentication success, username=%s, address=%s',
                attempt.username, attempt.source_address)
    attempt.successful = True
    attempt.lockout = False
    attempt.save()

    # Reset lockout counts for IP address and username
    LoginAttempt.objects.filter(username=attempt.username,
                                lockout=True).update(lockout=False)
    LoginAttempt.objects.filter(source_address=attempt.source_address,
                                lockout=True).update(lockout=False)

    return user


class StrictAuthenticationForm(AuthenticationForm):
    error_messages = auth_error_messages

    def __init__(self, request, *args, **kwargs):
        """ Make request argument required
        """
        return super(StrictAuthenticationForm, self).__init__(request, *args,
                                                              **kwargs)

    def clean(self):
        remote_addr = self.request.META['REMOTE_ADDR']
        host = self.request.get_host()
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        attempt = pre_auth_checks(username, password, remote_addr, host,
                                  self.error_messages)

        self.user_cache = authenticate(username=username, password=password)

        post_auth_checks(self.user_cache, attempt, self.error_messages)

        return self.cleaned_data


class StrictSetPasswordForm(forms.Form):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        }
    new_password1 = forms.CharField(label=_("New password"),
                                    widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=_("New password confirmation"),
                                    widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(StrictSetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password1(self):
        pw = self.cleaned_data.get('new_password1')
        if pw:
            password_min_length(pw)
            password_complexity(pw)
            password_user_attrs(pw, self.user)
            password_disallowed_terms(pw)
        return pw

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

    def is_valid(self):
        valid = super(StrictSetPasswordForm, self).is_valid()
        if self.is_bound:
            PasswordChange.objects.create(user=self.user, successful=valid,
                                          is_temporary=False)
            if valid:
                logger.info('Password change successful for user %s',
                            self.user)
            else:
                logger.info('Password change failed for user %s',
                            self.user)
        return valid

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user


class StrictPasswordChangeForm(StrictSetPasswordForm):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'password_incorrect': _("Your old password was entered incorrectly. "
                                "Please enter it again."),
        'password_unchanged': _("The new password must not be the same as "
                                "the old password"),
        }
    old_password = forms.CharField(label=_("Old password"),
                                   widget=forms.PasswordInput)

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password

    def clean_new_password1(self):
        pw = super(StrictPasswordChangeForm, self).clean_new_password1()

        # Check that old and new password differ
        if (self.cleaned_data.get('old_password') and
                self.cleaned_data['old_password'] == pw):

            raise forms.ValidationError(
                self.error_messages['password_unchanged'],
                'password_unchanged')

        return pw


StrictPasswordChangeForm.base_fields = OrderedDict(
    (k, StrictPasswordChangeForm.base_fields[k])
    for k in ['old_password', 'new_password1', 'new_password2']
)
