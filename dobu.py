# encoding: utf-8

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

    @staticmethod
    def cut_as_subline(s, base_depth):
        if len(s)<base_depth:
            return s
        return s[base_depth+1:]

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
    # nodefactoryをもらうようにした方がいいか？たぶんここでlpは使わねえし
    def __init__(self, linepasser):
        self._lp = linepasser

    def _parse(self):
        page = Page()
        nodefactory = NodeFactory(self._lp)
        while True:
            if nodefactory.already_empty():
                break
            node = nodefactory.get_next_node()
            page.add_node(node)

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

        nodecontent = self.proceed_as_something(indent, line_without_indent, lp)
        node.set_content(nodecontent)

        return node

    def proceed_as_something(self, indent, line_without_indent, lp):
        if Judgement.is_codeblock_start(line_without_indent):
            return self.proceeded_as_codeblock(indent, line_without_indent, lp)
        return self.proceeded_as_line(line_without_indent)

    def proceeded_as_codeblock(self, indent, line_without_indent, lp):
        _, caption = line_without_indent.split(':', maxsplit=1)

        codelines = []
        while True:
            line = lp.next
            line = Indent.cut_as_subline(line, base_depth=indent)
            break

        return None

    def proceeded_as_line(self, line):
        return None

class Page:
    def __init__(self):
        self._nodes = []

    def add_node(self, node):
        self._nodes.append(node)

class Node:
    def __init__(self):
        INDENT_DEPTH_UNDEFINED = -1
        self._indent_depth = INDENT_DEPTH_UNDEFINED
        self._nodecontent = None

    def set_indent_depth(self, indent_depth):
        self._indent_depth = indent_depth

    def set_content(self, nodecontent):
        self._nodecontent = nodecontent

class NodeContent:
    def __init__(self):
        #TYPE_BLOCK = 0
        TYPE_LINE = 1
        TYPE_CODEBLOCK = 2
        TYPE_UNDEFINED = -1
        self._type = TYPE_UNDEFINED

        self._content_by_obj = None

    def is_line(self):
        return False

    def is_codeblock(self):
        return False

class CodeBlock:
    def __init__(self):
        pass

class Line:
    def __init__(self):
        pass

if __name__ == "__main__":
    args = parse_arguments()
