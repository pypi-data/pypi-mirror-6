import logging
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.core.paginator import Paginator as DjangoPaginator

# Instantiate logger.
logger = logging.getLogger(__name__)


class Paginator(object):
    """
    Paginate results.
    """
    
    def __init__(self, serializer):
        """
        Constructor.
        """
        self.serializer = serializer() 
    
    def get_results(self, request, data, user=None, filters=None):
        """
        Please refer to the interface documentation.
        """
        # Check if items per page value was provided (default is 30)
        try:
            per_page = int(request.GET.get('per_page', 30))
            
            # Has to be bigger than 0!
            # TODO: Should raise exception?
            if per_page <= 0:
                per_page = 30
        # If invalid value, fallback to 30.
        # TODO: Should raise exception?
        except ValueError:
            per_page = 30
        
        # Fetch X items and paginate.
        paginator = DjangoPaginator(data, per_page)
        try:
            page = request.GET.get('page')
            result_page = paginator.page(page)
            page = int(page)
        # If page is not an integer, deliver first page.
        except PageNotAnInteger:
            page = 1
            result_page = paginator.page(page)
        # If page is out of range (e.g. 9999), deliver last page of results.
        except EmptyPage:
            page = paginator.num_pages
            result_page = paginator.page(page)
        
        # Build response.
        results = {
            'collection': self.serializer.serialize(result_page, user),
            'filters': {},
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': paginator.num_pages,
                'total_items': len(data)
            }
        }
        
        # If the QuerySet was filtered and respective filters are provided, append them to response.
        if filters:
            results['filters'] = filters
        
        # Return.
        return results