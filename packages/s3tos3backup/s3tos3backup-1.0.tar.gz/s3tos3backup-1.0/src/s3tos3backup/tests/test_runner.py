from __future__ import unicode_literals, absolute_import
import os
import sys

from mock import patch

from s3tos3backup.tests.compat import unittest
from s3tos3backup.runner import main


def exception_code(cm):
    if sys.version_info < (2, 7):
        return cm.exception
    return cm.exception.code


class TestRunner(unittest.TestCase):

    def tearDown(self):
        config_file = os.path.join(os.getenv("HOME"), ".s3tos3backup")
        if os.path.exists(config_file):
            os.remove(config_file)

    def test_configure(self):
        with self.assertRaises(SystemExit) as cm:
            main(['--configure'])
        self.assertEqual(exception_code(cm), 0)

    def test_version(self):
        with self.assertRaises(SystemExit) as cm:
            main(['--version'])
        self.assertEqual(exception_code(cm), 0)

    def test_wrong_config(self):
        with self.assertRaises(SystemExit) as cm:
            main(['--config='])
        self.assertEqual(exception_code(cm), 1)

    @patch('s3tos3backup.runner.run_backup')
    def test_no_bucket(self, MockClass):
        with self.assertRaises(SystemExit) as cm:
            main([])
        self.assertEqual(exception_code(cm), 1)
        assert not MockClass.called

    @patch('s3tos3backup.runner.run_backup')
    def test_run(self, MockClass):
        main(['-b src'])
        assert MockClass.called

    @patch('s3tos3backup.runner.run_backup', side_effect=KeyError('foo'))
    def test_report(self, MockClass):
        with self.assertRaises(SystemExit) as cm:
            main(['-b src'])
        self.assertEqual(exception_code(cm), 1)
