# encoding: utf-8
import unittest

import dobu

class TestRenderer(unittest.TestCase):
    def setUp(self):
        self._scb = """scb page sample
line
 line1
 line1
  line2
   やっぱり[趣味]は[プログラミング]に限りますな。`print(f"hello world! {array[i]=}");` とか `import os` みたいな[リテラル記法]はよく使いますよね
  url系も使いましょう
   [前にsta https://scrapbox.io/sta/]
   [https://scrapbox.io/sta/ 後ろにsta]
   [https://scrapbox.io/sta/ 後ろに スペース区切りで sta]
   [前に スペース区切りで sta https://scrapbox.io/sta/]
   [URLなしで スペース区切りの リンクは ただのページ内リンク]
  引用忘れてましたね
   >引用
   >引用の中で`リテラル`や[link]
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

    def tearDown(self):
        pass

    @staticmethod
    def to_file(filename, lines):
        return dobu.list2file(filename, lines)

    def test_print_with_debugrenderer(self):
        scb = self._scb

        lines = scb.split('\n')
        linepasser = dobu.LinePasser(lines)
        pageparser = dobu.PageParser(linepasser)
        page = pageparser.parse()

        renderer = dobu.DebugRenderer(page)
        lines = renderer.render()

        self.to_file('1_debug_debugout.txt', lines)

    def test_print_with_htmlrenderer(self):
        scb = self._scb

        lines = scb.split('\n')
        linepasser = dobu.LinePasser(lines)
        pageparser = dobu.PageParser(linepasser)
        page = pageparser.parse()
        page.name = 'scb page sample'

        renderer = dobu.HTMLRenderer(page)
        lines = renderer.render()

        self.to_file('2_html_debugout.html', lines)

if __name__ == '__main__':
    unittest.main()