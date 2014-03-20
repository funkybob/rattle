
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
lg.add('EQUALS', '=')
lg.add('COMMA', ',')
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

@pg.production('arg : expr')
def arg_expr(p):
    return p[0]

@pg.production('arg_list : arg')
def arg_list_arg(p):
    return p

@pg.production('arg_list : arg COMMA arg_list')
def arg_list_prepend(p):
    arg, _, arg_list = p
    arg_list.insert(0, arg)
    return arg_list

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

@pg.production('expr : expr LPAREN arg_list RPAREN')
def expr_args_cll(p):
    func, _, args, _ = p
    print "CALL: %r" % p
    return ast.Call(
        func=func,
        args=args,
        keywords=[],
    )

@pg.error
def error(token):
    raise ValueError('Unexpected token: %r' % token)
