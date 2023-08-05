import logging
import types
from django.db.models.query import QuerySet
from django.http.response import HttpResponse

from encoders import JSONEncoder
from pagination import Paginator

# Instantiate logger.
logger = logging.getLogger(__name__)


class HTTPStatus:
    """
    Response status codes.
    """
    
    # 1xx Informational.
    INFORMATIONAL_100_CONTINUE = 100
    INFORMATIONAL_101_SWITCHING_PROTOCOLS = 101
    
    # 2xx Success.
    SUCCESS_200_OK = 200
    SUCCESS_201_CREATED = 201
    SUCCESS_202_ACCEPTED = 202
    SUCCESS_203_NON_AUTHORITATIVE_INFORMATION = 203
    SUCCESS_204_NO_CONTENT = 204
    SUCCESS_205_RESET_CONTENT = 205
    SUCCESS_206_PARTIAL_CONTENT = 206
    
    # 3xx Redirection.
    REDIRECTION_300_MULTIPLE_CHOICES = 300
    REDIRECTION_301_MOVED_PERMANENTLY = 301
    REDIRECTION_302_FOUND = 302
    REDIRECTION_303_SEE_OTHER = 303
    REDIRECTION_304_NOT_MODIFIED = 304
    REDIRECTION_305_USE_PROXY = 305
    REDIRECTION_306_RESERVED = 306
    REDIRECTION_307_TEMPORARY_REDIRECT = 307
    
    # 4xx Client Error.
    CLIENT_ERROR_400_BAD_REQUEST = 400
    CLIENT_ERROR_401_UNAUTHORIZED = 401
    CLIENT_ERROR_402_PAYMENT_REQUIRED = 402
    CLIENT_ERROR_403_FORBIDDEN = 403
    CLIENT_ERROR_404_NOT_FOUND = 404
    CLIENT_ERROR_405_METHOD_NOT_ALLOWED = 405
    CLIENT_ERROR_406_NOT_ACCEPTABLE = 406
    CLIENT_ERROR_407_PROXY_AUTHENTICATION_REQUIRED = 407
    CLIENT_ERROR_408_REQUEST_TIMEOUT = 408
    CLIENT_ERROR_409_CONFLICT = 409
    CLIENT_ERROR_410_GONE = 410
    CLIENT_ERROR_411_LENGTH_REQUIRED = 411
    CLIENT_ERROR_412_PRECONDITION_FAILED = 412
    CLIENT_ERROR_413_REQUEST_ENTITY_TOO_LARGE = 413
    CLIENT_ERROR_414_REQUEST_URI_TOO_LONG = 414
    CLIENT_ERROR_415_UNSUPPORTED_MEDIA_TYPE = 415
    CLIENT_ERROR_416_REQUESTED_RANGE_NOT_SATISFIABLE = 416
    CLIENT_ERROR_417_EXPECTATION_FAILED = 417
    CLIENT_ERROR_428_PRECONDITION_REQUIRED = 428
    CLIENT_ERROR_429_TOO_MANY_REQUESTS = 429
    CLIENT_ERROR_431_REQUEST_HEADER_FIELDS_TOO_LARGE = 431
    
    # 5xx Server Error.
    SERVER_ERROR_500_INTERNAL_SERVER_ERROR = 500
    SERVER_ERROR_501_NOT_IMPLEMENTED = 501
    SERVER_ERROR_502_BAD_GATEWAY = 502
    SERVER_ERROR_503_SERVICE_UNAVAILABLE = 503
    SERVER_ERROR_504_GATEWAY_TIMEOUT = 504
    SERVER_ERROR_505_HTTP_VERSION_NOT_SUPPORTED = 505
    SERVER_ERROR_511_NETWORK_AUTHENTICATION_REQUIRED = 511


class Response(HttpResponse):
    """
    Builds the response.
    """
    
    def __init__(self, request, data, serializer, status, pagination=True, filters=None):
        """
        Constructor.
        
        Args:
            request - The request that originated this response.
            data - The raw response data.
            serializer - The serializer that will be used to serialize the data.
            status - The HTTP status code of the response.
            pagination (optional) - When the response data is a QuerySet, this states if the response should be
                                    paginated or not. Default is True.
            filters (optional) - When the response data is a QuerySet and it was filtered by given parameters,
                                 they are provided in this field.
        """
        
        # Encoder (default: JSON)
        encoder = JSONEncoder()
        
        # If request was authenticated, fetch respective user.
        if request.auth:
            user = request.auth['user']
        else:
            user = None
            
        # Data is a QuerySet and pagination was requested.
        if isinstance(data, QuerySet) and pagination == True:
            response = Paginator(serializer).get_results(request, data, user, filters)
            
        # Data is a Python dict, no need to serialize!
        elif isinstance(data, types.DictType):
            response = data
        
        # Serialize data.
        else:
            response = serializer().serialize(data, user)
        
        # Build HTTP response.
        super(Response, self).__init__(content=encoder.encode(response),
                                       status=status,
                                       mimetype=encoder.get_mimetype())