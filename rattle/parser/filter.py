import ast

from . import parsers

from ..utils.parser import (build_call, get_filter_func, get_lookup_name,
    production)


fpg = parsers.fpg
"""
Filter parser generator.

Used to tokenize content inside ``{{`` and ``}}`` as well as the args and
kwargs in tags

The overall rules are::

    arg          :  expr

    arg_list     :  arg
                 |  arg_list COMMA arg

    expr         :  literal
                 |  expr DOT NAME

                 |  expr PLUS expr
                 |  expr MINUS expr
                 |  expr MUL expr
                 |  expr DIV expr
                 |  expr MOD expr

                 |  expr AND expr
                 |  expr OR expr

                 |  expr EQUAL expr
                 |  expr NEQUAL expr
                 |  expr LT expr
                 |  expr LTE expr
                 |  expr GT expr
                 |  expr GTE expr
                 |  expr IN expr
                 |  expr NOTIN expr
                 |  expr ISNOT expr
                 |  expr IS expr

                 |  expr filter
                 |  LPAREN expr RPAREN
                 |  expr LSQB expr RSQB
                 |  expr LPAREN RPAREN
                 |  expr LPAREN arg_list RPAREN
                 |  expr LPAREN kwarg_list RPAREN
                 |  expr LPAREN arg_list COMMA kwarg_list RPAREN

    filter       :  PIPE lookup_name
                 |  PIPE lookup_name COLON literal
                 |  PIPE lookup_name LPAREN RPAREN
                 |  PIPE lookup_name LPAREN arg_list RPAREN
                 |  PIPE lookup_name LPAREN kwarg_list RPAREN
                 |  PIPE lookup_name LPAREN arg_list COMMA kwarg_list RPAREN

    kwarg        :  NAME ASSIGN expr

    kwarg_list   :  kwarg
                 |  kwarg_list COMMA kwarg

    literal      :  name
                 |  number
                 |  string

    lookup_name  :  NAME
                 |  lookup_name DOT NAME

    name         :  NAME

    number       :  NUMBER

    string       :  STRING

"""

fpg.precedence = [
    ('left', ['COMMA']),
    ('right', ['ASSIGN']),
    ('left', ['PIPE']),
    ('left', ['AND', 'OR']),
    ('left', ['EQUAL', 'NEQUAL',
              'LT', 'LTE', 'GT', 'GTE',
              'IN', 'NOTIN',
              'ISNOT', 'IS']),
    ('left', ['PLUS', 'MINUS']),
    ('left', ['MUL', 'DIV', 'MOD']),
    ('left', ['LSQB', 'RSQB']),
    ('left', ['DOT']),
    ('left', ['LPAREN', 'RPAREN']),
]


@production(fpg, 'arg : expr')
def fpg_arg_expr(p):
    return p[0]


@production(fpg, 'arg_list : arg')
def fpg_arg_list_arg(p):
    return p


@production(fpg, 'arg_list : arg_list COMMA arg')
def fpg_arg_list_append(p):
    arg_list, _, arg = p
    arg_list.append(arg)
    return arg_list


@production(fpg, 'expr : literal')
def fpg_expr_literal(p):
    return p[0]


@production(fpg, 'expr : expr DOT NAME')
def fpg_expr_DOT_NAME(p):
    lterm, _, rterm = p
    return ast.Attribute(
        value=lterm,
        attr=rterm.getstr(),
        ctx=ast.Load(),
    )


_binop_mapping = {
    'PLUS': ast.Add,
    'MINUS': ast.Sub,
    'MUL': ast.Mult,
    'DIV': ast.Div,
    'MOD': ast.Mod,
}


@production(fpg,
            'expr : expr PLUS expr',
            'expr : expr MINUS expr',
            'expr : expr MUL expr',
            'expr : expr DIV expr',
            'expr : expr MOD expr')
def fpg_expr_binop(p):
    lterm, op, rterm = p
    operator = _binop_mapping[op.gettokentype()]
    return ast.BinOp(left=lterm, op=operator(), right=rterm)


_boolop_mapping = {
    'AND': ast.And,
    'OR': ast.Or,
}


@production(fpg,
            'expr : expr AND expr',
            'expr : expr OR expr')
def fpg_expr_boolop(p):
    lterm, op, rterm = p
    operator = _boolop_mapping[op.gettokentype()]
    return ast.BoolOp(op=operator(), values=[lterm, rterm])


_cmpop_mapping = {
    'EQUAL': ast.Eq,
    'NEQUAL': ast.NotEq,
    'LT': ast.Lt,
    'LTE': ast.LtE,
    'GT': ast.Gt,
    'GTE': ast.GtE,
    'IN': ast.In,
    'NOTIN': ast.NotIn,
    'ISNOT': ast.IsNot,
    'IS': ast.Is,
}


@production(fpg,
            'expr : expr EQUAL expr',
            'expr : expr NEQUAL expr',
            'expr : expr LTE expr',
            'expr : expr LT expr',
            'expr : expr GTE expr',
            'expr : expr GT expr',
            'expr : expr IN expr',
            'expr : expr NOTIN expr',
            'expr : expr ISNOT expr',
            'expr : expr IS expr')
