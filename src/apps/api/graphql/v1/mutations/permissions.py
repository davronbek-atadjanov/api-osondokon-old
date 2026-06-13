# permissions.py
from django.core.exceptions import PermissionDenied
from apps.business.models import Membership

def get_user_membership(user, business_id):
    """Get user's membership for a business with prefetched permissions"""
    return Membership.objects.filter(
        user=user,
        business_id=business_id
    ).select_related('role').prefetch_related(
        'role__permissions',
        'permissions'
    ).first()

def check_category_permission(info, business_id, action):
    """
    Check if user has permission for specific category action
    Actions: 'view', 'create', 'edit', 'delete'
    """
    user = info.context.user
    if not user.is_authenticated:
        raise PermissionDenied("Authentication required")
    
    membership = get_user_membership(user, business_id)
    if not membership:
        raise PermissionDenied("You're not a member of this business")
    
    # Super admin bypass (if you have this concept)
    if getattr(membership.role, 'is_super_admin', False):
        return membership
    
    # Check both role permissions and individual membership permissions
    required_perm = f'can_{action}'
    menu_permissions = []
    
    # Get from role permissions
    role_perms = membership.role.permissions.filter(menu_name="categories").first()
    if role_perms:
        menu_permissions.append(role_perms)
    
    # Get from individual membership permissions
    member_perms = membership.permissions.filter(menu_name="categories").first()
    if member_perms:
        menu_permissions.append(member_perms)
    
    # Check if any permission set grants the required permission
    for perm in menu_permissions:
        if getattr(perm, required_perm, False):
            return membership
    
    raise PermissionDenied(f"You don't have {action} permission for categories")