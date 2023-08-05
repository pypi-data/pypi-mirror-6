#
# Created on 2012-8-14
#
# @author: Para
#

from nosclient.nos import NosError
import nos
import socket
from webob import exc
import logging

LOG = logging.getLogger(__name__)


def exception_wrap(method):
    '''
    wrap function for exception handle
    handle NosError and socket.error
    :raise webob.exc.HTTPClientError: request nos error
    :raise webob.exc.HTTPRequestTimeout: request time out
    '''
    def fn(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except NosError, e:
            LOG.exception('NosError in nosclient call_nos_driver, due to: %s'
                                % str(e))
            raise exc.HTTPClientError(str(e))
        except socket.error, e:
            LOG.exception('Connection timeout occurs in nosclient '
                          'call_nos_driver, due to: %s' % str(e))
            raise exc.HTTPRequestTimeout(str(e))
    return fn


class CallNosDriver():

    '''
        this class is call nos.py api to make a connection to NOS
    '''

    def __init__(self, context, url, host, access_key, access_secret,
                 is_whitelist=False, use_nos_store_class=False):
        '''
            call NOS API
        '''
        self.url = url
        self.host = host
        self.is_whitelist = is_whitelist
        self.access_key = access_key
        self.access_secret = access_secret
        self.nos_api = nos.Nos(context, self.url, self.host, self.access_key,
                               self.access_secret, self.is_whitelist,
                                use_nos_store_class=use_nos_store_class)

    def upload_object(self, bucketName, objectKey, content):
        raise UnimplementedException()

    def get_object(self, bucketName, objectKey):
        raise UnimplementedException()

    def get_object_url(self, bucketName, objectKey, expires):
        raise UnimplementedException()

    def delete_object(self, bucketName, objectKey):
        raise UnimplementedException()

    def check_object_exist(self, bucketName, objectKey):
        raise UnimplementedException()


class UnimplementedException(Exception):
    """UnimplementedException is raised when some interface hasn't
    been implemented yet. This is an internal error that should never
    be seen by a user. Please report a bug if you see this."""
    def __str__(self):
        return "Object is Unimplemented"
