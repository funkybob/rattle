rattle
======

Python templating tool.

Plan
----

The plan is "simple".  Utilise the source tokeniser I wrote for
django-contemplation, then use the ``tokenize`` and ``ast`` modules to convert
templates into "native" code.

Each Token will be built into native code using AST and ast.compile.

Argument expressions will use the tokenizer to provide rapid, reliable parsing.

Tags will mostly use the same basic format:

    {% tagname [args]* [kwargs]* as ? %}

so the engine can parse it itself.
