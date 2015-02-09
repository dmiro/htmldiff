#!/usr/bin/env python
"""
htmldiff.py
Original is (C) Ian Bicking <ianb@colorstudy.com>
With changes from Richard Cyganiak <richard@cyganiak.de>

Finds the differences between two HTML files.  *Not* line-by-line
comparison (more word-by-word).

Command-line usage:
  ./htmldiff.py test1.html test2.html

Better results if you use mxTidy first.  The output is HTML.
"""

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import re
import cgi
import urllib2
import argparse
import urlparse
from difflib import SequenceMatcher


class HTMLMatcher(SequenceMatcher):

    commentRE = re.compile('<!--.*?-->', re.S)
    tagRE = re.compile('<script.*?>.*?</script>|<.*?>', re.S)
    headRE = re.compile('<\s*head\s*>', re.S | re.I)
    wsRE = re.compile('^([ \n\r\t]|&nbsp;)+$')

    def __init__(self, source1, source2):
        isjunk = lambda x: self.wsRE.match(x)
        SequenceMatcher.__init__(self, isjunk, source1, source2, False)

    def set_seq1(self, a):
        SequenceMatcher.set_seq1(self, self._split_html(a))

    def set_seq2(self, b):
        SequenceMatcher.set_seq2(self, self._split_html(b))

    def html_encode(self, s, esc=cgi.escape):
        return esc(s, 1)

    def _split_tags(self, t):
        result = []
        pos = 0
        while 1:
            match = self.tagRE.search(t, pos=pos)
            if not match:
                result.append(t[pos:])
                break
            result.append(t[pos:match.start()])
            result.append(match.group(0))
            pos = match.end()
        return result

    def _split_words(self, t):
        return re.findall(r'([^ \n\r\t,.&;/#=<>()-]+|(?:[ \n\r\t]|&nbsp;)+|[,.&;/#=<>()-])', t)

    def _split_html(self, t):
        t = self.commentRE.sub('', t)
        r = self._split_tags(t)
        result = []
        for item in r:
            if item.startswith('<'):
                result.append(item)
            else:
                result.extend(self._split_words(item))
        return result

    def html_diff(self, addstylesheet=False):
        opcodes = self.get_opcodes()
        a = self.a
        b = self.b
        out = StringIO()
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                for item in a[i1:i2]:
                    out.write(item)
            if tag == 'delete':
                self._text_delete(a[i1:i2], out)
            if tag == 'insert':
                self._text_insert(b[j1:j2], out)
            if tag == 'replace':
                if self._is_invisible_change(a[i1:i2], b[j1:j2]):
                    for item in b[j1:j2]:
                        out.write(item)
                else:
                    self._text_delete(a[i1:i2], out)
                    self._text_insert(b[j1:j2], out)
        html = out.getvalue()
        out.close()
        if addstylesheet:
            html = self._add_stylesheet(html, self.stylesheet())
        return html

    def _is_invisible_change(self, seq1, seq2):
        if len(seq1) != len(seq2):
            return False
        for i in range(0, len(seq1)):
            #if seq1[i][0] == '<' and seq2[i][0] == '<':
            #    continue
            if self.wsRE.match(seq1[i]) and self.wsRE.match(seq2[i]):
                continue
            if seq1[i] != seq2[i]:
                return False
        return True

    def _text_delete(self, lst, out):
        text = ''
        for item in lst:
            if item.startswith('<'):
                self._out_delete(text, out)
                text = ''
                out.write(self.format_delete_tag(item))
            else:
                text += item
        self._out_delete(text, out)

    def _text_insert(self, lst, out):
        text = ''
        for item in lst:
            if item.startswith('<'):
                self._out_insert(text, out)
                text = ''
                out.write(self.format_insert_tag(item))
                out.write(item)
            else:
                text += item
        self._out_insert(text, out)

    def _out_delete(self, s, out):
        if s.strip() == '':
            out.write(s)
        else:
            out.write(self.start_delete_text())
            out.write(s)
            out.write(self.end_delete_text())

    def _out_insert(self, s, out):
        if s.strip() == '':
            out.write(s)
        else:
            out.write(self.start_insert_text())
            out.write(s)
            out.write(self.end_insert_text())

    def stylesheet(self):
        return '''
.insert { background-color: #aaffaa }
.delete { background-color: #ff8888; text-decoration: line-through }
.tagInsert { background-color: #007700; color: #ffffff }
.tagDelete { background-color: #770000; color: #ffffff }
'''

    def _add_stylesheet(self, html, ss):
        match = self.headRE.search(html)
        if match:
            pos = match.end()
        else:
            pos = 0
        return '%s<style type="text/css"><!--\n%s\n--></style>%s' % (html[:pos], ss, html[pos:])

    def start_insert_text(self):
        return '<span class="insert">'

    def end_insert_text(self):
        return '</span>'

    def start_delete_text(self):
        return '<span class="delete">'

    def end_delete_text(self):
        return '</span>'

    def format_insert_tag(self, tag):
        return '<span class="tagInsert">insert: <tt>%s</tt></span>' % self.html_encode(tag)

    def format_delete_tag(self, tag):
        return '<span class="tagDelete">delete: <tt>%s</tt></span>' % self.html_encode(tag)


class NoTagHTMLMatcher(HTMLMatcher):
    def format_insert_tag(self, tag):
        return ''

    def format_delete_tag(self, tag):
        return ''


