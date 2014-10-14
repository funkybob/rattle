from rattle.template import library


def quote(value):
    return '"%s"' % value

library.register_filter(quote)


def squote(value):
    return "'%s'" % value

library.register_filter(squote)
