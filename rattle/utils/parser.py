import ast


def build_call(func, args=[], kwargs=[]):
    return ast.Call(
        func=func,
        args=args,
        keywords=kwargs,

    )


def get_lookup_name(names):
    return ast.Call(
        func=ast.Attribute(
            value=ast.Str(s='.'),
            attr='join',
            ctx=ast.Load()
        ),
        args=[
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
        ],
        keywords=[]
    )
