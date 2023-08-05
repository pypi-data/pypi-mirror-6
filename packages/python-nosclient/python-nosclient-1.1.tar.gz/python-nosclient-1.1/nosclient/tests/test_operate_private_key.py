#
# Created on 2012-8-20
#
# @author: Para
#
from webob import exc
import logging
import time
import unittest

from nosclient.operate_chunk_image import OperateChunkImage
from nosclient.operate_private_key import OperatePrivateKey
from nosclient.tests.fake_context import FakeContext


CONF = {
        'test_nos_url': '114.113.199.19:8181',
        'test_nos_host': 'nos.netease.com',
        'test_nos_accessKey': 'b295e375578148b1a9889de090004636',
        'test_nos_accessSecret': '04a71f1b55ae410b9deb9dbb0bdc04a4',
        'test_nos_bucket': 'test-openstack-bucket'
        }

context = FakeContext()

logging.disable(logging.CRITICAL)


class OperatePrivateKeyTest(unittest.TestCase):

    """
    Unit test case that establishes a mock environment within
    a testing directory (in isolation)
    """

    def setUp(self):
        self.nos_private_key = OperatePrivateKey(context,
                            url=CONF.get("test_nos_url"),
                            host=CONF.get("test_nos_host"),
                            access_key=CONF.get("test_nos_accessKey"),
                            access_secret=CONF.get("test_nos_accessSecret"))
        self.nos_help = OperateChunkImage(context,
                           url=CONF.get("test_nos_url"),
                           host=CONF.get("test_nos_host"),
                           access_key=CONF.get("test_nos_accessKey"),
                           access_secret=CONF.get("test_nos_accessSecret"))
        if not self.nos_help.check_bucket_exist(CONF.get("test_nos_bucket")):
            self.nos_help.create_bucket(CONF.get("test_nos_bucket"))

    def tearDown(self):
        self.nos_help.delete_bucket(CONF.get("test_nos_bucket"))

    def test_object_operation(self):
        """
            test upload, get
        """
        BUCKET_NAME = CONF.get("test_nos_bucket")
        OBJECT_KEY = "test.private"
        content = "123456"
        expiresTime = 86400
        EXPIRES = long(time.time() + expiresTime)

        #test upload
        upload_return = self.nos_private_key.upload_private_key(BUCKET_NAME,
                                                                OBJECT_KEY,
                                                                content,
                                                                EXPIRES)

        #test get
        object_content = self.nos_private_key.get_object(BUCKET_NAME,
                                                         OBJECT_KEY)
        self.assertEqual(object_content, content)

        #test get url
        object_url = self.nos_private_key.get_object_url(BUCKET_NAME,
                                                         OBJECT_KEY,
                                                         EXPIRES)
        self.assertEqual(upload_return, object_url)

        self.nos_help.delete_object(BUCKET_NAME, OBJECT_KEY)

    def test_get_inexistent_object(self):
        BUCKET_NAME = CONF.get("test_nos_bucket")
        OBJECT_KEY = "test1.private"
        self.assertRaises(exc.HTTPClientError,
                          self.nos_private_key.get_object,
                          BUCKET_NAME, OBJECT_KEY)
