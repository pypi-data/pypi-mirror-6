# -*- coding: utf-8 -*-

import unittest
import mock
import os.path
from rt.zestreleaser.pyflakes.pyflakes_checker import check

dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')

data = {
        'original_version': '0.1',
        'name': 'foo.bar',
        'workingdir': dir,
        'history_file': 'docs/HISTORY.txt',
        'history_header': '%(new_version)s (%(today)s)',
        'history_lines': ['Changelog', '=========', '',
                          '0.1 (2014-04-15)', '------------------', '',
                          '- Nothing changed yet.', ''],
        'new_version': '0.1.1', 'commit_msg': 'Preparing release %(new_version)s',
        'today': '2014-04-15',
    }


class PyflakesCheckTest(unittest.TestCase):

    @mock.patch('zest.releaser.utils.ask')
    @mock.patch('rt.zestreleaser.pyflakes.pyflakes_checker.find')
    def test_nop_when_no_python_found(self, find, ask):
        find.return_value = []
        check(data)
        self.assertFalse(ask.called)

    @mock.patch('zest.releaser.utils.ask')
    def test_ask_for_seing_output(self, ask):
        check(data)
        self.assertTrue(ask.called)

    @mock.patch('zest.releaser.utils.ask')
    @mock.patch('StringIO.StringIO.getvalue')
    def test_skip_if_not_warns_found(self, getvalue, ask):
        getvalue.return_value = ''
        check(data)
        self.assertFalse(ask.called)

    @mock.patch('zest.releaser.utils.ask')
    def test_ask_confirmation_after_warns(self, ask):
        ask.return_value = True
        check(data)
        ask.assert_called_with('Do you want to continue anyway?', default=False)


if __name__ == "__main__":
    unittest.main()
