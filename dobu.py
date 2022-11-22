# encoding: utf-8

from xml.sax.handler import property_declaration_handler


def parse_arguments():
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument('-i', '--input-path', default=None)
    parser.add_argument('--input-from-cd', default=False, action='store_true')

    parser.add_argument('--to-dobu', default=True, action='store_true')
    parser.add_argument('--to-html', default=False, action='store_true')

    parser.add_argument('--not-stdout-but-file', default=False, action='store_true')

    parser.add_argument('--html-template', default=None)

    args = parser.parse_args()
    return args

def file2list(filepath):
    ret = []
    with open(filepath, encoding='utf8', mode='r') as f:
        ret = [line.rstrip('\n') for line in f.readlines()]
    return ret

def list2file(filepath, ls):
    with open(filepath, encoding='utf8', mode='w') as f:
        f.writelines(['{:}\n'.format(line) for line in ls] )

class Stack:
    def __init__(self, ls):
        self._contents = ls

    def pop(self):
        return self._contents.pop()

    def push(self, element):
        self._contents.append(element)

    def peek(self):
        bottompos = len(self._contents) - 1

        is_empty = bottompos==-1

        element = None
        if not is_empty:
            element = self._contents[bottompos]

        return element, is_empty

class Judgement:
    @staticmethod
    def is_codeblock_start(line_without_indent):
        line = line_without_indent

        ok_prefix = line.startswith('code:')
        is_there_caption = len(line) > len('code:')

        if not ok_prefix:
            return False
        if not is_there_caption:
            return False
        return True

    @staticmethod
    def is_codeblock_end(line_without_indent):
        line = line_without_indent

        ok_terminate = line.startswith(':c')
        ok_terminate_only = len(line) == len(':c')

        if not ok_terminate:
            return False
        if not ok_terminate_only:
            return False
        return True

class Indent:
    @staticmethod
    def get_depth(s):
        depth = 0
        while True:
            is_outofindex = depth >= len(s)
            if is_outofindex:
                break
            c = s[depth]
            if c == ' ':
                depth += 1
                continue
            break
        return depth

    @staticmethod
    def trim(s):
        return s.strip(' ')

class LinePasser:
    def __init__(self, lines):
        self._lines = lines
        self._idx = 0

    def already_empty(self):
        lastidx = len(self._lines)
        if self._idx >= lastidx:
            return True
        return False

    @property
    def next(self):
        if self.already_empty():
            raise RuntimeError('LinePasser says "already empty."')
        line = self._lines[self._idx]
        self._idx += 1
        return line

class PageParser:
    def __init__(self, linepasser):
        self.set_linepasser(linepasser)

    def set_linepasser(self, linepasser):
        self._lp = linepasser

    def parse(self):
        page = Page()
        nodefactory = NodeFactory(self._lp)
        while True:
            if nodefactory.already_empty():
                break
            node = nodefactory.get_next_node()
            page.add_node(node)
        return page

class NodeFactory:
    def __init__(self, linepasser):
        self._lp = linepasser

    def already_empty(self):
        return self._lp.already_empty()

    def get_next_node(self):
        lp = self._lp
        line = lp.next

        indent = Indent.get_depth(line)
        line_without_indent = Indent.trim(line)

        node = Node()
        node.set_indent_depth(indent)

        nodecontent = self.proceed_as_something(line_without_indent, lp)
        node.set_content(nodecontent)

        return node

    def proceed_as_something(self, line_without_indent, lp):
        if Judgement.is_codeblock_start(line_without_indent):
            return self.proceeded_as_codeblock(line_without_indent, lp)
        return self.proceeded_as_line(line_without_indent)

    def proceeded_as_codeblock(self, line_without_indent, lp):
        _, caption = line_without_indent.split(':', maxsplit=1)

        codelines = []
        while True:
            line = lp.next
            line_without_indent = Indent.trim(line)
            if Judgement.is_codeblock_end(line_without_indent):
                break
            codelines.append(line)

        codeblock = CodeBlock(caption, codelines)
        nodecontent = NodeContent()
        nodecontent.set_codeblock(codeblock)
        return nodecontent

    def proceeded_as_line(self, line):
        lineobj = Line(line)
        nodecontent = NodeContent()
        nodecontent.set_line(lineobj)
        return nodecontent

class Page:
    def __init__(self):
        self._nodes = []

    def add_node(self, node):
        self._nodes.append(node)

    @property
    def nodes(self):
        return self._nodes

class Node:
    def __init__(self):
        INDENT_DEPTH_UNDEFINED = -1
        self._indent_depth = INDENT_DEPTH_UNDEFINED
        self._nodecontent = None

    def set_indent_depth(self, indent_depth):
        self._indent_depth = indent_depth

    def set_content(self, nodecontent):
        self._nodecontent = nodecontent

    @property
    def content(self):
        return self._nodecontent

class NodeContent:
    '''
    コンテンツのセットは利用者の責任で行わせる
    '''
    TYPE_LINE = 1
    TYPE_CODEBLOCK = 2
    TYPE_UNDEFINED = -1

    def __init__(self):
        self._type = self.TYPE_UNDEFINED

        self._content_by_obj = None

    def __str__(self):
        return f'type:{self._type}'

    def set_codeblock(self, codeblock):
        self._content_by_obj = codeblock
        self._type = self.TYPE_CODEBLOCK

    def set_line(self, instance_of_line):
        self._content_by_obj = instance_of_line
        self._type = self.TYPE_LINE

    def is_line(self):
        return self._type == self.TYPE_LINE

    def is_codeblock(self):
        return self._type == self.TYPE_CODEBLOCK

    @property
    def content(self):
        return self._content_by_obj

class CodeBlock:
    def __init__(self, caption, lines):
        self._caption = caption
        self._lines = lines

    @property
    def caption(self):
        return self._caption
    
    @property
    def lines(self):
        return self._lines

class Line:
    def __init__(self, line):
        self._raw = line
        self._inline_elements = []

    def _parse(self):
        line = self._raw
        linelen = len(line)

        # 1 リテラルを解釈する
        # 開始位置が見つかったら、終了位置も探しに行く

        # 2 リンクを解釈する
        # リンク用スタックを使って、最も内側のリンク表記だけ解釈されるようにする

        # 3 組み立てる
        # 

    @property
    def raw(self):
        return self._raw

    @property
    def inline_elements(self):
        return self._inline_elements

class QuoteLine:
    def __init__(self):
        pass

class BlankLine:
    def __init__(self):
        pass

class InlineElement:
    def __init__(self):
        pass

    @property
    def text(self):
        return self._text

    @property
    def uri(self):
        return self._uri

    @text.setter
    def text(self, text):
        self._text = text

    @uri.setter
    def uri(self, uri):
        self._uri = uri

class Plain(InlineElement):
    def __init__(self):
        super().__init__()

class Link(InlineElement):
    def __init__(self):
        super().__init__()

class Image(InlineElement):
    def __init__(self):
        super().__init__()

class Literal(InlineElement):
    def __init__(self):
        super().__init__()

if __name__ == "__main__":
    args = parse_arguments()
