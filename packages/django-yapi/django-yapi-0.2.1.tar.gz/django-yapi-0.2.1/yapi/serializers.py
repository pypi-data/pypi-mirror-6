import logging
from django.db.models.query import QuerySet
from django.core.paginator import Page

# Instantiate logger.
logger = logging.getLogger(__name__)


class BaseSerializer(object):
    """
    This class should be extended by all response data serializers.
    """
      
    def to_simple(self, obj, user=None):
        """
        This brings complex Python data structures down to native types.
        """
        raise NotImplementedError()
        
    def serialize(self, data, user=None):
        """
        Serializes the given data.
        
        Args:
            data - The data to be serialized (Object instance or QuerySet/Page array)
            user - (optional) The user requesting the data that may affect its representation,
                 given the permissions.
        
        Returns:
            If the data is an Object, return it in its native Python types. If it is a QuerySet, return
            an array containing all the Objects in their native Python types.
        """
        
        # Data is a QuerySet.
        if isinstance(data, QuerySet) or isinstance(data, Page):
            return [self.to_simple(obj, user) for obj in data]
        
        # Data is an Object instance.
        else:
            return self.to_simple(data, user)