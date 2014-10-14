from rattle.template import library

@library.register_filter
def quote(value):
    return '"%s"' % value


@library.register_filter
def squote(value):
    return "'%s'" % value
