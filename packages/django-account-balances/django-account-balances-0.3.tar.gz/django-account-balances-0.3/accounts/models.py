from accounts import abstract_models
from django.db import models

try:
    from oscar.core.compat import AUTH_USER_MODEL
except ImportError:
    from django.conf import settings
    AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

class AccountType(abstract_models.AccountType):
    pass


class Account(abstract_models.Account):
    pass


class Transfer(abstract_models.Transfer):
    pass


class Transaction(abstract_models.Transaction):
    pass


class IPAddressRecord(abstract_models.IPAddressRecord):
    pass

class AccountSecondaryUsers(models.Model):

    # The secondary users hooks to the user model, which may vary by project
    # explicitly link to the custom model here, if defined, to ease migration
    account = models.ForeignKey(Account)
    user = models.ForeignKey(AUTH_USER_MODEL)
