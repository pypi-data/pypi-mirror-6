import logging

from django.utils.translation import ugettext as _

from django_auth_policy.checks import enforce_password_change
from django_auth_policy import settings as dap_settings


logger = logging.getLogger(__name__)


def update_session(session, user):
    """ Check for temporary or expired passwords and store in session
    Our middleware should enforce a password change in next request
    """
    enforce, is_exp, is_temp = enforce_password_change(user)

    # Log password enforcement
    if enforce:
        if is_temp and not session.get('password_is_temporary'):
            logger.info(u'User %s must change temporary password', user)

        if is_exp and not session.get('password_is_expired'):
            logger.info(u'User %s must change expired password', user)

        if (not is_temp and not is_exp and
            not session.get('password_change_enforce')):
            logger.info(u'User %s must change password', user)

    session['password_change_enforce'] = enforce
    session['password_is_expired'] = is_exp
    session['password_is_temporary'] = is_temp


def password_policy_texts():
    """ Returns a list of policy rules for passwords as enforces by
    Django Auth Policy. Use this to display policy rules on pages
    with change password forms.

    Every rule has a text and an optional caption.
    """
    rules = []

    if dap_settings.PASSWORD_MIN_LENGTH:
        rules.append({
            'text': _(dap_settings.PASSWORD_MIN_LENGTH_TEXT).format(
                length=dap_settings.PASSWORD_MIN_LENGTH),
            'caption': '',
        })

    for rule in dap_settings.PASSWORD_COMPLEXITY:
        rules.append({
            'text': _(dap_settings.PASSWORD_COMPLEXITY_TEXT).format(
                rule_text=_(rule['text'])),
            'caption': _('Allowed characters: {chars}').format(
                chars=rule['chars']),
        })

    if dap_settings.MAX_PASSWORD_AGE:
        rules.append({
            'text': _(dap_settings.MAX_PASSWORD_AGE_TEXT).format(
                age=dap_settings.MAX_PASSWORD_AGE),
            'caption': '',
        })

    return rules
