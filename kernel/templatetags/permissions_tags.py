from django import template

register = template.Library()


@register.filter
def permission(user, permission, obj):
    if user.has_perm(permission, obj):
        return True
    return False
