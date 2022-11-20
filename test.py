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

class TestIndent(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_0(self):
        s = ''

        e = 0
        a = dobu.Indent.get_depth(s)
        self.assertEqual(e, a)

    def test_1_spaceonly(self):
        s = ' '

        e = 1
        a = dobu.Indent.get_depth(s)
        self.assertEqual(e, a)

    def test_n_spaceonly(self):
        s = '    '

        e = 4
        a = dobu.Indent.get_depth(s)
        self.assertEqual(e, a)

    def test_1_mix(self):
        s = ' line'

        e = 1
        a = dobu.Indent.get_depth(s)
        self.assertEqual(e, a)

    def test_n_mix(self):
        s = '    line'

        e = 4
        a = dobu.Indent.get_depth(s)
        self.assertEqual(e, a)

    def test_1_noindent(self):
        s = 'a'

        e = 0
        a = dobu.Indent.get_depth(s)
        self.assertEqual(e, a)

    def test_n_noindent(self):
        s = 'line'

        e = 0
        a = dobu.Indent.get_depth(s)
        self.assertEqual(e, a)

if __name__ == '__main__':
    unittest.main()
