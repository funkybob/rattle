
import rply

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

# Operators
lg.add('ASSIGN', r'=')
lg.add('PLUS', r'\+')
lg.add('MINUS', r'-')
lg.add('MUL', r'\*')
lg.add('DIV', r'/')
lg.add('MOD', r'%')



