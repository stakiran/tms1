# encoding: utf-8
import unittest

import dobu

class TestIsHttp(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test(self):
        a = dobu.is_http('http://www.google.co.jp')
        self.assertTrue(a)
        a = dobu.is_http('http://www.google.co.jp ')
        self.assertTrue(a)
        a = dobu.is_http('ttp://www.google.co.jp')
        self.assertFalse(a)
        a = dobu.is_http('')
        self.assertFalse(a)
        # そんな厳密な判定はしてないのでプロトコル部分が合えば、もう ok になってる
        a = dobu.is_http('http://')
        self.assertTrue(a)

        a = dobu.is_https('https://www.google.co.jp')
        self.assertTrue(a)
        a = dobu.is_http('https://www.google.co.jp')
        self.assertFalse(a)

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

    def xtest_onepass(self):
        line = ' やっぱり[趣味]は[プログラミング]に限りますな。`print(f"hello world! {array[i]=}");` とか `import os` みたいな[リテラル記法]はよく使いますよね'
        lineobj = dobu.Line(line)

        a = lineobj._inline_elements_at_literal
        self.assertEqual(' やっぱり[趣味]は[プログラミング]に限りますな。', a[0].raw)
        self.assertEqual('print(f"hello world! {array[i]=}");', a[1].text)
        self.assertEqual(' とか ', a[2].raw)
        self.assertEqual('import os', a[3].text)
        self.assertEqual(' みたいな[リテラル記法]はよく使いますよね', a[4].raw)

        # 今は literal=textがある、link=uriがある、というテキトーな判定になっている（実装からしてそう合わせている）
        # 暫定でしかない
        # どこかでちゃんとした判定（isinstanceとか）+中身の判定も切り替える（linkの場合、textとuriが分かれてるとか）必要

        a = lineobj._inline_elements_at_link
        self.assertEqual(' やっぱり', a[0].raw)
        self.assertEqual('趣味', a[1].uri)
        self.assertEqual('は', a[2].raw)
        self.assertEqual('プログラミング', a[3].uri)
        self.assertEqual('に限りますな。', a[4].raw)
        self.assertEqual('print(f"hello world! {array[i]=}");', a[5].text)
        self.assertEqual(' とか ', a[6].raw)
        self.assertEqual('import os', a[7].text)
        self.assertEqual(' みたいな', a[8].raw)
        self.assertEqual('リテラル記法', a[9].uri)
        self.assertEqual('はよく使いますよね', a[10].raw)

class TestLink(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_onepass(self):
        line = ' やっぱり[趣味]は[プログラミング]に限りますな。`print(f"hello world! {array[i]=}");` とか `import os` みたいな[リテラル記法]はよく使いますよね'
        lineobj = dobu.Link(line)

if __name__ == '__main__':
    unittest.main()
