import datetime
import json
import logging
from django.middleware.csrf import CsrfViewMiddleware
from django.http.response import HttpResponseNotAllowed, HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from authentication import AnyAuthentication
from models import ApiCall
from response import HTTPStatus, Response
from django.views.generic.base import View

# Instantiate logger.
logger = logging.getLogger(__name__)


class Resource(View):
    """
    Maps an API endpoint URL to its respective handler.
    """
        
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
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
            self.allowed_methods.index(method.upper())
        except ValueError:
            return HttpResponseNotAllowed(self.allowed_methods)
        # Variable containing allowed verbs does not exist, no verbs allowed then.
        except AttributeError:
            return HttpResponseNotAllowed([])
        
        # If verb is available, respective method must exist.
        meth = getattr(self, method.lower(), None)
        if not meth:
            return HttpResponse(status=HTTPStatus.SERVER_ERROR_501_NOT_IMPLEMENTED)
        
        ##################################
        #         Authentication         #
        ##################################
        
        #
        # 1) Check for authentication requirements.
        #
        
        ####
        # a) Handler-wide authentication (i.e. ALL methods require auth) ------>
        try:
            # If authentication is required, then the handler has the following attribute
            # consisting of an array of the available authentication types.
            authentication_classes = self.authentication
        # <------ No handler-wide authentication required.
        except AttributeError:
        
            ####
            # b) Check for method-specific authentication requirements. ------>
            try:
                # If authentication is required, the respective method decorator adds the array of
                # available authentication types to the following method var.
                authentication_classes = meth.authentication
            # <------ No method-specific authentication required.
            except AttributeError:
                
                ####
                # c) If this place is reached, then NO auth is required. Period. ------>
                authentication_classes = None
                # <------
        
        #
        # 2) Authentication is required! Check for any valid auth credentials, according to available auth types.
        #
        if authentication_classes:
            
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
        
        #
        # 3) No authentication is required.
        #
        else:
            # Even though authentication is not required, check if request was made by an
            # authenticated user, for logging purposes. 
            authentication = AnyAuthentication().authenticate(request)
            
        # Put the result of the authentication in the request object, as it may be used in executing the API call
        # (e.g. figuring out how to serialize objects, given the user permissions)
        request.auth = authentication
        
        ##################################
        #        CSRF Validation         #
        ##################################
        
        # When request is anonymous or authenticated via Django session, explicitly perform CSRF validation.
        if not request.auth or request.auth['class'] == 'SessionAuthentication':
            reason = CsrfViewMiddleware().process_view(request, None, (), {})
            # CSRF Failed.
            if reason:
                return HttpResponse(content=json.dumps({ 'message': 'CSRF verification failed. Request aborted.' }),
                                    status=HTTPStatus.CLIENT_ERROR_403_FORBIDDEN,
                                    mimetype='application/json')
            
        ##################################
        #          Authorization         #
        ##################################
        
        #
        # 1) Check for permission requirements.
        #
        
        ####
        # a) Handler-wide permissions (i.e. ALL methods same permissions) ------>
        try:
            # If specific permissions are required, then the handler has the following attribute
            # consisting of an array of the required permissions.
            permission_classes = self.permissions
        # <------ No handler-wide permissions required.
        except AttributeError:
        
            ####
            # b) Check for method-specific permission requirements. ------>
            try:
                # If permission is required, the respective method decorator adds the array of
                # required permission types to the following method var.
                permission_classes = meth.permission
            # <------ No method-specific permissions required.
            except AttributeError:
                
                ####
                # c) If this place is reached, then are NOT permission requirements. Period. ------>
                permission_classes = None
                # <------
                
        #
        # 2) Validate permissions.
        #
        if permission_classes:
            
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
        else:
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
                        request_get_params=dict(request.GET.iterlists()),
                        request_data=request_data,
                        response_data=response_data)
        
        # If error occurs, JUST log. If this place is reached, then the request was successfully
        # executed and result should be returned.
        except:
            logger.error('Unable to log API call!', exc_info=1)
        
        ##################################
        #             Return             #
        ##################################
        
        return result