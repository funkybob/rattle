import rply


slg = rply.LexerGenerator()

slg.add('VS', r'\{\{\s*')
slg.add('VE', r'\s*\}\}')

slg.add('TS', r'\{%')
slg.add('TE', r'\s*%\}')

slg.add('CS', r'\{#\s*')
slg.add('CE', r'\s*#\}')

# Matches everything that is ...
# * not preceded by a start token (any of ``{{``, ``{%`` or ``{#``) AND
# * is followed by any of:
#   * a start token (matches right before a tag/var/comment starts)
#   * a end token (any of ``}}``, ``%}`` or ``#}``) (everything inside a tag
#     except the tag name)
#   * End of string
slg.add('CONTENT', r'(?<!(\{[{%#])).*?(?=(\{[{%#])|(\s*[#%}]\})|$)')

slg.add('IF', r'\s*if\s+')
slg.add('ENDIF', r'\s*endif\s+')
slg.add('ELSE', r'\s*else\s+')

slg.add('FOR', r'\s*for\s+')
slg.add('ENDFOR', r'\s*endfor\s+')
slg.add('EMPTY', r'\s*empty\s+')
