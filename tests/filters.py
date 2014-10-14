from rattle.template import library


def quote(value):
    return '"%s"' % value

library.register_filter(quote)
