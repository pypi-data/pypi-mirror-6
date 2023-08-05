import logging

# Instantiate logger.
logger = logging.getLogger(__name__)


class BasePermission(object):
    """
    All permission classes should extend BasePermission.
    """

    def has_permission(self, request, user):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        raise NotImplementedError()
    
    
class IsStaff(BasePermission):
    """
    Check if user has staff permission.
    """
    
    def has_permission(self, request, user):
        """
        Please refer to the interface documentation.
        """
        if user and user.is_staff:
            return True
        else:
            return False