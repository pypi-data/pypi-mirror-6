from __future__ import unicode_literals

import os
import unittest
from bussiness import _GLOBAL, ToolSet


class ToolSetTest(unittest.TestCase):

    def setUp(self):
        _GLOBAL.DIR_PATH = os.path.join(os.getcwd(), '.doctpl')
        self.toolset = ToolSet()

    def test_dir_abs_path(self):
        self.assertEqual(
            self.toolset.dir_abs_path,
            os.path.join(os.getcwd(), '.doctpl'),
        )

    def test_avaliable_templates(self):
        self.assertEqual(
            set(self.toolset.avaliable_templates),
            {'template_a', 'template_b'},
        )

    def test_copy_for_not_existed_file(self):
        target_not_exist = os.path.join(_GLOBAL.DIR_PATH,
                                        'testdir/not_exist')
        if os.path.exists(target_not_exist):
            os.remove(target_not_exist)

        path = self.toolset.make_copy('./.doctpl/testdir/not_exist',
                                      'template_a')

        self.assertEqual(path, target_not_exist)
        self.assertEqual(
            open(path, 'r').read(),
            "template_a's content.\n",
        )

    def test_copy_for_existed_file(self):
        target_exist = os.path.join(_GLOBAL.DIR_PATH, 'testdir/exist')
        open(target_exist, 'w').close()

        with self.assertRaises(Exception) as context:
            self.toolset.make_copy('./.doctpl/testdir/exist', 'template_a')

        self.assertIn(
            'Already Existed',
            ''.join(context.exception.args),
        )

    def test_copy_no_such_template(self):
        with self.assertRaises(Exception) as context:
            self.toolset.make_copy('./.doctpl/testdir/exist', 'template_c')

        self.assertIn(
            'No Such Template',
            ''.join(context.exception.args),
        )


if __name__ == '__main__':
    unittest.main()
