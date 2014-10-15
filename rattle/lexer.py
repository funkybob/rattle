import rply

"""
.. warning:

    Watch the order in which the tokens are added to the lexer! In case of
    ambiguity the *first matching* will win!
"""

lg = rply.LexerGenerator()

# Literals
lg.add('NUMBER', r'\d+(\.\d+|[eE]-?\d+)?')
lg.add('STRING', r"'.*?'|\".*?\"")
lg.add('NAME', r'[a-zA-Z_][a-zA-Z0-9_]*')

# Parenthesis
lg.add('LSQB', r'\[')
lg.add('RSQB', r'\]')
lg.add('LPAREN', r'\(')
lg.add('RPAREN', r'\)')

# Connectors
lg.add('COMMA', r',')
lg.add('DOT', r'\.')
lg.add('PIPE', r'\|')
lg.add('COLON', r':')

# Binary Operators
lg.add('ASSIGN', r'=(?!=)')  # neg. lookahead. Needed due to rply restriction
lg.add('PLUS', r'\+')
lg.add('MINUS', r'-')
lg.add('MUL', r'\*')
lg.add('DIV', r'/')
lg.add('MOD', r'%')

# Comparators
lg.add('EQUAL', r'==')
lg.add('NEQUAL', r'!=')
lg.add('LTE', r'<=')
lg.add('LT', r'<')
lg.add('GTE', r'>=')
lg.add('GT', r'>')
