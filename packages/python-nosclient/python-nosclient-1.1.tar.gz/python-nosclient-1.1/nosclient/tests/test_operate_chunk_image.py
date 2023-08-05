# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import hashlib
import logging
import unittest
import webob

from nosclient.operate_chunk_image import OperateChunkImage
from nosclient.tests.fake_context import FakeContext

#if running in NOS white list IPs, set IS_RUNNING_IN_WHITELIST as True
IS_RUNNING_IN_WHITELIST = True

CONF = {
        'chunk_store_cache_enable': False,
        'chunk_store_cache': 'fake',
        'chunk_store_sos': 'nos',
        'chunk_store_sos_url': '114.113.199.19:8181',
        'chunk_store_sos_host': 'nos.netease.com',
        'chunk_store_sos_user': 'b295e375578148b1a9889de090004636',
        'chunk_store_sos_key': '04a71f1b55ae410b9deb9dbb0bdc04a4',
        'chunk_store_sos_projectid': '9f7db30969ce46b490622a8de773f088',
        'chunk_store_display_name': 'openstack-unittest',
        'chunk_store_sos_bucket': 'glance-image-test-1111-ubuntu'
        }

context = FakeContext()

TEST_BUCKET_NAME = "python-nosclient-unittest-9"
logging.disable(logging.CRITICAL)


class OperateChunkImageTestCase():
    def test_object_operation(self):
        """
        test upload,get,delete a object and check exist in correct way
        """
        OBJECT_KEY = "python-nosclient-unittest-file1"
        content = "1111111"
        ##test upload
        etag = self.nos_driver.upload_object(TEST_BUCKET_NAME, OBJECT_KEY,
                                             content)
        ##test get
        content_to_verify = self.nos_driver.get_object(TEST_BUCKET_NAME,
                                                       OBJECT_KEY)
        self.assertEqual(hashlib.md5(content).hexdigest(), etag)
        self.assertEqual(content_to_verify, content)
        ##test check
        obj_exist = self.nos_driver.check_object_exist(TEST_BUCKET_NAME,
                                                       OBJECT_KEY)
        self.assertTrue(obj_exist)
        ##test delete
        self.nos_driver.delete_object(TEST_BUCKET_NAME, OBJECT_KEY)
        obj_exist = self.nos_driver.check_object_exist(TEST_BUCKET_NAME,
                                                       OBJECT_KEY)
        self.assertFalse(obj_exist)

    def test_delete_inexistent_object(self):
        OBJECT_KEY = "delete-a-inexistent-object-test"
        self.assertRaises(webob.exc.HTTPClientError,
                          self.nos_driver.delete_object,
                          TEST_BUCKET_NAME, OBJECT_KEY)

    def test_get_inexistent_object(self):
        OBJECT_KEY = "get-a-inexistent-object-test"
        self.assertRaises(webob.exc.HTTPClientError,
                          self.nos_driver.get_object,
                          TEST_BUCKET_NAME, OBJECT_KEY)

    def test_upload_inexistent_bucket(self):
        OBJECT_KEY = "upload-a-inexistent-bucket-test"
        NOT_EXIST_BUCKET_NAME = "not-exist-bucket-test"
        self.assertRaises(webob.exc.HTTPClientError,
                          self.nos_driver.upload_object,
                          NOT_EXIST_BUCKET_NAME, OBJECT_KEY, "11111")


class TestOperateChunkImage(OperateChunkImageTestCase, unittest.TestCase):

    """
    Unit test case that establishes a mock environment within
    a testing directory (in isolation)
    """

    def setUp(self):
        self.nos_driver = OperateChunkImage(context,
                        url=CONF.get("chunk_store_sos_url"),
                        host=CONF.get("chunk_store_sos_host"),
                        access_key=CONF.get("chunk_store_sos_user"),
                        access_secret=CONF.get("chunk_store_sos_key"),
                        is_whitelist=False
                        )
        if not self.nos_driver.check_bucket_exist(TEST_BUCKET_NAME):
            self.nos_driver.create_bucket(TEST_BUCKET_NAME)

    def tearDown(self):
        self.nos_driver.delete_bucket(TEST_BUCKET_NAME)


class TestWhiteListOperateChunkImage(OperateChunkImageTestCase,
                                     unittest.TestCase):

    """
    Unit test case that establishes a mock environment within
    a testing directory (in isolation)
    """

    def setUp(self):
        if not IS_RUNNING_IN_WHITELIST:
            self.skipTest("NOT running in NOS white list IPs")
            return
        self.nos_driver = OperateChunkImage(context,
                           url=CONF.get("chunk_store_sos_url"),
                           host=CONF.get("chunk_store_sos_host"),
                           access_key=CONF.get("chunk_store_display_name"),
                           access_secret=CONF.get("chunk_store_sos_projectid"),
                           is_whitelist=True
                           )
        if not self.nos_driver.check_bucket_exist(TEST_BUCKET_NAME):
            self.nos_driver.create_bucket(TEST_BUCKET_NAME)

    def tearDown(self):
        self.nos_driver.delete_bucket(TEST_BUCKET_NAME)
