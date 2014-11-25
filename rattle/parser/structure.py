import ast

from . import parsers
from ..lexer import lexers
from ..utils.parser import (build_call, build_class, build_yield, production,
    split_tag_args_string, update_source_pos)


spg = parsers.spg
"""
Structure parser generator.

Used to tokenize and split the template at ``{{``, ``}}``, ``{%``, ``%}``,
``{#`` and ``#}``.

The overall rules are::

    doc      :  CONTENT
             |  var
             |  tag
             |  comment
             |  doc CONTENT
             |  doc var
             |  doc tag
             |  doc comment

    var      :  VS CONTENT VE

    tag      :  if
             |  for

    if       :  TS IF CONTENT TE inner TS ENDIF TE
             |  TS IF CONTENT TE inner TS ELSE TE inner TS ENDIF TE

    for      :  TS FOR CONTENT TE inner TS ENDFOR TE
             |  TS FOR CONTENT TE inner TS ELSE TE inner TS ENDFOR TE
             |  TS FOR CONTENT TE inner TS EMPTY TE inner TS ENDFOR TE

    comment  :  CS CONTENT CE

    inner    :  CONTENT
             |  var
             |  tag
             |  comment
             |  inner CONTENT
             |  inner var
             |  inner tag
             |  inner comment

"""

spg.precedence = []


@production(spg, 'doc : CONTENT')
def doc__CONTENT(state, p):
    klass, root_func = build_class()
    state.blocks.append(root_func)
    content = p[0]
    content = update_source_pos(ast.Str(s=content.getstr()), content)
    state.append_to_block(build_yield(content))
    return klass


@production(spg,
            'doc : var',
            'doc : tag',
            'doc : comment')
def doc__parsed(state, p):
    klass, root_func = build_class()
    state.blocks.append(root_func)
    state.append_to_block(p[0])
    return klass


@production(spg, 'doc : doc CONTENT')
def doc__doc_CONTENT(state, p):
    doc, content = p
    content = update_source_pos(ast.Str(s=content.getstr()), content)
    state.append_to_block(build_yield(content))
    return doc


@production(spg,
            'doc : doc var',
            'doc : doc tag')
def doc__doc_parsed(state, p):
    doc, parsed = p
    state.append_to_block(parsed)
    return doc


@production(spg, 'doc : doc comment')
def doc__doc_comment(state, p):
    doc, _ = p
    return doc


@production(spg, 'var : VS CONTENT VE')
def var__varstart_CONTENT_varend(state, p):
    content = parsers.fp.parse(lexers.fl.lex(p[1].getstr()))
    return build_yield(build_call(
        func=ast.Name(id='auto_escape', ctx=ast.Load()),
        args=[
            update_source_pos(content, p[1])
        ]
    ))


@production(spg,
            'tag : if',
            'tag : for')
def tag(state, p):
    return p[0]


@production(spg, 'if : TS IF CONTENT TE inner TS ENDIF TE')
def if__impl(state, p):
    ts, _, condition, _, body, _, _, _ = p
    test = parsers.fp.parse(lexers.fl.lex(condition.getstr()))
    return update_source_pos(ast.If(
        test=test,
        body=body,
        orelse=[]
    ), ts)


@production(spg, 'if : TS IF CONTENT TE inner TS ELSE TE inner TS ENDIF TE')
def if__else_impl(state, p):
    ts, _, condition, _, body, _, _, _, orelse, _, _, _ = p
    test = parsers.fp.parse(lexers.fl.lex(condition.getstr()))
    return update_source_pos(ast.If(
        test=test,
        body=body,
        orelse=orelse,
    ), ts)


@production(spg, 'for : TS FOR CONTENT TE inner TS ENDFOR TE')
def for__impl(state, p):
    ts, _, args, _, body, _, _, _ = p
    target, in_, var = split_tag_args_string(args.getstr())
    if in_ != 'in':
        raise ValueError('"in" expected in for loop arguments')
    iterator = parsers.fp.parse(lexers.fl.lex(var))
    return update_source_pos(ast.For(
        target=ast.Subscript(
            value=ast.Name(id='context', ctx=ast.Load()),
            slice=ast.Index(value=ast.Str(s=target)),
            ctx=ast.Store()
        ),
        iter=iterator,
        body=body,
        orelse=[]
    ), ts)


@production(spg,
            'for : TS FOR CONTENT TE inner TS ELSE TE inner TS ENDFOR TE',
            'for : TS FOR CONTENT TE inner TS EMPTY TE inner TS ENDFOR TE')
def for__else_impl(state, p):
    ts, _, args, _, body, _, _, _, orelse, _, _, _ = p
    target, in_, var = split_tag_args_string(args.getstr())
    if in_ != 'in':
        raise ValueError('"in" expected in for loop arguments')
    iterator = parsers.fp.parse(lexers.fl.lex(var))
    return update_source_pos(ast.For(
        target=ast.Subscript(
            value=ast.Name(id='context', ctx=ast.Load()),
            slice=ast.Index(value=ast.Str(s=target)),
            ctx=ast.Store()
        ),
        iter=iterator,
        body=body,
        orelse=orelse
    ), ts)


@production(spg, 'comment : CS CONTENT CE')
def comment(state, p):
    return build_yield(ast.Str(s=''))


@production(spg, 'inner : CONTENT')
def inner__CONTENT(state, p):
    content = p[0]
    content = update_source_pos(ast.Str(s=content.getstr()), content)
    return [build_yield(content)]


@production(spg,
            'inner : var',
            'inner : tag',
            'inner : comment')
def inner__parsed(state, p):
    return p


@production(spg, 'inner : inner CONTENT')
def inner__inner_CONTENT(state, p):
    inner, content = p
    content = update_source_pos(ast.Str(s=content.getstr()), content)
    inner.append(build_yield(content))
    return inner


@production(spg,
            'inner : inner var',
            'inner : inner tag')
def inner__inner_parsed(state, p):
    inner, parsed = p
    inner.append(parsed)
    return inner


@production(spg, 'inner : inner comment')
def inner__inner_comment(state, p):
    inner, _ = p
    return inner


@spg.error
def error(token):
    raise ValueError('Unexpected token: %r' % token)
