# encoding: utf-8
import unittest

import dobu

class TestLinePasser(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_0(self):
        lines = []
        lp = dobu.LinePasser(lines)

        with self.assertRaises(RuntimeError):
            lp.next

    def test_1(self):
        lines = ['aaa']
        lp = dobu.LinePasser(lines)

        self.assertEqual('aaa', lp.next)
        with self.assertRaises(RuntimeError):
            lp.next

    def test_n(self):
        lines = ['aaa','111','','ディーディーディー']
        lp = dobu.LinePasser(lines)

        self.assertEqual('aaa', lp.next)
        self.assertEqual('111', lp.next)
        self.assertEqual('', lp.next)
        self.assertEqual('ディーディーディー', lp.next)
        with self.assertRaises(RuntimeError):
            lp.next

if __name__ == '__main__':
    unittest.main()
