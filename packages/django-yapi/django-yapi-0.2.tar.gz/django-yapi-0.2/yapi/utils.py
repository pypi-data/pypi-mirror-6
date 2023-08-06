import datetime
import hashlib
import hmac
import logging
import random
import uuid

# Instantiate logger.
logger = logging.getLogger(__name__)


def generate_key(salt):
    """
    Generates a new random key.
    """
    key = hashlib.new('ripemd160')
    key.update(str(salt) + str(random.getrandbits(256)) + str(datetime.datetime.now()) + hmac.new(uuid.uuid4().bytes, digestmod=hashlib.sha1).hexdigest())
    return key.hexdigest() + hex(int(datetime.datetime.now().strftime('%s')))[2:]