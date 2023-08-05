# author: hzguanqiang@corp.netease.com
#

""" fake Context class for tests """


class FakeContext(object):

    def __init__(self):
        self.unified_log_id = 'fake_uuid'
        self.unified_log_seq = '1.1'

    def to_dict(self):
        return {'unified_log_id': None,
                'unified_log_seq': None}
