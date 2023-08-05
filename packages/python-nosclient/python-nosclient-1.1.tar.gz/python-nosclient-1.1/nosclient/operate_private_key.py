#
# Created on 2012-8-16
#
# @author: Para
#
from nosclient.call_nos_driver import CallNosDriver
from nosclient.call_nos_driver import exception_wrap


class OperatePrivateKey(CallNosDriver):
    '''
        Call super __init__(self, url, host, accessKey, accessSecret)
    '''

    @exception_wrap
    def upload_object(self, bucketName, objectKey, content):
        '''
            Upload object
        '''
        self.nos_api.putObject(bucketName, objectKey, content, len(content))

    @exception_wrap
    def upload_private_key(self, bucketName, objectKey, content,
                           expiresTime, use_domain=True):
        '''
            Upload private key.
            @return: this private key url
            @state error exception: raise webob.exc.HTTPClientError
            @timeout exception: raise webob.exc.HTTPRequestTimeout
        '''
        self.upload_object(bucketName, objectKey, content)
        return self.get_object_url(bucketName, objectKey,
                                   expiresTime, use_domain)

    @exception_wrap
    def get_object(self, bucketName, objectKey):
        '''
            Download object
            @return: this object content
        '''
        return self.nos_api.getObject(bucketName, objectKey)

    @exception_wrap
    def get_object_url(self, bucketName, objectKey, expires, use_domain=True):
        '''
            Get object url
            @return: this object url
        '''
        return 'http://' + self.nos_api.getObjectURL(bucketName, objectKey,
                                                     expires, use_domain)

    @exception_wrap
    def delete_private_key(self, bucketName, objectKey):
        '''
            Delete object
        '''
        self.nos_api.deleteObject(bucketName, objectKey)

    @exception_wrap
    def check_bucket_exist(self, bucket_name):
        """
        check whether bucket exists
        """
        return self.nos_api.check_bucket_exist(bucket_name)

    @exception_wrap
    def create_bucket(self, bucket_name, location_constraint="HZ",
                      object_deduplicate="False"):
        """
        create a bucket with bucket name, return nos response content
        """
        return self.nos_api.create_bucket(bucket_name, location_constraint,
                                          object_deduplicate)

    @exception_wrap
    def check_object_exist(self, bucket_name, object_key):
        """
        return true if exist and false if not exist
        raise NosError if error cause
        """
        return self.nos_api.checkObjectExist(bucket_name, object_key)
