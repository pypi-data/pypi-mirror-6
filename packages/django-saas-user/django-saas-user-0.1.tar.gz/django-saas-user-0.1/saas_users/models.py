
from django.contrib.auth import models as auth
from django.contrib.auth.hashers import (check_password, make_password,
    UNUSABLE_PASSWORD_PREFIX)
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from . import settings


class UserManager(auth.BaseUserManager):
    pass

@python_2_unicode_compatible
class User(models.Model):

    email = models.EmailField(unique=True)
    password = models.CharField(_('password'), max_length=128,
        default=UNUSABLE_PASSWORD_PREFIX
    )
    last_login = models.DateTimeField(_('last login'), default=timezone.now)

    is_active = True

    is_superuser = models.BooleanField(_('superuser status'), default=False)

    objects = UserManager()

    def __str__(self):  # pragma: no cover
        return self.email

    def get_default_role(self):
        return self.roles.order_by('pk')[0]

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        def setter(raw_password):  # pragma: no cover
            '''Called by the password hasher if the password needs updating.'''
            self.set_password(raw_password)
            self.save(update_fields=["password"])
        return check_password(raw_password, self.password, setter)


class Role(models.Model):
    user = models.ForeignKey('User', related_name='roles')

    namespace = models.ForeignKey(settings.NAMESPACE_MODEL)
    last_login = models.DateTimeField(_('last login'), default=timezone.now)

    is_active = models.BooleanField(default=False)
    is_superrole = models.BooleanField(default=False)

    # Permissions API
    groups = models.ManyToManyField('Group', verbose_name=_('groups'), blank=True,
        help_text=_('The groups this user belongs to. A user will get all '
            'permissions granted to each of his/her group.'
        ),
        related_name="role_set", related_query_name="role")
    user_permissions = models.ManyToManyField('auth.Permission',
        verbose_name=_('user permissions'), blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="role_set", related_query_name="role")

    class Meta:
        unique_together = (
            ('user', 'namespace'),
        )

    def is_anonymous(self):
        return False
    def is_authenticated(self):
        return True

    @property
    def is_superuser(self):
        return self.user.is_superuser

    # XXX Proxy these calls to User?
    # set_password
    # check_password
    # set_unusable_password
    # has_usable_password
    def get_full_name(self):
        return u'[%s] %s' % (self.namespace, self.user.email,)

    def get_short_name(self):
        return self.user.email

    def get_group_permissions(self, obj=None):
        '''
        Yield a set of permissions this Role inherits from groups.
        '''
        if obj is not None:
            # We don't support per-object permissions
            return set()

        Permission = models.get_model('auth', 'Permission')
        # We cache the result, just like auth.User does
        if not hasattr(self, '_role_group_perm_cache'):
            if self.is_superuser:
                # Superuser gets all permissions
                perms = Permission.objects.all()
            elif self.is_superrole:
                # Superrole gets all permissions in all groups for this
                # namespace
                perms = Permission.objects.filter(
                    role_groups__namespace=self.namespace,
                )
            else:
                # Find all permissions for all Groups this Role is a member of.
                perms = Permission.objects.filter(
                    role_groups__role=self,
                    role_groups__namespace=self.namespace,
                )
            # Construct the set as a list of "app_label.permission_name" strings.
            perms = perms.values_list('content_type__app_label', 'codename').order_by()
            self._role_group_perm_cache = set("%s.%s" % (ct, name) for ct, name in perms)
        return self._role_group_perm_cache

    def get_all_permissions(self, obj=None):
        if obj is not None:
            return set()

        if not hasattr(self, '_role_perm_cache'):
            self._role_perm_cache = set("%s.%s" % (p.content_type.app_label, p.codename) for p in self.user_permissions.select_related())
            self._role_perm_cache.update(self.get_group_permissions(obj))
        return self._role_perm_cache

    def has_perm(self, perm, obj=None):
        if not self.is_active:
            return False

        if self.is_superuser:
            return True

        return perm in self.get_all_permissions(obj)

    def has_perms(self, perm_list, obj=None):
        return all(
            self.has_perm(perm, obj)
            for perm in perm_list
        )

    def has_module_perms(self, app_label):
        if not self.is_active:
            return False

        if self.is_superuser:
            return True

        return any(
            perm[:perm.index('.')] == app_label
            for perm in self.get_all_permissions()
        )


@python_2_unicode_compatible
class Group(models.Model):
    namespace = models.ForeignKey(settings.NAMESPACE_MODEL)
    name = models.CharField(_('name'), max_length=80, unique=True)
    permissions = models.ManyToManyField('auth.Permission',
        verbose_name=_('permissions'), blank=True,
        related_name='role_groups',
    )

    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')
        unique_together = (
            ('namespace', 'name'),
        )

    def __str__(self):  # pragma: no cover
        return u'[%s] %s' % (self.namespace, self.name,)
