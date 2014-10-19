import rply


flg = rply.LexerGenerator()

# Key words
flg.add('IN', r'in')
flg.add('NOTIN', r'not in')
flg.add('ISNOT', r'is not')
flg.add('IS', r'is')

# Literals
flg.add('NUMBER', r'\d+(\.\d+|[eE]-?\d+)?')
flg.add('STRING', r"'.*?'|\".*?\"")
flg.add('NAME', r'[a-zA-Z_][a-zA-Z0-9_]*')

# Parenthesis
flg.add('LSQB', r'\[')
flg.add('RSQB', r'\]')
flg.add('LPAREN', r'\(')
flg.add('RPAREN', r'\)')

# Connectors
flg.add('COMMA', r',')
flg.add('DOT', r'\.')
flg.add('PIPE', r'\|')
flg.add('COLON', r':')

# Binary Operators
flg.add('ASSIGN', r'=(?!=)')  # neg. lookahead. Needed due to rply restriction
flg.add('PLUS', r'\+')
flg.add('MINUS', r'-')
flg.add('MUL', r'\*')
flg.add('DIV', r'/')
flg.add('MOD', r'%')

# Comparators
flg.add('EQUAL', r'==')
flg.add('NEQUAL', r'!=')
flg.add('LTE', r'<=')
flg.add('LT', r'<')
flg.add('GTE', r'>=')
flg.add('GT', r'>')

flg.ignore(r'\s+')
