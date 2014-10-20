import ast

import rply

from .filter import fpg
from ..lexer.filter import flg
from ..lexer.structure import slg
from ..utils.parser import (build_call, build_str_join, build_str_list_comp,
    update_source_pos)


#: structure parser generator
#:
#: Useed to tokenize and split the template at ``{{``, ``{%``, ``{#``, ``}}``,
#: ``%}`` and ``#}``
spg = rply.ParserGenerator(
    [rule.name for rule in slg.rules],
    precedence=[]
)


"""

doc  :  CONTENT
     |  var
     |  tag
     |  comment
     |  doc CONTENT
     |  doc var
     |  doc tag
     |  doc comment

var  :  VS CONTENT VE

tag  :  if

if   :  TS IF CONTENT TE doc TS ENDIF TE
     |  TS IF CONTENT TE doc TS ELSE TE doc TS ENDIF TE

comment : CS CONTENT CE

"""


@spg.production('doc : CONTENT')
def doc__CONTENT(p):
    c = p[0]
    return [update_source_pos(ast.Str(s=c.getstr()), c)]


@spg.production('doc : var')
@spg.production('doc : tag')
@spg.production('doc : comment')
def doc__parsed(p):
    return p


@spg.production('doc : doc CONTENT')
def doc__doc_CONTENT(p):
    doc, content = p
    doc.append(update_source_pos(ast.Str(s=content.getstr()), content))
    return doc


@spg.production('doc : doc var')
def doc__doc_var(p):
    doc, var = p
    doc.append(var)
    return doc


@spg.production('doc : doc tag')
def doc__doc_tag(p):
    doc, var = p
    doc.append(var)
    return doc


@spg.production('doc : doc comment')
def doc__doc_comment(p):
    doc, _ = p
    return doc


@spg.production('var : VS CONTENT VE')
def var__varstart_CONTENT_varend(p):
    filter_lexer = flg.build()
    filter_parser = fpg.build()
    content = filter_parser.parse(filter_lexer.lex(p[1].getstr()))
    return build_call(
        func=ast.Name(id='auto_escape', ctx=ast.Load()),
        args=[
            content
        ]
    )


@spg.production('tag : if')
def tag_if(p):
    return p[0]


@spg.production('if : TS IF CONTENT TE doc TS ENDIF TE')
def tag_if_impl(p):
    ts, _, condition, _, body, _, _, _ = p
    filter_lexer = flg.build()
    filter_parser = fpg.build()
    test = filter_parser.parse(filter_lexer.lex(condition.getstr()))
    return update_source_pos(ast.IfExp(
        test=test,
        body=build_str_join(build_str_list_comp(body)),
        orelse=ast.Str(s='')
    ), ts)


@spg.production('if : TS IF CONTENT TE doc TS ELSE TE doc TS ENDIF TE')
def tag_if_else_impl(p):
    ts, _, condition, _, body, _, _, _, orelse, _, _, _ = p
    filter_lexer = flg.build()
    filter_parser = fpg.build()
    test = filter_parser.parse(filter_lexer.lex(condition.getstr()))
    return update_source_pos(ast.IfExp(
        test=test,
        body=build_str_join(build_str_list_comp(body)),
        orelse=build_str_join(build_str_list_comp(orelse)),
    ), ts)


@spg.production('comment : CS CONTENT CE')
def comment(p):
    return ast.Str(s='')


@spg.error
def error(token):
    raise ValueError('Unexpected token: %r' % token)
