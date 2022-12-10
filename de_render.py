# encoding: utf-8
import os
import sys

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
  リテラル
   `リテラル`
   not-lite`lite`not-lite`lite``lite`not-lite
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
        renderer.use_line_flattening()
        lines = renderer.render()

        self.to_file('2_html_debugout.html', lines)

class TestConverter(unittest.TestCase):
    def setUp(self):
        self.MYFULLPATH = os.path.abspath(sys.argv[0])
        self.MYDIR = os.path.dirname(self.MYFULLPATH)

    def tearDown(self):
        pass

    def test_onepass(self):
        sourcedir = os.path.join(self.MYDIR, 'scb')
        outputdir = os.path.join(self.MYDIR, 'html_debugout')

        try:
            os.mkdir(outputdir)
        except FileExistsError:
            pass

        converter = dobu.Converter(output_directory=outputdir)
        filepathes = converter.directory2filepathes(sourcedir)

        print(f'sourcedir: {sourcedir}')
        print(f'outputdir: {outputdir}')
        print(f'the count of sourcefiles is: {len(filepathes)}')

        testee_filepath = filepathes[0]
        page = converter.filepath2page(testee_filepath)
        converter.page2file(page)

if __name__ == '__main__':
    unittest.main()
