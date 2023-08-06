
from django.middleware.csrf import rotate_token
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY

from . import signals
from .models import Role

def set_role(request, role):
    '''
    Switch a logged in user to a different role on the same User.
    '''
    if not isinstance(request.user, Role):
        raise ValueError('Not a Role')

    if not request.user.user.roles.filter(pk=role.pk).exists():
        raise ValueError('Role does not belong to current User')

    old_role = request.user
    role.backend = old_role.backend
    request.user = role
    request.session[SESSION_KEY] = role.pk
    request.session[BACKEND_SESSION_KEY] = role.backend
    rotate_token(request)

    signals.role_changed.send(sender=request.user, old_role=old_role, new_role=role, session=request.session)
    return True
