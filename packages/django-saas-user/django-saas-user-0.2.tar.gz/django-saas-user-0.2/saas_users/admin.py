
from django.contrib import admin

from . import models

class RoleInline(admin.TabularInline):
    model = models.Role
    # XXX Need to ensure namespace + group.namespace match

class UserAdmin(admin.ModelAdmin):
    inlines = [
        RoleInline,
    ]

admin.site.register(models.User, UserAdmin)
admin.site.register(models.Role)
admin.site.register(models.Group)
