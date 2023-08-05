from __future__ import unicode_literals, absolute_import
import boto

from moto import mock_s3
from mock import patch

from s3tos3backup.tests.compat import unittest
from s3tos3backup.copy import copy_bucket
from s3tos3backup.remove import remove_old_buckets
from s3tos3backup.backup import run_backup


class TestOperations(unittest.TestCase):

    def _create_defaults(self, bucket_name='src'):
        self.connection = boto.connect_s3()
        self.connection.create_bucket(bucket_name)
        bucket = self.connection.get_bucket(bucket_name)
        for x in xrange(2):
            key = bucket.new_key('foo-%d' % x)
            key.set_contents_from_string(x)
            key.set_acl('public-read')
            key.close()

    @mock_s3
    def test_copy(self):
        self._create_defaults()
        copy_bucket(self.connection, 'src', 'src-copy')
        keys = [k.name for k in self.connection.get_bucket('src').get_all_keys()]
        self.assertEqual(keys, ['foo-0', 'foo-1'])

        # test 2nd copy errors
        copy_bucket(self.connection, 'src', 'src-copy')
        keys = [k.name for k in self.connection.get_bucket('src').get_all_keys()]
        self.assertEqual(keys, ['foo-0', 'foo-1'])

        # test not implemented copy to path
        self.assertRaises(ValueError, copy_bucket, connection=self.connection, src='src', dst='src-copy/foo')

    @mock_s3
    def test_remove(self):
        self._create_defaults('src-backup-2012-01-01')
        remove_old_buckets(self.connection, 'src')

        buckets = [b.name for b in self.connection.get_all_buckets()]
        self.assertEqual(buckets, [])

    @patch('s3tos3backup.backup.copy_bucket')
    @patch('s3tos3backup.backup.remove_old_buckets')
    @mock_s3
    def test_backup_all(self, MockClass1, MockClass2):
        run_backup('src', True, True)
        assert MockClass1.called
        assert MockClass2.called

    @patch('s3tos3backup.backup.copy_bucket')
    @patch('s3tos3backup.backup.remove_old_buckets')
    @mock_s3
    def test_backup_all_with_credendials(self, MockClass1, MockClass2):
        run_backup('src', True, True, 'foo', 'bar')
        assert MockClass1.called
        assert MockClass2.called
