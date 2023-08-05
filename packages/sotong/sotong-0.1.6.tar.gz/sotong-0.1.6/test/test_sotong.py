import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import sotong


class TestSotong(unittest.TestCase):

    def test_sotong(self):
        self.assertTrue(sotong.sotong.Sotong)

        s = sotong.sotong.Sotong()

        @s.watch('./')
        def project_file_modified(event):
            pass

        @s.interval(10)
        def interval():
            pass

        @s.daily(10, 34, 56)
        def daily_task():
            pass

    def test_import(self):
        from sotong import api, log, event

if __name__ == '__main__':
    unittest.main()
