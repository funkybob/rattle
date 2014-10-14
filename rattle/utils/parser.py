import ast


def build_call(func, args=[], kwargs=[]):
    return ast.Call(
        func=func,
        args=args,
        keywords=kwargs,
        starargs=None,
        kwargs=None
    )


def get_filter_func(name):
    return ast.Subscript(
        value=ast.Name(id='filters', ctx=ast.Load()),
        slice=ast.Index(value=name, ctx=ast.Load()),
        ctx=ast.Load(),
    )


def get_lookup_name(names):
    func = ast.Attribute(
        value=ast.Str(s='.'),
        attr='join',
        ctx=ast.Load()
    )
    args = [
        ast.GeneratorExp(
            elt=ast.Call(
                func=ast.Name(id='str', ctx=ast.Load()),
                args=[
                    ast.Name(id='x', ctx=ast.Load())
                ],
                keywords=[]
            ),
            generators=[
                ast.comprehension(
                    target=ast.Name(id='x', ctx=ast.Store()),
                    iter=ast.List(elts=names, ctx=ast.Load()),
                    ifs=[]
                )
            ]
        )
    ]
    return build_call(func, args)
