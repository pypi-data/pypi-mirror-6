import json
import logging

# Instantiate logger.
logger = logging.getLogger(__name__)


class BaseEncoder(object):
    """
    This class should be extended by all serialized data encoders.
    """
    
    def encode(self, data):
        """
        Encodes data from Python native types to the given format.
        """
        raise NotImplementedError()
    
    def decode(self, data):
        """
        Decodes data from the given format into Python native types.
        """
        raise NotImplementedError()
    
    def get_mimetype(self):
        """
        Returns the encoder's mimetype.
        """
        raise NotImplementedError()
        
        
class JSONEncoder(BaseEncoder):
    """
    Encoder implementation for the JSON data format.
    """
    
    def encode(self, data):
        """
        Returns the JSON formatted data.
        """
        return json.dumps(data)
    
    def get_mimetype(self):
        """
        Returns the JSON's mimetype.
        """
        return 'application/json'