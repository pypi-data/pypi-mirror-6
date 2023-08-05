
from django.dispatch import Signal

role_changed = Signal(providing_args=['old_role', 'new_role', 'session'])

