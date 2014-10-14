import re

TOKEN_TEXT = 0
TOKEN_VAR = 1
TOKEN_BLOCK = 2
TOKEN_COMMENT = 3
TOKEN_MAPPING = {
    TOKEN_TEXT: u'Text',
    TOKEN_VAR: u'Var',
    TOKEN_BLOCK: u'Block',
    TOKEN_COMMENT: u'Comment',
}


class Token(object):
    __slots__ = ('mode', 'content', 'line', 'col',)

    def __init__(self, mode, content, line=None, col=None):
        self.mode = mode
        self.content = content
        self.line = line
        self.col = col

    def __repr__(self):
        return u'{%s} %s' % (TOKEN_MAPPING[self.mode], self.content,)

    def _position(self, node):
        """
        Annotate an AST node with this token's row/col
        """
        node.lineno = self.line
        node.col_offset = self.col
        return node

tag_re = re.compile(r'{%\s*(?P<tag>.+?)\s*%}|'
                    r'{{\s*(?P<var>.+?)\s*}}|'
                    r'{#\s*(?P<comment>.+?)\s*#}')


def tokenise(template):
    """
    A generator which yields Token instances
    """
    upto = 0
    lineno = 0
    start = 0
    for m in tag_re.finditer(template):
        start, end = m.span()
        if upto < start:
            yield Token(TOKEN_TEXT, template[upto:start], line=lineno, col=upto)
        tag, var, comment = m.groups()
        if tag is not None:
            yield Token(TOKEN_BLOCK, tag, line=lineno, col=start)
        elif var is not None:
            yield Token(TOKEN_VAR, var, line=lineno, col=start)
        else:
            yield Token(TOKEN_COMMENT, comment, line=lineno, col=start)
        lineno += template[upto:end].count('\n')
        upto = end
    if upto < len(template):
        yield Token(TOKEN_TEXT, template[upto:], line=lineno, col=start)
