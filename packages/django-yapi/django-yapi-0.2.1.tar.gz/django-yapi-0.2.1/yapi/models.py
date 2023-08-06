import logging
from django.conf import settings
from django.db import models

# Instantiate logger.
logger = logging.getLogger(__name__)


class ApiKey(models.Model):
    """
    Keys used for authenticating API requests.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    key = models.CharField(max_length=200, unique=True, db_index=True)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField()
    
    def __unicode__(self):
        """
        String representation of the instance.
        """
        return str(self.user)


class ApiCall(models.Model):
    """
    Log details regarding API call.
    """
    date = models.DateTimeField()
    method = models.CharField(max_length=10)
    endpoint = models.CharField(max_length=100)
    source_ip = models.CharField(max_length=50)
    execution_start = models.DateTimeField()
    execution_end = models.DateTimeField()
    status = models.IntegerField()
    user_agent = models.CharField(max_length=200)
    authentication_class = models.CharField(max_length=50, blank=True)
    authentication_user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    authentication_token = models.CharField(max_length=200, blank=True)
    request_get_params = models.TextField(blank=True)
    request_data = models.TextField(blank=True)
    response_data = models.TextField(blank=True)
    
    def __unicode__(self):
        """
        String representation of the instance.
        """
        return self.method
    
    def execution_time(self):
        """
        Returns the execution time (in seconds) for the given API call.
        """
        return round((self.execution_end - self.execution_start).microseconds / float(1000000), 3)
    
    @staticmethod
    def new(date, method, endpoint, source_ip, execution_start, execution_end, status, user_agent,
            authentication=None, request_get_params=None, request_data=None, response_data=None):
        """
        Logs an API call.
        """
        api_call = ApiCall(date=date,
                           method=method,
                           endpoint=endpoint,
                           source_ip=source_ip,
                           execution_start=execution_start,
                           execution_end=execution_end,
                           status=status,
                           user_agent=user_agent)
        
        # If call was authenticated.
        if authentication:
            
            # Fetch details.
            authentication_user = authentication['user']
            authentication_class = authentication['class']
            authentication_token = authentication['token']
            
            # User.
            api_call.authentication_user = authentication_user
        
            # These details may not exist, but cannot be 'null' in the database, thus, replace by 'blank' if necessary.
            if not authentication_class:
                api_call.authentication_class = ''
            else:
                api_call.authentication_class = authentication_class
            if not authentication_token:
                api_call.authentication_token = ''
            else:
                api_call.authentication_token = authentication_token
                
        # If request/response data provided.
        if request_get_params:
            api_call.request_get_params = request_get_params
        if request_data:
            api_call.request_data = request_data
        if response_data:
            api_call.response_data = response_data
        
        # Save and return.
        api_call.save()
        return api_call