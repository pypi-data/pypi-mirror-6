
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

try:
    NAMESPACE_MODEL = settings.SAAS_USER_NAMESPACE_MODEL
except AttributeError:
    raise ImproperlyConfigured('You must specify SAAS_USER_NAMESPACE_MODEL.')
