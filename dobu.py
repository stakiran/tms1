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
        '''
        indent判定

        block判定

        if blockじゃない then lineとして処理
        else blockとして処理
        '''
        return None

class Page:
    def __init__(self):
        self._nodes = []

    def add_node(self, node):
        self._nodes.append(node)

class Node:
    def __init__(self):
        INITIAL_DUMMY = 0
        self._indent = INITIAL_DUMMY

if __name__ == "__main__":
    args = parse_arguments()
