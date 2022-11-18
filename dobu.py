# encoding: utf-8

def file2list(filepath):
    ret = []
    with open(filepath, encoding='utf8', mode='r') as f:
        ret = [line.rstrip('\n') for line in f.readlines()]
    return ret

def list2file(filepath, ls):
    with open(filepath, encoding='utf8', mode='w') as f:
        f.writelines(['{:}\n'.format(line) for line in ls] )

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

class FileParser:
    def __init__(self, linepasser):
        self._lp = linepasser

    def _parse(self):
        '''
        create page
        linesをlineごとにparseしてく
         create block_or_line
          ここで一気にn行かっさらうことがある。for line in linesとかだときつい。カウンタは原始的に管理すべきか
         create node
         node.add(block_or_line)
         page.add_node(node)
        '''
        lp = self._lp
        page = Page()
        while True:
            if lp.already_empty():
                break
            line = lp.next

            '''
            1 block or lineをつくる
             このとき、lpも渡して、必要ならn行分を取得してつくってしまう（block）
            2 nodeつくって、1をadd
            '''

class Page:
    def __init__(self):
        self._nodes = []

    def add_node(self, node):
        self._nodes.append(node)

class Node:
    def __init__(self, linepasser):
        INITIAL_DUMMY = 0
        self._indent = INITIAL_DUMMY

if __name__ == "__main__":
    args = parse_arguments()
