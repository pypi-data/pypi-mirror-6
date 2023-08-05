#
#Created on 2012-8-16
#
#@author: hzzhoushaoyu
#

from nosclient.call_nos_driver import CallNosDriver
from nosclient.call_nos_driver import exception_wrap


class OperateChunkImage(CallNosDriver):
    '''
    call nos to store or get chunk images
    '''

    @exception_wrap
    def upload_object(self, bucket_name, object_key, content):
        """
        return object etag
        """
        return self.nos_api.putObject(bucket_name, object_key, content,
                                      len(content))

    @exception_wrap
    def get_object(self, bucket_name, object_key):
        """
        return string content in content
        """
        return self.nos_api.getObject(bucket_name, object_key)

    @exception_wrap
    def get_object_length(self, bucket_name, object_key):
        """
        return object length
        """
        return self.nos_api.get_object_length(bucket_name, object_key)

    @exception_wrap
    def get_object_url(self, bucket_name, object_key, expires):
        return self.nos_api.getObjectURL(bucket_name, object_key, expires)

    @exception_wrap
    def delete_object(self, bucket_name, object_key):
        """
        delete an object in nos bucket
        """
        self.nos_api.deleteObject(bucket_name, object_key)

    @exception_wrap
    def check_object_exist(self, bucket_name, object_key):
        """
        return true if exist and false if not exist
        raise NosError if error cause
        """
        return self.nos_api.checkObjectExist(bucket_name, object_key)

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
    def delete_bucket(self, bucket_name):
        """
        delete bucket named bucket_name
        """
        self.nos_api.delete_bucket(bucket_name)
