__author__ = 'sleibman'

import nose
from sewing import joiner

class TestFullImage(object):
    def setup(self):
        pass

    def teardown(self):
        pass

    def test_init(self):
        fi = joiner.FullImage('/tmp', 0, 0, 1, 1)
        nose.tools.assert_true(type(fi) == joiner.FullImage)

