===============
django-yapi
===============

YAPI == Yet/Why Another API Framework

This is a mini-framework for creating RESTful APIs in Django.


Installation
============

1. Download dependencies:
    - Python 2.6+
    - Django 1.5+
    
2. ``pip install django-yapi`` or ``easy_install django-yapi``



Configuration
=============

settings.py
-----------

1. Add "yapi" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        # all other installed apps
        'yapi',
    )
      
2. Add logger handler::

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            # all other handlers
            'log_file_yapi': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(os.path.join(os.path.dirname( __file__ ), '..'), 'logs/yapi.log'),
                'maxBytes': '16777216', # 16megabytes
             },
        },
        'loggers': {
            # all other loggers
            'yapi': {
                'handlers': ['log_file_yapi'],
                'propagate': True,
                'level': 'DEBUG',
            }
        }
    }
    
3. Make sure you have a 'HOST_URL' setting containing the address in which the app is deployed:
    ``HOST_URL = 'http://localhost:8000'`` (example)

Logs
----

Create a 'logs' folder in your project's root folder (if you don't have one already).
Your project folder should look something like this::

    myproject/
        __init__.py
        settings.py
        urls.py
        wsgi.py
    logs/
    manage.py

Database
--------

Run ``python manage.py syncdb`` to create the yapi models.


API Namespace
=============

Now, you will have to decide the URL "namespace" from which your API will be available and add it to
your top-level ``urls.py``.

Yapi's **convention** is that everything that regards to the API (urls, handlers, serializers, etc) should be in a
package named "api" inside the respective app package. This way, the API namespace should point to a urls.py
inside an "api" package in your project's main package::

    myapp/
        api/
            __init__.py
            handlers.py
            serializers.py
            urls.py
        __init__.py
        models.py
        urls.py
        views.py
    myproject/
        api/
            __init__.py
            urls.py
        __init__.py
        settings.py
        urls.py
        wsgi.py
    logs/
    manage.py

Add namespace to the top-level ``urls.py``::

    # myproject/urls.py
    # ============

    urlpatterns = patterns('',
       # all other url mappings
       url(r'^api', include('myproject.api.urls', namespace='api')),
    )
    
In this example, we have an app called "myapp" which has an API. In order for it to be "acessible", its URLs must be
added to the top-level API namespace::

    # myproject/api/urls.py
    # ============
    
    urlpatterns = patterns('',
        # all other api url mappings
        url(r'^/myapp', include('myapp.api.urls', namespace='myapp')),
    )
    
Resources
=========

A "Resource" maps an URL to the code that will handle the requests made to it.

By convention, Resource handlers reside in a file called ``handlers.py`` in the api package::

    # myapp/api/handlers.py
    # ============

	from yapi.resource import Resource
    from yapi.response import HTTPStatus, Response

    class ResourceIndex(Resource):
        """
        API endpoint handler.
        """
    
        # HTTP methods allowed.
        allowed_methods = ['GET']
    
        def get(self, request):
            """
            Process GET request.
            """
                                
            # Return.
            return Response(request=request,
                            data={ 'hello': 'world' },
                            serializer=None,
                            status=HTTPStatus.SUCCESS_200_OK)
                            
Now we map the handler to a given URL::

    # myapp/api/urls.py
    # ============
    
    from django.conf.urls import patterns, url
    from yapi.resource import Resource

    from handlers import ResourceIndex

    urlpatterns = patterns('',
        url(r'^/?$', ResourceIndex.as_view(), name='index'),
    )
    
This way, if put ``http://localhost:8000/api/myapp`` in the address bar of your browser, you should get a JSON object
in return containing ``{ 'hello': 'world' }``.

Basic Schema
------------

From the example above we can see how easy it is to write a Resource class. You just need to set the ``allowed_methods``
array with the HTTP verbs that the handler supports and then, for each allowed verb, write the respective method.

Yapi's **convention** is to use POST/GET/PUT/DELETE to CREATE/READ/UPDATE/DELETE.

- ``POST`` -> ``def post(request)``
- ``GET`` -> ``def get(request)``
- ``PUT`` -> ``def put(request)``
- ``DELETE`` -> ``def delete(request)``

**IMPORTANT:** In this example there isn't any additional value being passed by the URL, therefore the only data received
by the methods is the standard Django ``request``. Make sure to include in the method any other additional parameter
that may be passed by the URL.

Authentication & Authorization
------------------------------

If the resource should only be accessible via authenticated users, then a variable ``authentication`` should be set
with an array of the valid authentication types. Yapi ships with the following authentication methods:

- ``yapi.authentication.SessionAuthentication`` -> Validates if the request is made by a browser with a valid Django session (i.e. user is logged in to the site)
- ``yapi.authentication.ApiKeyAuthentication`` -> Validates if the request is made with a valid ``api_key`` provided as a GET parameter.

