import datetime
import json
import logging
from django.http.response import HttpResponseNotAllowed, HttpResponse, HttpResponseForbidden

from authentication import AnyAuthentication
from models import ApiCall
from response import HTTPStatus, Response

# Instantiate logger.
logger = logging.getLogger(__name__)


class Resource:
    """
    Maps an API endpoint URL to its respective handler.
    """
    
    def __init__(self, handler):
        """
        Constructor.
        """
        if not callable(handler):
            raise AttributeError, "Handler not callable."
        self.handler = handler()
        
    def __call__(self, request, *args, **kwargs):
        """
        Call handler's method according to request HTTP verb.
        """
        
        ##################################
        #         Request Details        #
        ##################################
        
        requested_at = datetime.datetime.now()
        method = request.method
        endpoint = request.path
        source_ip = request.META['REMOTE_ADDR']
        user_agent = request.META['HTTP_USER_AGENT']
        
        ##################################
        #           HTTP Method          #
        ##################################
        
        # Check if verb is allowed.
        try:
            self.handler.allowed_methods.index(method.upper())
        except ValueError:
            return HttpResponseNotAllowed(self.handler.allowed_methods)
        # Variable containing allowed verbs does not exist, no verbs allowed then.
        except AttributeError:
            return HttpResponseNotAllowed([])
        
        # If verb is available, respective method must exist.
        meth = getattr(self.handler, method.lower(), None)
        if not meth:
            return HttpResponse(status=HTTPStatus.SERVER_ERROR_501_NOT_IMPLEMENTED)
        
        ##################################
        #         Authentication         #
        ##################################
        
        try:
            # If authentication is required, then the handler has the following attribute
            # consisting of an array of the available authentication types.
            authentication_classes = self.handler.authentication
            authentication = None
            
            # Check for valid credentials for each of the available authentication types.
            for ac in authentication_classes:
                try:
                    authentication = ac().authenticate(request)
                    # Break the loop as soon as the first authentication class successfully validates respective credentials.
                    if authentication:
                        break
                except NotImplementedError:
                    pass
                
            # If this place is reached without any of the authentication classes having returned success,
            # then authentication has failed and since we are here because this resource requires authentication,
            # the request is forbidden.
            if not authentication:
                return HttpResponse(status=HTTPStatus.CLIENT_ERROR_401_UNAUTHORIZED)
        
        # No authentication is required.
        except AttributeError:
            # Even though authentication is not required, check if request was made by an
            # authenticated user, for logging purposes. 
            authentication = AnyAuthentication().authenticate(request)
            
        # Put the result of the authentication in the request object, as it may be used in executing the API call
        # (e.g. figuring out how to serialize objects, given the user permissions)
        request.auth = authentication
            
        ##################################
        #          Authorization         #
        ##################################
        
        try:
            # If specific permissions are required, then the handler has the following attribute
            # consisting of an array of the required permissions.
            permission_classes = self.handler.permissions
            
            # If there are permission restrictions, then the request must be authenticated.
            if not authentication:
                return HttpResponseForbidden()
            
            # For the request to be authorized, ***ALL** the permission classes must return True.
            else:
                for p in permission_classes:
                    try:
                        if not p().has_permission(request, authentication['user']):
                            return HttpResponseForbidden()
                    # The permission class doesn't have the necessary method implemented, we consider the permission check as failed,
                    # thus, the user isn't authorized to access the resource.
                    except NotImplementedError:
                        return HttpResponseForbidden()
                
        # There aren't any permission restrictions.
        except AttributeError:
            pass
        
        ##################################
        #          Request Body          #
        ##################################
         
        # Some requests require for a body.
        try:
            ['POST', 'PUT'].index(method.upper())
            
            # If this place is reached, then the HTTP request should have a body.
            try:
                
                # Don't process body if request haz files, because it messes up stream and stuff and basically
                # everything blows up.
                # TODO: Got to figure this out better.
                if request.FILES:
                    request.data = request.FILES
                
                # Business as usual...
                else:
                    # For now, the only parser suported is JSON.
                    data = json.loads(request.body)
                    
                    # If this place is reached, then body was successfully parsed. Add it to the request object.
                    request.data = data
            
            # Error parsing request body to JSON.
            except ValueError:
                return HttpResponse(content=json.dumps({ 'message': 'Missing arguments' }),
                                    status=HTTPStatus.CLIENT_ERROR_400_BAD_REQUEST,
                                    mimetype='application/json')
        except ValueError:
            pass
        except:
            logger.error('Unable to process request body!', exc_info=1)
            return Response(request=request,
                            data={ 'message': 'Resource #1' },
                            serializer=None,
                            status=HTTPStatus.SERVER_ERROR_500_INTERNAL_SERVER_ERROR)
        
        ##################################
        #          Execute Call          #
        ##################################
            
        # Invoke method, logging execution time start and end.
        exec_start = datetime.datetime.now()
        try:
            result = meth(request, *args, **kwargs)
        except:
            logger.error('Error executing API call', exc_info=1)
            result = HttpResponse(status=HTTPStatus.SERVER_ERROR_500_INTERNAL_SERVER_ERROR)
        exec_end = datetime.datetime.now()
        
        ##################################
        #               Log              #
        ##################################
        
        try:
            request_data = None
            response_data = None
        
            # If bad request, log request data (POST and PUT) and response body.
            if result.status_code >= 400 and result.status_code <= 599:
                if method == 'POST' or method == 'PUT':
                    request_data = request.data
                response_data = result.content
            
            # Log.
            ApiCall.new(date=requested_at,
                        method=method,
                        endpoint=endpoint,
                        source_ip=source_ip,
                        execution_start=exec_start,
                        execution_end=exec_end,
                        status=result.status_code,
                        user_agent=user_agent,
                        authentication=authentication,
                        request_data=request_data,
                        response_data=response_data)
        
        except:
            logger.error('Unable to log API call!', exc_info=1)
            return Response(request=request,
                            data={ 'message': 'Resource #2' },
                            serializer=None,
                            status=HTTPStatus.SERVER_ERROR_500_INTERNAL_SERVER_ERROR)
        
        ##################################
        #             Return             #
        ##################################
        
        return result