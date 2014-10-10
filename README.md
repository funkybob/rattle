rattle
======

Python templating tool.

Overview
--------

With all the complains of Django's Template Language being "slow", whilst most
people never use half of its built in features that prevent it being faster,
and after playing with AST for a bit, I decided to try to build a mostly
Django compatible template library, that compiled its tags with AST.

Syntax
------

    {{ var }}
    {{ var|filter }}
    {{ var|filter:arg }}
    {{ var|filter(args, kwargs=val) }}

    {# comment #}

    {% block %}
    {% block args kwargs=val %}
    {% block .... as target %}
