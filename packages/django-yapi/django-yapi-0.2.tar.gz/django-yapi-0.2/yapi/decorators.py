def authentication_classes(authentication_classes):
    """
    Specifies authentication requirements.
    """
    def decorator(func):
        func.authentication = authentication_classes
        return func
    return decorator


def permission_classes(permission_classes):
    """
    Specifies authorization requirements.
    """
    def decorator(func):
        func.permission = permission_classes
        return func
    return decorator