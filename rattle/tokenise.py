
import ast
import re
import tokenize
from StringIO import StringIO

TOKEN_TEXT = 0
TOKEN_VAR = 1
TOKEN_BLOCK = 2
TOKEN_COMMENT = 3
TOKEN_MAPPING = {
    TOKEN_TEXT: 'Text',
    TOKEN_VAR: 'Var',
    TOKEN_BLOCK: 'Block',
    TOKEN_COMMENT: 'Comment',
}

class Token(object):
    __slots__ = ('mode', 'content', 'line', 'col',)
    def __init__(self, mode, content, line=None, col=None):
        self.mode = mode
        self.content = content
        self.line = line
        self.col = col

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

def parse_expr(content):
    '''Turn a content string into AST'''
    stream = tokenize.generate_tokens(StringIO(content).redline)

    # First token MUST be either a literal, or name
    tok = next(stream)
    if tok.exact_type == tokenize.STRING:
        code = ast.String(s=tok.string)
    elif tok.exact_type == tokenize.NUMBER:
        if '.' in tok.string:
            val = float(tok.string)
        else:
            val = int(tok.string)
        code = ast.Num(n=val)
    elif tok.exact_type == tokenize.NAME:
        code = ast.Subscript(value=ast.Name(id='context', ctx=ast.Load()), slice=ast.Index(value=ast.Str(s=tok.string), ctx=ast.Load()))
    else:
        raise TemplateSyntaxError(content)

    for tok in stream:
        if tok.exact_type == tokenize.DOT:
            code = ast.Attribute(value=code, )
        elif tok.exact_type == tokenize.LSQB:
            ntok = next(stream)
            # Subscript
            code = ast.Subscript(value=code, slice=ast.Index(value=
    return ast.Expr(value=code)


class Template(object):
    def __init__(self, source):
        self.source = source

        self.func = self.parse()

    def parse(self):
        '''Convert the parsed tokens into a list of expressions
        Then join them'''
        steps = []
        for token in tokenise(self.source):
            if token.mode == TOKEN_TEXT:
                steps.append(
                    ast.Expr(value=ast.Str(s=token.content))
                )
            elif token.mode == TOKEN_VAR:
                # parse
                steps.append(
                    parse_expr(token.content)
                )
            elif token.mode == TOKEN_BLOCK:
                # Parse args/kwargs
                # create tag class instance

        return ast.Module(body=[
            ast.Expr(value=ast.ListComp(
                elt=ast.Call(func=ast.Name(id='str', ctx=ast.Load()), args=[
                    ast.Name(id='x', ctx=ast.Load()),
                ]),
                generators=[
                    ast.comprehension(
                        target=ast.Name(id='x', ctx=ast.Store()),
                        iter=ast.Name('steps', ctx=ast.Load()),
                        ifx=[]
                    )
                ]
            ))
        # value=ListComp(elt=Call(func=Name(id='str', ctx=Load())

    def render(self, context):
        return self.func(context)

