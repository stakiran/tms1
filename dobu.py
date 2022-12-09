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

LB = '\n'
def string2lines(s):
    return s.split(LB)

def list2file(filepath, ls):
    with open(filepath, encoding='utf8', mode='w') as f:
        f.writelines(['{:}\n'.format(line) for line in ls] )

def is_http(line, use_https=False):
    line_without_casesensitive = line.lower()
    if use_https:
        s = 'https://'
    else:
        s = 'http://'
    sl = len(s)

    if len(line_without_casesensitive)<sl:
        return False
    if line_without_casesensitive[:sl]==s:
        return True
    return False

def is_https(line):
    return is_http(line, use_https=True)

def get_corrected_filename(filename):
    # Use algorithm og https://github.com/stakiran/vscode-scb/blob/master/language-feature/src/util.ts#L29
    invalid_chars ='\\/:*?"<>|'
    noisy_chars =' '
    target_chars = invalid_chars + noisy_chars

    after_char = '_'

    ret = filename
    for target_char in target_chars:
        ret = ret.replace(target_char, after_char)
    return ret

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
        self._name = ''

    def add_node(self, node):
        self._nodes.append(node)

    @property
    def nodes(self):
        return self._nodes

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

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
    def indent_depth(self):
        return self._indent_depth

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
        self._is_quote = False

        initial = Undefined(self._raw)
        self._inline_elements.append(initial)
        self._parse_mode()
        self._parse()

    def _parse_mode(self):
        line = self._raw
        is_empty = len(line)==0
        is_no_content = len(line)==1

        if is_empty:
            return
        if is_no_content:
            return

        firstchar = line[0]
        if firstchar == '>':
            self._is_quote = True

    def _parse(self):
        new_inline_elements = []
        for inlineelement in self._inline_elements:
            # 1 リテラルの解釈
            line = inlineelement.raw
            start_of_parse = 0
            while True:
                startpos = line.find('`', start_of_parse)
                not_found_startpos = startpos == -1
                if not_found_startpos:
                    break

                endpos = line.find('`', startpos+1)
                not_found_endpos = endpos == -1
                if not_found_endpos:
                    break

                # ......`......`...
                # ^^^^^^        ^^^
                #  head         tail

                head = line[start_of_parse:startpos]
                is_head_empty = len(head)==0
                if is_head_empty:
                    pass
                else:
                    head_is_undefined_yet = Undefined(head)
                    new_inline_elements.append(head_is_undefined_yet)

                literal = line[startpos+1:endpos]
                literalobj = Literal(literal)
                new_inline_elements.append(literalobj)

                start_of_parse = endpos+1
            tail = line[start_of_parse:] 
            is_tail_empty = len(tail)==0
            if is_tail_empty:
                continue
            tail_is_undefined_yet = Undefined(tail)
            new_inline_elements.append(tail_is_undefined_yet)
        self._inline_elements_at_literal = new_inline_elements
        # これで new_inline_elements は undefined, literal, literal, undfined, undefined, literal みたいになる

        self._inline_elements = new_inline_elements
        new_inline_elements = []
        for inlineelement in self._inline_elements:
            # 2 リンクの解釈
            is_literal = isinstance(inlineelement, Literal)
            if is_literal:
                new_inline_elements.append(inlineelement)
                continue

            line = inlineelement.raw
            start_of_parse = 0
            while True:
                startpos = line.find('[', start_of_parse)
                not_found_startpos = startpos == -1
                if not_found_startpos:
                    break

                # ...[....[...
                #    1    2
                # 終端 ] の前に先に [ が見つかった場合、後者の位置から探索を再開

                # ...[....]...[...
                #    1    2
                # 終端 ] が先に来た場合、リンクとみなせる

                nextstartpos = line.find('[', startpos+1)
                endpos = line.find(']', startpos+1)

                not_found_endpos = endpos == -1
                if not_found_endpos:
                    break

                maybe_nested = -1 < nextstartpos and nextstartpos < endpos
                if maybe_nested:
                    start_of_parse = nextstartpos + 1
                    continue

                # ......[......]...
                # ^^^^^^        ^^^
                #  head         tail


                head = line[start_of_parse:startpos]
                is_head_empty = len(head)==0
                if is_head_empty:
                    pass
                else:
                    head_is_undefined_yet = Undefined(head)
                    new_inline_elements.append(head_is_undefined_yet)

                link = line[startpos+1:endpos]
                link = Link(link)
                new_inline_elements.append(link)

                start_of_parse = endpos+1
            tail = line[start_of_parse:] 
            is_tail_empty = len(tail)==0
            if is_tail_empty:
                continue
            tail_is_undefined_yet = Undefined(tail)
            new_inline_elements.append(tail_is_undefined_yet)
        self._inline_elements_at_link = new_inline_elements
        # これで new_inline_elements は undefined, literal, literal, (undefined, link, link), (link), literal みたいになる

        self._inline_elements = new_inline_elements
        new_inline_elements = []
        for inlineelement in self._inline_elements:
            is_literal = isinstance(inlineelement, Literal)
            is_link = isinstance(inlineelement, Link)
            if is_literal or is_link:
                new_inline_elements.append(inlineelement)
                continue

            line = inlineelement.raw
            plain = Plain(line)
            new_inline_elements.append(plain)
        # これで new_inline_elements は plain, literal, literal, plain, link, link, link, literal みたいになる
        self._inline_elements_at_plain = new_inline_elements

        self._inline_elements = new_inline_elements

    @property
    def raw(self):
        return self._raw

    @property
    def inline_elements(self):
        return self._inline_elements

    @property
    def is_quote(self):
        return self._is_quote

