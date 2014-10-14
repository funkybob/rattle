from rattle.template import library

@library.register_filter
def join(value, sep):
    return sep.join(value)


@library.register_filter
def lcjoin(value, sep, lower=False):
    if lower:
        return sep.join(map(str.lower, value))
    return sep.join(value)


@library.register_filter
def quote(value):
    return '"%s"' % value


@library.register_filter
def squote(value):
    return "'%s'" % value
