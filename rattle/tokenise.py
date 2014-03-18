
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

tag_re = re.compile(r'{%\s*(?P<tag>.+?)\s*%}|{{\s*(?P<var>.+?)\s*}}|{#\s*(?P<comment>.+?)\s*#}')

                
def tokenise(template):
    '''A generator which yields Token instances'''
    # XXX Add line number tracking
    # XXX Add line, col tracking to tokens
    upto = 0
    for m in tag_re.finditer(template):
        start, end = m.span()
        if upto < start:
            yield Token(TOKEN_TEXT, template[upto:start], col=upto)
        upto = end
        tag, var, comment = m.groups()
        if tag is not None:
            yield Token(TOKEN_BLOCK, tag, col=start)
        elif var is not None:
            yield Token(TOKEN_VAR, var, col=start)
        else:
            yield Token(TOKEN_COMMENT, comment, col=start)
    if upto < len(template):
        yield Token(TOKEN_TEXT, template[upto:], col=start)

