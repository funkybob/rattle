import ast


def build_call(func, args=[], kwargs=[]):
    """
    Constructs a :class:`ast.Call` node that calls the given function ``func``
    with the arguments ``args`` and keyword arguments ``kwargs``.

    :param func: An AST that, when evaluated, returns a function.
    :param args: The positional arguments passed to the function.
    :param kwags: The keyword arguments passed to the function.
    :returns: Calls the function with the provided args and kwargs.
    :rtype: ast.Call
    """
    return ast.Call(
        func=func,
        args=args,
        keywords=kwargs,
        starargs=None,
        kwargs=None
    )


def get_filter_func(name):
    """
    Looks up the filter given by ``name`` in a context variable ``'filters'``.

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

    :param names: A list of one or more :class:`ast.Str` notes that will be
        joined by a dot and will be used to find a filter or tag function /
        class.
    :type names: list of :class:`ast.Str`
    :returns: ``'.'.join(names)``
    :rtype: str
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
