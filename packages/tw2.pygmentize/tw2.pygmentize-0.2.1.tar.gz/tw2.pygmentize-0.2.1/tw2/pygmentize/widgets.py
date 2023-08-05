import tw2.core as twc

from pygments import highlight
from pygments.lexers import get_lexer_by_name, get_lexer_for_filename,\
    find_lexer_class, get_lexer_for_mimetype
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound


class Pygmentize(twc.Widget):
    template = "tw2.pygmentize.templates.pygmentize"

    name = twc.Variable(default=property(lambda s: hasattr(s, 'compound_id') and s.compound_id or hasattr(s, 'id') and s.id or ''))

    lexer_name = twc.Param(default=None,
        description='Hint to find the Pygments lexer')
    lexer_args = twc.Param(default=dict(),
        description='Additional arguments for the Pygments lexer')

    formatter_class = twc.Param(default=HtmlFormatter,
        description='Pygments formatter class')
    style = twc.Param(default=u'default',
        description='Pygments formatter style attribute')
    noclasses = twc.Param(default=True,
        description='Pygments formatter noclasses attribute (use style attributes in the HTML tags instead)')
    formatter_args = twc.Param(default=dict(),
        description='Additional arguments for the Pygments formatter')

    filename = twc.Param(default=None,
        description='Filename of displayed file (only used for additional Pygments lexer detection)')
    source = twc.Param(default='',
        description='Source code to highlight and display')

    def prepare(self):
        super(Pygmentize, self).prepare()

        lexer = None

        # Try very hard to get any lexer

        if self.filename:
            try:
                lexer = get_lexer_for_filename(self.filename, self.source or None, **self.lexer_args)
            except ClassNotFound:
                pass

        if self.lexer_name:
            lexer = find_lexer_class(self.lexer_name)
            if lexer:
                lexer = lexer(**self.lexer_args)

            try:
                lexer = get_lexer_by_name(self.lexer_name, **self.lexer_args)
            except ClassNotFound:
                pass

            try:
                lexer = get_lexer_for_mimetype(self.lexer_name, **self.lexer_args)
            except ClassNotFound:
                pass

        if not lexer:
            # Fallback, so that we at least have line numbering
            lexer = get_lexer_by_name('text', **self.lexer_args)

        formatter_args = dict(self.formatter_args)
        if self.name:
            for k in 'lineanchors', 'linespans':
                if k in formatter_args:
                    formatter_args[k] = self.name + '_' + formatter_args[k]
        formatter_args['style'] = self.style
        formatter_args['noclasses'] = self.noclasses
        formatter = self.formatter_class(**formatter_args)

        self.source = highlight(self.source, lexer, formatter)
