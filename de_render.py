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

    def test_print_with_debugrenderer(self):
        scb = self._scb

        lines = scb.split('\n')
        linepasser = dobu.LinePasser(lines)
        pageparser = dobu.PageParser(linepasser)
        page = pageparser.parse()

        renderer = dobu.DebugRenderer(page)
        lines = renderer.render()

        print('[Debug Render]')
        for line in lines:
            print(line)

    def test_print_with_htmlrenderer(self):
        scb = self._scb

        lines = scb.split('\n')
        linepasser = dobu.LinePasser(lines)
        pageparser = dobu.PageParser(linepasser)
        page = pageparser.parse()
        page.name = 'scb page sample'

        renderer = dobu.HTMLRenderer(page)
        lines = renderer.render()

        print('[HTML Render]')
        for line in lines:
            print(line)

if __name__ == '__main__':
    unittest.main()
