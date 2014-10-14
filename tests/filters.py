from rattle.template import library


def join(value, sep):
    return sep.join(value)


def lcjoin(value, sep, lower=False):
    if lower:
        return sep.join(map(str.lower, value))
    return sep.join(value)


def quote(value):
    return '"%s"' % value


def squote(value):
    return "'%s'" % value


for f in (join, lcjoin, quote, squote):
    library.register_filter(f)
