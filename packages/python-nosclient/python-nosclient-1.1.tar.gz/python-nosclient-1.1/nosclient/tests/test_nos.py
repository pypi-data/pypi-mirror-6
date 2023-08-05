import unittest
from nosclient import nos


class NosTestCase(unittest.TestCase):

    def test_get_auth_head_with_none_object_key(self):
        nn = nos.Nos(None, 'fake.nos.com', 'fakehost',
                     'fake-access-key', 'fake-secret-key')
        nn._get_auth_head('testbucket', None, 'fakeDate', 'GET',
                          'application/json', 'fakemd5')
        # no assert, just make sure no exception raised.

    def test_get_auth_head_with_none_bucket_name(self):
        nn = nos.Nos(None, 'fake.nos.com', 'fakehost',
                     'fake-access-key', 'fake-secret-key')
        nn._get_auth_head(None, None, 'fakeDate', 'GET',
                          'application/json', 'fakemd5')
        # no assert, just make sure no exception raised.