When several authentication methods are accepted, **the request is considered authenticated as soon as one checks**
(e.g. SessionAuthentication fails, but APIKeyAuthentication validates). If the user is authenticated, it is added to
the ``request`` object and can be accessed by ``request.auth['user']``.

If the resource should only be acessible by authenticated users that match a specifc ruleset, then ``permissions``
should be set with an array of all the authorization credentials required. Yapi ships with the following authorization
methods:

- ``yapi.permissions.IsStaff`` -> Checks if user has Staff permission.

**In order for the authorization to be validated all authorization classes must check**.

If we wanted to make the Resource in the example above only available to authenticated staff users, it would look
something like this::

    # myapp/api/handlers.py
    # ============

    from yapi.authentication import SessionAuthentication, ApiKeyAuthentication
    from yapi.resource import Resource
    from yapi.response import HTTPStatus, Response

    class ResourceIndex(Resource):
        """
        API endpoint handler.
        """
    
        # HTTP methods allowed.
        allowed_methods = ['GET']
        
        # Authentication & Authorization.
        authentication = [SessionAuthentication, ApiKeyAuthentication]
        permissions = [IsStaff]
    
        def get(self, request):
            """
            Process GET request.
            """
                                
            # Return.
            return Response(request=request,
                            data={ 'hello': 'world' },
                            serializer=None,
                            status=HTTPStatus.SUCCESS_200_OK)
                            
Request Body
------------

When the request is a ``POST`` or a ``PUT``, it is assumed that there is a request body and, if it isn't present or fails
parsing, the request fails.

**IMPORTANT** Currently, the only format accepted for the request body is a JSON payload.

The request body is parsed into a native Python ``dict`` and can be acessible in ``request.data``.
    
Resource Listing
----------------

In trying to follow some HATEOAS principles, we suggest that the API's root URL should return a listing of the available
resources and respective URLs::

    # myproject/api/resources.py
    # ============
    
    from django.conf import settings
    from django.core.urlresolvers import reverse

    def get_api_resources_list(user):
        return {
            'url': settings.HOST_URL + reverse('api:index'),
            'resources': {
                'myapp': {
                    'url': settings.HOST_URL + reverse('api:myapp:index')
                }
            }
        }
        
Now, add it to the API's root URL::

    # myproject/api/urls.py
    # ============
    
    urlpatterns = patterns('',
        # all other api url mappings
        url(r'^/?$', ResourcesListHandler.as_view(), name='index'),
        url(r'^/myapp', include('myapp.api.urls', namespace='myapp')),
    )
    
And write the respective handler::

    # myproject/api/handlers.py
    # ============
  
  	from yapi.resource import Resource
    from yapi.response import HTTPStatus, Response
    from resources import get_api_resources_list

    class ResourcesListHandler(Resource):
        """
        API endpoint handler.
        """
    
        # HTTP methods allowed.
        allowed_methods = ['GET']
    
        def get(self, request):
            """
            Process GET request.
            """
                                
            # Return.
            return Response(request=request,
                            data=get_api_resources_list(request.auth['user']),
                            serializer=None,
                            status=HTTPStatus.SUCCESS_200_OK)
                            
Don't forget to keep this list updated everytime you make changes to your resources.

Response
=========

``yapi.response.Response`` is the prefered way of returning a call to a given handler (Django's ``HTTPResponse`` also works)

- ``request`` -> The request that originated this response.
- ``data`` -> The raw response data (a Python *dict*, with all data in native types)
- ``serializer`` -> The serializer that will be used to serialize the data.
- ``status`` -> The HTTP status code of the response (preferably from ``yapi.response.HTTPStatus``)
- ``pagination`` (optional) -> When the response data is a QuerySet, this states if the response should be paginated or not. Default is True.
- ``filters`` (optional) -> When the response data is a QuerySet and it was filtered by given parameters, they are provided in this field.

Serializers
-----------

When the response ``data`` is a *complex* Python object, it must first be serialized to native Python types. This way,
each for every resource that may be returned, a serializer that implements ``yapi.serializers.BaseSerializer`` must be
written.

Basically, a ``to_simple(self, obj, user=None)`` method has to be implemented.

- ``obj`` -> The object instance that will be serialized.
- ``user`` (optional) -> The user that made the request. This is useful when the instance representation varies according to the user/permissions.

Lets look at an example for serializing a user::

    from apps.api.serializers import BaseSerializer

    class UserSerializer(BaseSerializer):
        """
        Adds methods required for instance serialization.
        """
        
        def to_simple(self, obj, user=None):
            """
            Please refer to the interface documentation.
            """
            # Build response.
            simple = {
                'email': obj.email,
                'name': obj.name,
                'last_login': obj.last_login.strftime("%Y-%m-%d %H:%M:%S")
            }
        
            # Return.
            return simple

In this case, an example response could be::

    return Response(request=request,
                    data=request.auth['user'],
                    serializer=UserSerializer,
                    status=HTTPStatus.SUCCESS_200_OK)
