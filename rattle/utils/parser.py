import ast

from rattle import PY3


class ParserState(object):
    """
    Used to keep state information during template parsing, e.g. current block.
    """

    def __init__(self):
        self.blocks = []

    def append_to_block(self, value):
        """
        Appends the given value to the body of the currently active block
        function.

        :param value: A :class:`ast.stmt` node.
        """
        self.blocks[-1].body.append(value)


def production(generator, *rules):
    """
    Wrapper around :meth:`rply.ParserGenerator.production` to patch the rules
    into the production's docstring.

    :param generator: An instance of a :class:`rply.ParserGenerator`.
    :param rules: The rules matching this production.
    """

    def wrapper(func):
        docstring = [func.__doc__, '\n'] if func.__doc__ else []
        docstring.append("This production is used for the following rules::\n")

        for rule in rules:
            generator.production(rule)(func)
            docstring.append("    " + rule)

        docstring.append('\n.')
        func.__doc__ = '\n'.join(docstring)
        return func
    return wrapper


def build_call(func, args=[], kwargs=[]):
    """
    Constructs a :class:`ast.Call` node that calls the given function ``func``
    with the arguments ``args`` and keyword arguments ``kwargs``.

    This is equivalent to::

        func(*args, **kwargs)

    :param func: An AST that, when evaluated, returns a function.
    :param args: The positional arguments passed to the function.
    :param kwags: The keyword arguments passed to the function.
    :returns: Calls the function with the provided args and kwargs.
    :rtype: :class:`ast.Call`
    """
    return ast.Call(
        func=func,
        args=args,
        keywords=kwargs,
        starargs=None,
        kwargs=None
    )


def build_class():
    """
    Constructs a :class:`ast.ClassDef` node that wraps the entire template
    file. The class will have an entry function ``root`` with:

    .. function:: root(context)

        Starts the template parsing with the given context.

        :returns: Returns a generator of strings that can be joined to the
            rendered template.

    :returns: a 2-tuple with the class and the entry function
    """
    args = {}
    if PY3:
        args.update({
            'args': [
                ast.arg(arg='self', annotation=None),
                ast.arg(arg='context', annotation=None),
            ],
            'kwonlyargs': [],
            'kw_defaults': [],
        })
    else:
        args['args'] = [
            ast.Name(id='self', ctx=ast.Param()),
            ast.Name(id='context', ctx=ast.Param())
        ]
    root_func = ast.FunctionDef(
        name='root',
        args=ast.arguments(
            vararg=None,
            kwarg=None,
            defaults=[],
            **args
        ),
        body=[
            # we add an empty string to guarantee for a string and generator on
            # root level
            build_yield(ast.Str(s=''))
        ],
        decorator_list=[]
    )
    klass = ast.ClassDef(
        name='Template',
        bases=[ast.Name(id='object', ctx=ast.Load())],
        keywords=[],
        starargs=None,
        kwargs=None,
        body=[root_func],
        decorator_list=[]
    )
    return klass, root_func


def build_str_join(l):
    """
    Constructs a :class:`ast.Call` that joins all elements of ``l`` with an
    empty string (``''``).

    This is equivalent to::

        ''.join(l)

    :params list l: A string or list of strings.
    :returns: ``l`` joined by ``''``
    :rtype: str
    """
    return build_call(
        func=ast.Attribute(value=ast.Str(s=''), attr='join', ctx=ast.Load()),
        args=[l]
    )


def build_yield(value):
    """
    Constructs a :class:`ast.Yield` expression to be used in the block
    functions.

    This is equivalent to::

        yield value

    :param ast.expr value: Any AST `expr` node (e.g. :class:`ast.Str`,
        :class:`ast.Call`) that is or returns a string.
    :returns: A yield expression (``ast.Expr(ast.Yield(value))``) with the
        given value.
    :rtype: :class:`ast.Expr`
    """
    return ast.Expr(value=ast.Yield(value=value))


def get_filter_func(name):
    """
    Looks up the filter given by ``name`` in a context variable ``'filters'``.

    This is equivalent to::

        filters[name]

    :param str name: The filter name.
    :returns: A filter function.
    :rtype: ast.Subscript
    """
    return ast.Subscript(
        value=ast.Name(id='filters', ctx=ast.Load()),
        slice=ast.Index(value=name, ctx=ast.Load()),
        ctx=ast.Load(),
    )


def get_lookup_name(names):
    """
    Joins all ``names`` by ``'.'``.

    This is equivalent to::

        '.'.join(names)

    :param names: A list of one or more :class:`ast.Str` notes that will be
        joined by a dot and will be used to find a filter or tag function /
        class.
    :type names: list of :class:`ast.Str`
    :returns: ``'.'.join(names)``
    :rtype: :class:`ast.Call`
    """
    func = ast.Attribute(
        value=ast.Str(s='.'),
        attr='join',
        ctx=ast.Load()
    )
    args = [ast.List(
        elts=names,
        ctx=ast.Load()
    )]
    return build_call(func, args)


def split_tag_args_string(s):
    args = []
    current = []
    escaped, quote, squote = False, False, False
    parens = 0
    for c in s:
        if escaped:
            escaped = False
            current.append('\\')
            current.append(c)
            continue

        if c == '"':
            if not squote:
                quote = not quote
        elif c == "'":
            if not quote:
                squote = not squote
        elif c == "(":
            if not quote and not squote:
                parens += 1
        elif c == ")":
            if not quote and not squote:
                if parens <= 0:
                    raise ValueError('Closing un-open parenthesis in `%s`' % s)
                parens -= 1
        elif c == "\\":
            escaped = True
            continue
        elif c == " ":
            if not quote and not squote and parens == 0:
                if current:
                    args.append(''.join(current))
                    current = []
                continue
        current.append(c)
    if not escaped and not quote and not squote and parens == 0:
        if current:
            args.append(''.join(current))
    else:
        if quote:
            raise ValueError('Un-closed double quote in `%s`' % s)
        if squote:
            raise ValueError('Un-closed single quote in `%s`' % s)
        if parens > 0:
            raise ValueError('Un-closed parenthesis (%d still open) in `%s`' %
                             (parens, s))
        if escaped:
            raise ValueError('Un-used escaping in `%s`' % s)
    return args


def update_source_pos(node, token):
    """
    Updates the AST node ``node`` with the position information, such as line
    number and column number, from the lexer's token ``token``.
    """
    node.lineno = token.source_pos.lineno
    node.col_offset = token.source_pos.colno
    return node
