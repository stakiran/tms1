# encoding: utf-8
import unittest

import dobu

class TestStack(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_0(self):
        stack = dobu.Stack([])

        with self.assertRaises(IndexError):
            stack.pop()

        stack.push('a')

        e = 'a'
        a = stack.pop()
        self.assertEqual(e, a)

        with self.assertRaises(IndexError):
            stack.pop()

    def test_1(self):
        stack = dobu.Stack(['1'])

        e = '1'
        a = stack.pop()
        self.assertEqual(e, a)

    def test_2(self):
        stack = dobu.Stack(['1', 'a'])

        e = 'a'
        a = stack.pop()
        self.assertEqual(e, a)

        e = '1'
        a = stack.pop()
        self.assertEqual(e, a)

    def test_peek(self):
        stack = dobu.Stack(['a'])
        e_elm = 'a'
        a_elm, a_res = stack.peek()
        self.assertEqual(e_elm, a_elm)
        self.assertFalse(a_res)

        stack.pop()
        _, a_res = stack.peek()
        self.assertTrue(a_res)

        stack.push('123')
        stack.push('789')
        stack.push('456')
        e_elm = '456'
        a_elm, a_res = stack.peek()
        self.assertEqual(e_elm, a_elm)
        self.assertFalse(a_res)

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

class TestPage(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_onepass(self):
        scb = """scb page sample
line
 line1
 line1
  line2
block
 code:codeblock1
  aaa
  あいうえお
 :c
 line1
 code:codeblock2.scb
  not line1
   not line2
    not line3
 :c
  line2
code:rootcodeblock
 not line1
:c"""

        lines = scb.split('\n')
        linepasser = dobu.LinePasser(lines)

        pageparser = dobu.PageParser(linepasser)

        page = pageparser.parse()
        nodes = page.nodes

        e = 11
        a = len(nodes)
        self.assertEqual(e, a)

        self.assertTrue(nodes[0].content.is_line())
        self.assertTrue(nodes[1].content.is_line())
        self.assertTrue(nodes[2].content.is_line())
        self.assertTrue(nodes[3].content.is_line())
        self.assertTrue(nodes[4].content.is_line())
        self.assertTrue(nodes[5].content.is_line())
        self.assertTrue(nodes[6].content.is_codeblock())
        self.assertTrue(nodes[7].content.is_line())
        self.assertTrue(nodes[8].content.is_codeblock())
        self.assertTrue(nodes[9].content.is_line())
        self.assertTrue(nodes[10].content.is_codeblock())

class TestLine(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_onepass(self):
        line = ' やっぱり[趣味]は[プログラミング]に限りますな。`print(f"hello world! {array[i]=}");` とか `import os` みたいな[リテラル記法]はよく使いますよね'
        lineobj = dobu.Line(line)

        print('')
        for inlineelement in lineobj.inline_elements:
            print(f'|{inlineelement.raw}|')

if __name__ == '__main__':
    unittest.main()
