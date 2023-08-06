import unittest
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock


class AWSTest(unittest.TestCase):
    def test_aws_init(self):
        
