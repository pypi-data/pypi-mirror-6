import datetime
import logging
from django.core.exceptions import ObjectDoesNotExist

from models import ApiKey

# Instantiate logger.
logger = logging.getLogger(__name__)


class BaseAuthentication(object):
    """
    All authentication classes should extend BaseAuthentication.
    """

    def authenticate(self, request):
        """
        Authenticate the request validating respective credentials and, if successful, return a dict containing
        the authentication class, the user and (optional) the token (i.e. API Key).
        """
        raise NotImplementedError()
        

class SessionAuthentication(BaseAuthentication):
    """
    Use Django's session framework for authentication.
    """
    
    def authenticate(self, request):
        """
        Please refer to the interface documentation.
        """        
        # There is an active user logged in.
        if request.user.is_authenticated() and request.user.is_active:
            return {
                'class': self.__class__.__name__,
                'user': request.user,
                'token': None
            }
        else:
            return None
    
    
class ApiKeyAuthentication(BaseAuthentication):
    """
    Simple API Key based authentication. The 'api_key' should be provided via GET parameter.
    """
    
    def authenticate(self, request):
        """
        Please refer to the interface documentation.
        """
        # Fetch mandatory param.
        try:
            api_key = request.GET['api_key']
        except KeyError:
            return None
        
        # Check if key is valid and active.
        try:
            key = ApiKey.objects.get(key=api_key, active=True)
            
            # If this place is reached, then we have a valid API key.
            key.last_used = datetime.datetime.now()
            key.save()
            
            # Return.
            return {
                'class': self.__class__.__name__,
                'user': key.user,
                'token': api_key
            }
        
        # Key does not exist or isn't active.
        except ObjectDoesNotExist:
            return None 
    
    
class AnyAuthentication(BaseAuthentication):
    """
    Attempt to validate credentials using all available classes.
    """
    
    def authenticate(self, request):
        """
        Please refer to the interface documentation.
        """
        for ac in [SessionAuthentication, ApiKeyAuthentication]:
            try:
                authentication = ac().authenticate(request)
                # Break the loop as soon as the first authentication class successfully validates respective credentials.
                if authentication:
                    return authentication
            except NotImplementedError:
                pass
            
        # If this place was reached, then none of the authentication classes were successfull.
        return None