.. _index:

==================
Django Auth Policy
==================

Installation instructions
=========================

Follow these steps to install ``django_auth_policy``:

* Install ``django_auth_policy`` using pip, easy_install or the
  provided setup.py.

* Add ``django_auth_policy`` to Django setting ``INSTALLED_APPS``.

* Add ``django_auth_policy.middleware.AuthenticationPolicyMiddleware`` to the
  Django setting ``MIDDLEWARE_CLASSES``, make sure to include it *after* the
  ``AuthenticationMiddleware``.

* Use the authentication form and the change password forms from
  ``django_auth_policy.forms``. For inspiration on how to use these forms
  have a look at ``django_auth_forms.urls.py``.

* Add policies to your settings, a good starting point can be::

    AUTHENTICATION_POLICIES = (
        ('django_auth_policy.authentication.AuthenticationBasicChecks', {}),
        ('django_auth_policy.authentication.AuthenticationDisableExpiredUsers', {}),
        ('django_auth_policy.authentication.AuthenticationLockedUsername', {}),
        ('django_auth_policy.authentication.AuthenticationLockedRemoteAddress', {}),
    )

    PASSWORD_STRENGTH_POLICIES = (
        ('django_auth_policy.password_strength.PasswordMinLength', {}),
        ('django_auth_policy.password_strength.PasswordContainsUpperCase', {}),
        ('django_auth_policy.password_strength.PasswordContainsLowerCase', {}),
        ('django_auth_policy.password_strength.PasswordContainsNumbers', {}),
        ('django_auth_policy.password_strength.PasswordContainsSymbols', {}),
        ('django_auth_policy.password_strength.PasswordUserAttrs', {}),
        ('django_auth_policy.password_strength.PasswordDisallowedTerms', {
            'terms': ['Testsite']
        }),
    )

    PASSWORD_CHANGE_POLICIES = (
        ('django_auth_policy.password_change.PasswordChangeExpired', {}),
        ('django_auth_policy.password_change.PasswordChangeTemporary', {}),
    )

  Update the ``terms`` of ``PasswordDisallowedTerms`` to a list of terms one
  does not allow in passwords. Like the name and domainname of the site.

  Check the source code of the policies to see which settings are available per
  policy (like the ``terms`` of the ``PasswordDisallowedTerms``).

* Run the ``./manage.py check_auth_policy`` command as a sanity check if
  everything is in place. This command is **NO guarantee** since it\'s easy
  for developers to work around the checks performed by this command.