class QuoteLine:
    def __init__(self):
        pass

class BlankLine:
    def __init__(self):
        pass

class InlineElement:
    def __init__(self, raw):
        self._raw = raw
        self._text = None
        self._uri = None

    @property
    def raw(self):
        return self._raw

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

class Undefined(InlineElement):
    def __init__(self, raw):
        super().__init__(raw)

class Plain(InlineElement):
    def __init__(self, raw):
        super().__init__(raw)
        self._text = raw

class Link(InlineElement):
    def __init__(self, raw):
        super().__init__(raw)

        self._text = ''
        self._uri = ''
        self._parse()

    def _parse(self):
        line = self._raw
        ls = line.split(' ')
        is_single_element = len(ls)==0

        # [xxxx]
        # [http://...]
        # [https://...]
        if is_single_element:
            if is_http(line) or is_https(line):
                self._uri = line
                return
            self._text = line
            return

        # [uri rest]
        # [rest uri]
        # restは複数のスペースを含む可能性がある
        first = ls[0]
        last = ls[-1]
        if is_http(first) or is_https(first):
            self._uri = first
            self._text = ' '.join(ls[1:])
            return
        if is_http(last) or is_https(last):
            self._uri = last
            self._text = ' '.join(ls[:-1])
            return
        self._text = line

class Uri(InlineElement):
    # 今のところ画像は無いので、Image ではなく「URLのみ記されたもの」的な概念として定義しておく
    def __init__(self, raw):
        super().__init__(raw)

class Literal(InlineElement):
    def __init__(self, raw):
        super().__init__(raw)
        self.text = raw

class Renderer:
    def __init__(self, page):
        self.page = page

    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, page):
        self._page = page

    def render(self):
        page = self.page
        nodes = page.nodes
        outlines = []

        lines = self._render_page_header(page)
        outlines.extend(lines)

        for node in nodes:
            lines = self._render_node(node)
            outlines.extend(lines)

        lines = self._render_page_footer(page)
        outlines.extend(lines)

        return outlines

    def _render_node(self, node):
        indent_depth = node.indent_depth
        nodecontent = node.content
        contentobj = nodecontent.content

        lines = ['<NOT INTERPRETED in node level>']
        if nodecontent.is_codeblock():
            lines = self._render_codeblock(contentobj, indent_depth)
        if nodecontent.is_line():
            lines = self._render_line(contentobj, indent_depth)
        return lines

    def _render_line(self, lineobj, indent_depth):
        outlines = []

        inline_elements = lineobj.inline_elements
        rawline = lineobj.raw

        element_outlines = self._render_line_header(lineobj, indent_depth)
        outlines.extend(element_outlines)

        for inline_element in inline_elements:
            element_outlines = ['<NOT INTERPRETED in inline-element level>']
            if isinstance(inline_element, Link):
                element_outlines = self._render_link(inline_element)
            if isinstance(inline_element, Literal):
                element_outlines = self._render_literal(inline_element)
            if isinstance(inline_element, Link):
                element_outlines = self._render_link(inline_element)
            if isinstance(inline_element, Plain):
                element_outlines = self._render_plain(inline_element)
            outlines.extend(element_outlines)

            # たぶん inlineelement 間のマージンを入れるi/fもあった方がいい……

        element_outlines = self._render_line_footer(lineobj, indent_depth)
        outlines.extend(element_outlines)

        return outlines

    def _render_page_header(self, page):
        raise NotImplementedError('Must return lines!')

    def _render_page_footer(self, page):
        raise NotImplementedError('Must return lines!')

    def _render_codeblock(self, codeblock, indent_depth):
        raise NotImplementedError('Must return lines!')

    def _render_line_header(self, rawline, indent_depth):
        raise NotImplementedError('Must return lines!')

    def _render_line_footer(self, rawline, indent_depth):
        raise NotImplementedError('Must return lines!')

    def _render_link(self, inline_element):
        raise NotImplementedError('Must return lines!')

    def _render_literal(self, inline_element):
        raise NotImplementedError('Must return lines!')

    def _render_plain(self, inline_element):
        raise NotImplementedError('Must return lines!')

