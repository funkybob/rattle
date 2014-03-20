
import ast
import rply

lg = rply.LexerGenerator()

lg.add('NUMBER', '\d+')
lg.add('STRING', "'.*?'|\".*?\"")
lg.add('NAME', '\w+')
lg.add('LSQB', '\[')
lg.add('RSQB', '\]')
lg.add('LPAREN', '\(')
lg.add('RPAREN', '\)')
#lg.add('EQUALS', '=')
#lg.add('COMMA', ',')
lg.add('DOT', '\.')


pg = rply.ParserGenerator(
    [rule.name for rule in lg.rules],
    precedence = [
    ],
)

'''

kwarg   :   NAME EQUALS expr

arg     :   expr

arg_list    :   arg
            |   arg COMMA arg_list

expr    :   NAME
        :   NUMBER
        :   STRING
        :   expr DOT NAME
        :   expr LSQB expr RSQB
        :   expr LPAREN RPAREN
        :   expr LPAREN arg_list RPAREN
        :   expr LPAREN kwarg_list RPAREN
        :   expr LPAREN arg_list COMMA kwarg_list RPAREN
'''

@pg.production('expr : NAME')
def expr_NAME(p):
    '''Look up a NAME in Context'''
    return ast.Subscript(
        value=ast.Name(id='context', ctx=ast.Load()),
        slice=ast.Index(value=ast.Str(s=p[0].getstr()), ctx=ast.Load()),
        ctx=ast.Load(),
    )

@pg.production('expr : STRING')
def expr_STRING(p):
    return ast.Str(s=p[0].getstr()[1:-1])

@pg.production('expr : NUMBER')
def expr_NUMBER(p):
    return ast.Number(n=int(p[0].getstr()))

@pg.production('expr : expr DOT NAME')
def expr_DOT_NAME(p):
    lterm, _, rterm = p
    return ast.Attribute(
        value=lterm,
        attr=rterm.getstr(),
        ctx=ast.Load(),
    )

@pg.production('expr : expr LSQB expr RSQB')
def expr_SUBSCRIPT(p):
    src, _, subscript, _ = p
    return ast.Subscript(
        value=src,
        slice=ast.Index(value=subscript, ctx=ast.Load()),
        ctx=ast.Load(),
    )

@pg.production('expr : expr LPAREN RPAREN')
def expr_empty_call(p):
    func, _, _ = p
    return ast.Call(
        func=func,
        args=[],
        keywords=[],
    )

@pg.error
def error(token):
    raise ValueError('Unexpected token: %r' % token)

if __name__ == '__main__':
    lexer = lg.build()
    parser = pg.build()

    class Mock(object):
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    TESTS = (
        ('a', {'a': 'yes'}, 'yes'),
        ('a.b', {'a': Mock(b='yes')}, 'yes'),
        ('a["b"]', {'a': {'b': 'yes'}}, 'yes'),
    )

    for src, ctx, out in TESTS:
        tokens = lexer.lex(src)
        expr = parser.parse(iter(tokens))

        src = ast.Module(body=[
            ast.Assign(
                targets=[ast.Name(id='result', ctx=ast.Store())],
                value=expr,
            )
        ])
        ast.fix_missing_locations(src)

        code = compile(src, filename='<ast>', mode='exec')

        glob = {'context': ctx}
        exec(code, glob)
        assert(glob['result'] == out)

