#!/usr/bin/env python
# -*- coding: utf-8 -*-

import difflib
import six
import xml.sax.saxutils
import chardet


class GHDiff(object):
    html_start = '<div class="diff">'
    html_end = '</div>'
    html_line = '<div class="%(css_class)s">%(prefix)s%(content)s</div>'
    html_highlight = '<span class="%(css_class)s">%(content)s</span>'

    css_classes = {}  # defaul to control/insert/delete/highlight

    @classmethod  # should be a classproperty
    def css(cls):
        return """\
            <style type="text/css">
                .diff {
                    border: 1px solid #cccccc;
                    background: none repeat scroll 0 0 #f8f8f8;
                    font-family: 'Bitstream Vera Sans Mono','Courier',monospace;
                    font-size: 12px;
                    line-height: 1.4;
                    white-space: normal;
                    word-wrap: break-word;
                }
                .diff div:hover {
                    background-color:#ffc;
                }
                .diff .%(control_class)s {
                    background-color: #eaf2f5;
                    color: #999999;
                }
                .diff .%(insert_class)s {
                    background-color: #ddffdd;
                    color: #000000;
                }
                .diff .%(insert_class)s .%(highlight_class)s {
                    background-color: #aaffaa;
                    color: #000000;
                }
                .diff .%(delete_class)s {
                    background-color: #ffdddd;
                    color: #000000;
                }
                .diff .%(delete_class)s .%(highlight_class)s {
                    background-color: #ffaaaa;
                    color: #000000;
                }
            </style>
            """ % dict(('%s_class' % key, cls.css_classes.get(key, key))
                       for key in ('control', 'insert', 'delete', 'highlight'))

    @classmethod
    def escape(cls, text):
        return xml.sax.saxutils.escape(text, {" ": "&nbsp;"})

    @classmethod
    def diff(cls, a, b, n=3, css=True):
        if isinstance(a, six.string_types):
            a = a.splitlines()
        if isinstance(b, six.string_types):
            b = b.splitlines()
        return cls.colorize(list(difflib.unified_diff(a, b, n=n)), css=css)

    @classmethod
    def colorize(cls, diff, css=True):
        css = cls.css() if css else ""
        return css + "\n".join(cls._colorize(diff))

    @classmethod
    def _colorize(cls, diff):
        if isinstance(diff, six.string_types):
            lines = diff.splitlines()
        else:
            lines = diff
        lines.reverse()
        while lines and not lines[-1].startswith("@@"):
            lines.pop()
        yield cls.html_start
        while lines:
            line = lines.pop()
            css_class = ""
            if line.startswith("@@"):
                css_class = "control"
            elif line.startswith("-"):
                css_class = "delete"
                if lines:
                    _next = []
                    while lines and len(_next) < 2:
                        _next.append(lines.pop())
                    if _next[0].startswith("+") and (len(_next) == 1
                        or _next[1][0] not in ("+", "-")):
                        aline, bline = cls._line_diff(line[1:], _next.pop(0)[1:])
                        yield cls._make_line('delete', aline, prefix='-')
                        yield cls._make_line('insert', bline, prefix='+')
                        if _next:
                            lines.append(_next.pop())
                        continue
                    lines.extend(reversed(_next))
            elif line.startswith("+"):
                css_class = "insert"
            yield cls._make_line(css_class, cls.escape(line))
        yield cls.html_end

    @classmethod
    def _make_line(cls, css_class, content, prefix=''):
        return cls.html_line % {
            'css_class': cls.css_classes.get(css_class, css_class),
            'prefix': prefix,
            'content': content,
        }

    @classmethod
    def _make_highlight(cls, content):
        css_class = 'highlight'
        return cls.html_highlight % {
            'css_class': cls.css_classes.get(css_class, css_class),
            'content': cls.escape(content),
        }

    @classmethod
    def _line_diff(cls, a, b):
        aline = []
        bline = []
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b).get_opcodes():
            if tag == "equal":
                aline.append(cls.escape(a[i1:i2]))
                bline.append(cls.escape(b[j1:j2]))
                continue
            aline.append(cls._make_highlight(a[i1:i2]))
            bline.append(cls._make_highlight(b[j1:j2]))
        return "".join(aline), "".join(bline)


if __name__ == "__main__":
    import optparse
    import sys

    parser = optparse.OptionParser()
    parser.set_usage("%prog [options] file1 file2")
    parser.add_option("--no-css", action="store_false", dest="css",
                      help="Don't include CSS in output", default=True)

    options, args = parser.parse_args()

    if (len(args) != 2):
        parser.print_help()
        sys.exit(-1)

    def read_file(filename):
        with open(filename) as f:
            text = f.read()
        codepage = chardet.detect(text)['encoding']
        return text.decode(codepage).splitlines()

    a = read_file(sys.argv[1])
    b = read_file(sys.argv[2])
    print(GHDiff.diff(a, b, css=options.css).encode('utf-8'))
