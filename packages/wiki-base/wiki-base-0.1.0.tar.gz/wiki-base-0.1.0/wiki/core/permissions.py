from wiki.conf import settings

###############################
# TARGET PERMISSION HANDLING #
###############################
#
# All functions are:
#   can_something(target, user)
#      => True/False
#
# All functions can be replaced by pointing their relevant
# settings variable in wiki.conf.settings to a callable(target, user)

def can_read(target, user):
    if callable(settings.CAN_READ):
        return settings.CAN_READ(target, user)
    else:
        # Deny reading access to deleted entities if user has no delete access
        is_deleted = target.current_revision and target.deleted
        if is_deleted and not target.can_delete(user):
            return False
        
        # Check access for other users...
        if user.is_anonymous() and not settings.ANONYMOUS:
            return False
        elif target.other_read:
            return True
        elif user.is_anonymous():
            return  False
        if user == target.owner:
            return True
        if target.group_read:
            if target.group and user.groups.filter(id=target.group.id).exists():
                return True
        if target.can_moderate(user):
            return True
        return False
        
def can_write(target, user):
    if callable(settings.CAN_WRITE):
        return settings.CAN_WRITE(target, user)
    # Check access for other users...
    if user.is_anonymous() and not settings.ANONYMOUS_WRITE:
        return False
    elif target.other_write:
        return True
    elif user.is_anonymous():
        return  False
    if user == target.owner:
        return True
    if target.group_write:
        if target.group and user and user.groups.filter(id=target.group.id).exists():
            return True
    if target.can_moderate(user):
        return True
    return False

def can_assign(target, user):
    if callable(settings.CAN_ASSIGN):
        return settings.CAN_ASSIGN(target, user)
    return not user.is_anonymous() and user.has_perm('wiki.assign')

def can_assign_owner(target, user):
    if callable(settings.CAN_ASSIGN_OWNER):
        return settings.CAN_ASSIGN_OWNER(target, user)
    return False

def can_change_permissions(target, user):
    if callable(settings.CAN_CHANGE_PERMISSIONS):
        return settings.CAN_CHANGE_PERMISSIONS(target, user)
    return (
        not user.is_anonymous() and (
            target.owner == user or
            user.has_perm('wiki.assign')
        )
    )

def can_delete(target, user):
    if callable(settings.CAN_DELETE):
        return settings.CAN_DELETE(target, user)
    return not user.is_anonymous() and target.can_write(user)

def can_moderate(target, user):
    if callable(settings.CAN_MODERATE):
        return settings.CAN_MODERATE(target, user)
    return not user.is_anonymous() and user.has_perm('wiki.moderate')

def can_admin(target, user):
    if callable(settings.CAN_ADMIN):
        return settings.CAN_ADMIN(target, user)
    return not user.is_anonymous() and user.has_perm('wiki.admin')