def expr_cmpop(p):
    lterm, op, rterm = p
    operator = _cmpop_mapping[op.gettokentype()]
    return ast.Compare(left=lterm, ops=[operator()], comparators=[rterm])


@production(fpg, 'expr : expr filter')
def fpg_expr_filter(p):
    arg, (filter, args, kwargs) = p
    return build_call(filter, [arg] + args, kwargs)


@production(fpg, 'expr : LPAREN expr RPAREN')
def fpg_expr_binop_paren(p):
    return p[1]


@production(fpg, 'expr : expr LSQB expr RSQB')
def fpg_expr_SUBSCRIPT(p):
    src, _, subscript, _ = p
    return ast.Subscript(
        value=src,
        slice=ast.Index(value=subscript, ctx=ast.Load()),
        ctx=ast.Load(),
    )


@production(fpg, 'expr : expr LPAREN RPAREN')
def fpg_expr_empty_call(p):
    func, _, _ = p
    return build_call(func)


@production(fpg, 'expr : expr LPAREN arg_list RPAREN')
def fpg_expr_args_call(p):
    func, _, args, _ = p
    return build_call(func, args)


@production(fpg, 'expr : expr LPAREN kwarg_list RPAREN')
def fpg_expr_kwargs_call(p):
    func, _, kwargs, _ = p
    return build_call(func, kwargs=kwargs)


@production(fpg, 'expr : expr LPAREN arg_list COMMA kwarg_list RPAREN')
def fpg_expr_full_call(p):
    func, _, args, _, kwargs, _ = p
    return build_call(func, args, kwargs)


@production(fpg, 'filter : PIPE lookup_name COLON literal')
def fpg_filter_colon_arg(p):
    _, filt, _, arg = p
    filter_name = get_lookup_name(filt)
    filter_func = get_filter_func(filter_name)
    return filter_func, [arg], []


@production(fpg, 'filter : PIPE lookup_name')
def fpg_filter_pipe_lookup_name(p):
    filter_name = get_lookup_name(p[1])
    filter_func = get_filter_func(filter_name)
    return filter_func, [], []


@production(fpg, 'filter : PIPE lookup_name LPAREN RPAREN')
def fpg_filter_pipe_lookup_empty_call(p):
    filter_name = get_lookup_name(p[1])
    filter_func = get_filter_func(filter_name)
    return filter_func, [], []


@production(fpg, 'filter : PIPE lookup_name LPAREN arg_list RPAREN')
def fpg_filter_pipe_lookup_args_call(p):
    _, filter, _, args, _ = p
    filter_name = get_lookup_name(filter)
    filter_func = get_filter_func(filter_name)
    return filter_func, args, []


@production(fpg, 'filter : PIPE lookup_name LPAREN kwarg_list RPAREN')
def fpg_filter_pipe_lookup_kwargs_call(p):
    _, filter, _, kwargs, _ = p
    filter_name = get_lookup_name(filter)
    filter_func = get_filter_func(filter_name)
    return filter_func, [], kwargs


@production(fpg, 'filter : PIPE lookup_name LPAREN arg_list COMMA kwarg_list RPAREN')
def fpg_filter_pipe_lookup_full_call(p):
    _, filter, _, args, _, kwargs, _ = p
    filter_name = get_lookup_name(filter)
    filter_func = get_filter_func(filter_name)
    return filter_func, args, kwargs


@production(fpg, 'kwarg : NAME ASSIGN expr')
def fpg_kwarg_assignment(p):
    name, _, expr = p
    return ast.keyword(arg=name.getstr(), value=expr)


@production(fpg, 'kwarg_list : kwarg')
def fpg_kwarg_list_kwarg(p):
    return p


@production(fpg, 'kwarg_list : kwarg_list COMMA kwarg')
def fpg_kwarg_list_append(p):
    kwarg_list, _, kwarg = p
    kwarg_list.append(kwarg)
    return kwarg_list


@production(fpg,
            'literal : name',
            'literal : number',
            'literal : string')
def fpg_literal(p):
    return p[0]


@production(fpg, 'lookup_name : NAME')
def fpg_lookup_name_NAME(p):
    return [ast.Str(s=p[0].getstr())]


@production(fpg, 'lookup_name : lookup_name DOT NAME')
def fpg_lookup_name_append(p):
    lookup_name, _, name = p
    lookup_name.append(ast.Str(s=name.getstr()))
    return lookup_name


@production(fpg, 'name : NAME')
def fpg_name_NAME(p):
    return ast.Subscript(
        value=ast.Name(id='context', ctx=ast.Load()),
        slice=ast.Index(value=ast.Str(s=p[0].getstr()), ctx=ast.Load()),
        ctx=ast.Load(),
    )


@production(fpg, 'number : NUMBER')
def fpg_number_NUMBER(p):
    number = p[0].getstr()
    if '.' in number or 'e' in number or 'E' in number:
        cast = float
    else:
        cast = int
    return ast.Num(n=cast(number))


@production(fpg, 'string : STRING')
def fpg_string_STRING(p):
    return ast.Str(s=p[0].getstr()[1:-1])


@fpg.error
def fpg_error(token):
    raise ValueError('Unexpected token: %r' % token)