class DebugRenderer(Renderer):
    def __init__(self, page):
        super().__init__(page)

    def _render_page_header(self, page):
        return ['---- page header ----{']

    def _render_page_footer(self, page):
        return ['}---- page footer ----']

    def _render_line_header(self, lineobj, indent_depth):
        lines = []
        quote = ''
        if lineobj.is_quote:
            quote = '(>)'
        lines.append(f'head of line{quote}{{')
        return lines

    def _render_line_footer(self, lineobj, indent_depth):
        lines = []
        lines.append('}tail of line')
        return lines

    def _render_codeblock(self, codeblock, indent_depth):
        lines = []
        lines.append(f'codeblock: {codeblock.caption}')
        lines.append(f' indent: {indent_depth}')
        lines.append('====')
        lines.extend(codeblock.lines)
        return lines

    def _render_link(self, inline_element):
        lines = []
        lines.append('Link')
        lines.append(f' uri :"{inline_element.uri}"')
        lines.append(f' text:"{inline_element.text}"')
        return lines

    def _render_literal(self, inline_element):
        lines = []
        lines.append('Literal')
        lines.append(f' "{inline_element.text}"')
        return lines

    def _render_plain(self, inline_element):
        lines = []
        lines.append('Plain')
        lines.append(f' "{inline_element.text}"')
        return lines

class HTMLRenderer(Renderer):
    def __init__(self, page):
        super().__init__(page)

    def _render_page_header(self, page):
        title = f'{page.name}'
        s = f"""
<!DOCTYPE html>
<html>
    <head>
        <meta charSet="utf-8"/>
        <meta name="referrer" content="same-origin"/>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0"/>
        <title>{title}</title>
        <link rel="stylesheet" href="stylesheet.css"/>
    </head>
<body>
"""
        lines = string2lines(s)
        return lines

    def _render_page_footer(self, page):
        s = f"""</body>
</html>
"""
        lines = string2lines(s)
        return lines

    def _render_line_header(self, lineobj, indent_depth):
        lines = []

        margin_value = 1.5*indent_depth
        indent_part = f'margin-left: {margin_value}em;'

        quote_part = ''
        if lineobj.is_quote:
            quote_part = '<blockquote>'
        lines.append(f'<div class="node line" style="{indent_part}">{quote_part}<span>')
        return lines

    def _render_line_footer(self, lineobj, indent_depth):
        lines = []
        blankline = ''
        quote_part = ''
        if lineobj.is_quote:
            quote_part = '</blockquote>'
        lines.append(f'</span>{quote_part}</div>')
        lines.append(blankline)
        return lines

    def _render_codeblock(self, codeblock, indent_depth):
        lines = []

        margin_value = 1.5*indent_depth
        indent_part = f'margin-left: {margin_value}em;'

        lines.append(f'<div class="node" style="{indent_part}">')
        lines.append(f'<span class="code-block-start">{codeblock.caption}</span>')
        lines.append(f'<pre class="code-block">')
        lines.extend(codeblock.lines)
        lines.append('</pre></div>')
        return lines

    def _render_link(self, inline_element):
        lines = []

        uri = inline_element.uri
        text = inline_element.text
        is_link_in_page = inline_element.uri == ''
        if is_link_in_page:
            filename = text
            uri = filename
            uri = get_corrected_filename(uri)
            uri = f'{uri}.html'

        lines.append(f'<span class="link"><a href="{uri}">{text}</a></span>')
        return lines

    def _render_literal(self, inline_element):
        lines = []
        lines.append(f'<code class="literal">{inline_element.text}</code>')
        return lines

    def _render_plain(self, inline_element):
        lines = []
        lines.append(f'<span class="plain">{inline_element.text}</span>')
        return lines

if __name__ == "__main__":
    args = parse_arguments()
