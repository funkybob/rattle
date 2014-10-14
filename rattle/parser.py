
import ast

import rply

from .lexer import lg
from .utils.parser import build_call, get_lookup_name


pg = rply.ParserGenerator(
    [rule.name for rule in lg.rules],
    precedence=[
        ('left', ['COMMA']),
        ('right', ['ASSIGN']),
        ('left', ['PLUS', 'MINUS']),
        ('left', ['MUL', 'DIV', 'MOD']),
        ('left', ['LSQB', 'RSQB']),
        ('left', ['PIPE']),
        ('left', ['DOT']),
        ('left', ['LPAREN', 'RPAREN']),
    ],
)

"""

arg     :   expr

arg_list    :   arg
            |   arg_list COMMA arg

expr    :   NAME
        |   NUMBER
        |   STRING
        |   expr DOT NAME
        |   expr PLUS expr
        |   expr MINUS expr
        |   expr MUL expr
        |   expr DIV expr
        |   expr MOD expr
        |   expr filter
        |   LPAREN expr RPAREN
        |   expr LSQB expr RSQB
        |   expr LPAREN RPAREN
        |   expr LPAREN arg_list RPAREN
        |   expr LPAREN kwarg_list RPAREN
        |   expr LPAREN arg_list COMMA kwarg_list RPAREN

filter  :   PIPE lookup_name

kwarg   :   NAME ASSIGN expr

kwarg_list  :   kwarg
            |   kwarg_list COMMA kwarg

lookup_name : NAME
            | lookup_name DOT NAME
"""

lg.ignore(r"\s+")


@pg.production('arg : expr')
def arg_expr(p):
    return p[0]


@pg.production('arg_list : arg')
def arg_list_arg(p):
    return p


@pg.production('arg_list : arg_list COMMA arg')
def arg_list_append(p):
    arg_list, _, arg = p
    arg_list.append(arg)
    return arg_list


@pg.production('expr : NAME')
def expr_NAME(p):
    """
    Look up a NAME in Context
    """
    return ast.Subscript(
        value=ast.Name(id='context', ctx=ast.Load()),
        slice=ast.Index(value=ast.Str(s=p[0].getstr()), ctx=ast.Load()),
        ctx=ast.Load(),
    )


@pg.production('expr : NUMBER')
def expr_NUMBER(p):
    number = p[0].getstr()
    if '.' in number or 'e' in number or 'E' in number:
        cast = float
    else:
        cast = int
    return ast.Num(n=cast(number))


@pg.production('expr : STRING')
def expr_STRING(p):
    return ast.Str(s=p[0].getstr()[1:-1])


@pg.production('expr : expr DOT NAME')
def expr_DOT_NAME(p):
    lterm, _, rterm = p
    return ast.Attribute(
        value=lterm,
        attr=rterm.getstr(),
        ctx=ast.Load(),
    )


_operator_mapping = {
    'PLUS': ast.Add,
    'MINUS': ast.Sub,
    'MUL': ast.Mult,
    'DIV': ast.Div,
    'MOD': ast.Mod,
}


@pg.production('expr : expr PLUS expr')
@pg.production('expr : expr MINUS expr')
@pg.production('expr : expr MUL expr')
@pg.production('expr : expr DIV expr')
@pg.production('expr : expr MOD expr')
def expr_binop(p):
    lterm, op, rterm = p
    operator = _operator_mapping[op.gettokentype()]
    return ast.BinOp(left=lterm, op=operator(), right=rterm)


@pg.production('expr : expr filter')
def expr_filter(p):
    arg, filter = p
    return build_call(filter, [arg])


@pg.production('expr : LPAREN expr RPAREN')
def expr_binop_paren(p):
    return p[1]


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
    return build_call(func)


@pg.production('expr : expr LPAREN arg_list RPAREN')
def expr_args_call(p):
    func, _, args, _ = p
    return build_call(func, args)


@pg.production('expr : expr LPAREN kwarg_list RPAREN')
def expr_kwargs_call(p):
    func, _, kwargs, _ = p
    return build_call(func, kwargs=kwargs)


@pg.production('expr : expr LPAREN arg_list COMMA kwarg_list RPAREN')
def expr_full_call(p):
    func, _, args, _, kwargs, _ = p
    return build_call(func, args, kwargs)


@pg.production('filter : PIPE lookup_name')
def filter_pipe_lookup_name(p):
    filter_name = get_lookup_name(p[1])

    filter_func = ast.Subscript(
        value=ast.Name(id='filters', ctx=ast.Load()),
        slice=ast.Index(value=filter_name, ctx=ast.Load()),
        ctx=ast.Load(),
    )
    return filter_func


@pg.production('kwarg : NAME ASSIGN expr')
def keyword(p):
    name, _, expr = p
    return ast.keyword(arg=name.getstr(), value=expr)


@pg.production('kwarg_list : kwarg')
def kwarg_list_kwarg(p):
    return p


@pg.production('kwarg_list : kwarg_list COMMA kwarg')
def kwarg_list_append(p):
    kwarg_list, _, kwarg = p
    kwarg_list.append(kwarg)
    return kwarg_list


@pg.production('lookup_name : NAME')
def lookup_name_NAME(p):
    return [ast.Str(s=p[0].getstr())]


@pg.production('lookup_name : lookup_name DOT NAME')
def lookup_name_append(p):
    lookup_name, _, name = p
    lookup_name.append(ast.Str(s=name.getstr()))
    return lookup_name


@pg.error
def error(token):
    raise ValueError('Unexpected token: %r' % token)
