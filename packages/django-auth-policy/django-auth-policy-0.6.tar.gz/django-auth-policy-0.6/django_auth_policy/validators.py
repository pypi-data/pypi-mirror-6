import unicodedata
import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from django_auth_policy import settings as dap_settings


def password_min_length(value):
    if dap_settings.PASSWORD_MIN_LENGTH_TEXT is None:
        return

    if len(value) < dap_settings.PASSWORD_MIN_LENGTH:
        msg = _(dap_settings.PASSWORD_MIN_LENGTH_TEXT).format(
            length=dap_settings.PASSWORD_MIN_LENGTH)
        raise ValidationError(msg, code='password_min_length')


def password_complexity(value):
    if not dap_settings.PASSWORD_COMPLEXITY:
        return

    pw_set = set(value)
    for rule in dap_settings.PASSWORD_COMPLEXITY:
        if not pw_set.intersection(rule['chars']):
            msg = _(dap_settings.PASSWORD_COMPLEXITY_TEXT).format(
                rule_text=_(rule['text']))
            raise ValidationError(msg, 'password_complexity')


def _normalize_unicode(value):
    value = unicodedata.normalize('NFKD', unicode(value))
    return value.encode('ascii', 'ignore').strip().lower()


def password_user_attrs(value, user):
    """ Validate if password doesn't contain values from a list of user
    attributes. Every attribute will be normalized into ascii and split
    on non alphanumerics.

    Use this in the clean method of password forms

    `value`: password
    `user`: user object with attributes

    Example, which would raise a ValidationError:

        user.first_name = 'John'
        password_user_attrs('johns_password', user)
    """
    if not dap_settings.PASSWORD_USER_ATTRS:
        return

    simple_pass = _normalize_unicode(value)
    _non_alphanum = re.compile(r'[^a-z0-9]')
    for attr in dap_settings.PASSWORD_USER_ATTRS:
        v = getattr(user, attr, None)
        if not attr or len(attr) < 4:
            continue

        v = _normalize_unicode(v)

        for piece in _non_alphanum.split(v):
            if len(piece) < 4:
                continue

            if piece in simple_pass:
                msg = _(dap_settings.PASSWORD_USER_ATTRS_TEXT).format(
                    piece=piece)
                raise ValidationError(msg, 'password_user_attrs')


def password_disallowed_terms(value):
    if not dap_settings.PASSWORD_DISALLOWED_TERMS:
        return

    simple_pass = _normalize_unicode(value)
    for term in dap_settings.PASSWORD_DISALLOWED_TERMS:
        term = _normalize_unicode(term)

        if term in simple_pass:
            msg = _(dap_settings.PASSWORD_DISALLOWED_TERMS_TEXT).format(
                terms=term)
            raise ValidationError(msg, 'password_disallowed_terms')