class SimpleHTMLMatcher(HTMLMatcher):
    """Like HTMLMatcher, but returns a simpler diff
    """
    def start_insert_text(self):
        return '+['

    def end_insert_text(self):
        return ']'

    def start_delete_text(self):
        return '-['

    def end_delete_text(self):
        return ']'

    def format_insert_tag(self, tag):
        return '+[%s]' % tag

    def format_delete_tag(self, tag):
        return '-[%s]' % tag


class TextMatcher(HTMLMatcher):

    def set_seq1(self, a):
        SequenceMatcher.set_seq1(self, a.split('\n'))

    def set_seq2(self, b):
        SequenceMatcher.set_seq2(self, b.split('\n'))

    def html_diff(self, addstylesheet=False):
        opcodes = self.get_opcodes()
        a = self.a
        b = self.b
        out = StringIO()
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                self._write_lines(a[i1:i2], out)
            if tag == 'delete' or tag == 'replace':
                out.write(self.start_delete_text())
                self._write_lines(a[i1:i2], out)
                out.write(self.end_delete_text())
            if tag == 'insert' or tag == 'replace':
                out.write(self.start_insert_text())
                self._write_lines(b[j1:j2], out)
                out.write(self.end_insert_text())
        html = out.getvalue()
        out.close()
        if addstylesheet:
            html = self._add_stylesheet(html, self.stylesheet())
        return html

    def _write_lines(self, lines, out):
        for line in lines:
            line = self.html_encode(line)
            line = line.replace('  ', '&nbsp; ')
            line = line.replace('\t', '&nbsp; &nbsp; &nbsp; &nbsp; ')
            if line.startswith(' '):
                line = '&nbsp;' + line[1:]
            out.write('<tt>%s</tt><br>\n' % line)


def html_diff(source1, source2, notags=True, addstylesheet=False):
    """Return the difference between two pieces of HTML

        >>> html_diff('test1', 'test2')
        '<span class="delete">test1</span><span class="insert">test2</span>'
        >>> html_diff('test1', 'test1')
        'test1'
        >>> html_diff('<b>test1</b>', '<i>test1</i>', notags=False)
        '<span class="tagDelete">delete: <tt>&lt;b&gt;</tt></span><span class="tagInsert">insert: <tt>&lt;i&gt;</tt></span><i>test1<span class="tagDelete">delete: <tt>&lt;/b&gt;</tt></span><span class="tagInsert">insert: <tt>&lt;/i&gt;</tt></span></i>'
        >>> html_diff('<b>test1</b>', '<b>test1</b><x>test1</x>', notags=False)
        '<b>test1</b><span class="tagInsert">insert: <tt>&lt;x&gt;</tt></span><x><span class="insert">test1</span><span class="tagInsert">insert: <tt>&lt;/x&gt;</tt></span></x>'

    """
    if notags:
        h = NoTagHTMLMatcher(source1, source2)
    else:
        h = HTMLMatcher(source1, source2)
    return h.html_diff(addstylesheet)


def simple_html_diff(source1, source2):
    """Simpler form of htmldiff; mostly for testing, like:

        >>> simple_html_diff('test1', 'test2')
        '-[test1]+[test2]'
        >>> simple_html_diff('<b>Hello world!</b>', '<i>Hello you!</i>')
        '-[<b>]+[<i>]<i>Hello -[world!]-[</b>]+[you!]+[</i>]</i>'
    """
    h = SimpleHTMLMatcher(source1, source2)
    return h.html_diff()


def diff_resource(resource1, resource2, notags=True, addstylesheet=False, simplehtml=False):

    def get_source(resource):
        if urlparse.urlparse(resource).netloc:
            return urllib2.urlopen(resource).read()
        else:
            return open(resource).read()

    source1 = get_source(resource1)
    source2 = get_source(resource2)
    if simplehtml:
        return simple_html_diff(source1, source2)
    else:
        return html_diff(source1, source2, notags=notags, addstylesheet=addstylesheet)

def main():
    import sys

    parser = argparse.ArgumentParser(description='Outputs HTML that shows the differences in text between two versions '
                                                 'of an HTML document. Differences in markup are not shown.')
    parser.add_argument('resource1', help='File or URL to diff from')
    parser.add_argument('resource2', help='File or URL to diff against')
    parser.add_argument('-test', help='Test',
                        action='store_true', required=False, default=False)
    parser.add_argument('-ta', '--tags', help='Also compares the differences in tags',
                        action='store_true', required=False, default=False)
    parser.add_argument('-ss', '--stylesheet', help='Insert stylesheet to result',
                        action='store_true', required=False, default=False)
    parser.add_argument('-sh', '--simplehtml', help='Mostly for testing',
                        action='store_true', required=False, default=False)
    parser.add_argument('-o', '--output', help='Output file',
                        required=False)
                        
    args = parser.parse_args()

    if args.test:
        import doctest, sys
        results = doctest.testmod()
        if results.failed > 0:
            sys.exit(1)
    else:
        result = diff_resource(args.resource1, args.resource2, not args.tags, args.stylesheet, args.simplehtml)

    if args.output:
        try:
            dhtml = open(args.output, 'w')
            dhtml.write(result)
            dhtml.close()
        except Exception, ex:
            print ex
            sys.exit(1)
    else:
        print result


if __name__ == '__main__':
    main()
