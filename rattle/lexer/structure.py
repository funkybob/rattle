import rply


slg = rply.LexerGenerator()

slg.add('VS', r'\{\{\s*')
slg.add('VE', r'\s*\}\}')

slg.add('TS', r'\{%')
slg.add('TE', r'\s*%\}')

slg.add('CS', r'\{#\s*')
slg.add('CE', r'\s*#\}')

# Matches everything that is followed by {{, {%, {# or the string end, but
# doesn't consume the lookahead.
slg.add('CONTENT', r'(?<!(\{[{%#])).*?(?=(\{[{%#])|(\s*[#%}]\})|$)')

slg.add('IF', r'\s*if\s+')
slg.add('ENDIF', r'\s*endif\s+')
