"""
A pretty-printing dump function for the ast module. The code was copied from the
ast.dump function and modified slightly to pretty-print.

Alex Leone (acleone ~AT~ gmail.com), 2010-01-30

From http://alexleone.blogspot.co.uk/2010/01/python-ast-pretty-printer.html

Dump function copied from
https://github.com/st3fan/pythoncodeanalysis/blob/289a5302517bacabe282c5733f85c80e95560055/core/parse.py
and PEP-8-ifight.
"""


import ast


def dump(node, annotate_fields=True, include_attributes=True, indent='  '):
    """
    Return a formatted dump of the tree in *node*. This is mainly useful for
    debugging purposes. The returned string will show the names and the values
    for fields. This makes the code impossible to evaluate, so if evaluation is
    wanted *annotate_fields* must be set to False. Attributes such as line
    numbers and column offsets are not dumped by default. If this is wanted,
    *include_attributes* can be set to True.
    """
    def _format(node, level=0):
        if isinstance(node, ast.AST):
            fields = [(a, _format(b, level)) for a, b in ast.iter_fields(node)]
            if include_attributes and node._attributes:
                fields.extend([(a, _format(getattr(node, a), level))
                               for a in node._attributes])
            return ''.join([
                node.__class__.__name__,
                '(',
                ', '.join(('%s=%s' % field for field in fields)
                          if annotate_fields
                          else (b for a, b in fields)),
                ')'])
        elif isinstance(node, list):
            lines = ['[']
            lines.extend((indent * (level + 2) + _format(x, level + 2) + ','
                         for x in node))
            if len(lines) > 1:
                lines.append(indent * (level + 1) + ']')
            else:
                lines[-1] += ']'
            return '\n'.join(lines)
        return repr(node)

    if not isinstance(node, ast.AST):
        raise TypeError('expected AST, got %r' % node.__class__.__name__)
    return _format(node)
