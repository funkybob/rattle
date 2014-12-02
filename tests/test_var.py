from rattle import PY3, library

import tests.filters  # noqa: necessary to register test filters
from tests.utils import Mock, TemplateTestCase


def bye_filter(arg1):
    return 'Bye %s!' % arg1


def hello_filter(arg1):
    return 'Hello %s!' % arg1


class LiteralSyntaxTest(TemplateTestCase):

    def test_render_plaintext(self):
        self.assertRendered("Hello world!", 'Hello world!')

    def test_render_plaintext_literal_literal(self):
        self.assertRendered("{{ 'Hello '}}{{ 'world!' }}", 'Hello world!')

    def test_render_plaintext_literal_plaintext(self):
        self.assertRendered("Hello {{ 'world' }}!", 'Hello world!')

    def test_render_literal_plaintext(self):
        self.assertRendered("{{ 'Hello' }} world!", 'Hello world!')

    def test_renderStringLiteral(self):
        self.assertRendered("{{ 'hello' }}", 'hello')

    def test_renderNumLiteral(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ 23 }}', '23'),

            ('{{ 2.3 }}', '2.3'),
            ('{{ 12.34 }}', '12.34'),
            ('{{ 12e1 }}', '120.0'),
            ('{{ 12E1 }}', '120.0'),
            ('{{ 12e-1 }}', '1.2'),
            ('{{ 12E-1 }}', '1.2'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)


class VariableSyntaxTest(TemplateTestCase):

    def test_direct(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ a }}', {'a': 'yes'}, 'yes'),
        )
        for src, ctx, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_index(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ a[1] }}', {'a': ['yes', 'no']}, 'no'),
            ('{{ a["b"] }}', {'a': {'b': 'yes'}}, 'yes'),
            ('{{ a[c] }}', {'a': {'b': 'yes', 'c': 'no'}, 'c': 'b'}, 'yes'),
        )
        for src, ctx, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_attribute(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ a.b }}', {'a': Mock(b=1)}, '1'),
            ('{{ a.b.c }}', {'a': Mock(b=Mock(c=1))}, '1'),
            ('{{ a["b"].c }}', {'a': {'b': Mock(c=1)}}, '1'),
        )
        for src, ctx, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_function(self):

        def f_arg(arg1):
            return '%s' % (arg1)

        def f_args(arg1, arg2):
            return '%s %s' % (arg1, arg2)

        # A list of (template, context, output)
        TESTS = (
            ('{{ a(1) }}', {'a': lambda x: x}, '1'),
            ('{{ a(b,1) }}', {'a': lambda x, y: x + y, 'b': 6}, '7'),

            # args
            ('{{ a(1) }}', {'a': f_arg}, '1'),
            ('{{ a(1, 2) }}', {'a': f_args}, '1 2'),

            # kwargs
            ('{{ a(arg1=1) }}', {'a': f_arg}, '1'),
            ('{{ a(arg1=1, arg2=2) }}', {'a': f_args}, '1 2'),

            # args + kwargs
            ('{{ a(1, arg2=2) }}', {'a': f_args}, '1 2'),

            # with vars
            ('{{ a(x) }}', {'a': f_arg, 'x': 1}, '1'),
            ('{{ a(x, y) }}', {'a': f_args, 'x': 1, 'y': 2}, '1 2'),
            ('{{ a(arg1=x) }}', {'a': f_arg, 'x': 1}, '1'),
            ('{{ a(arg1=x, arg2=y) }}', {'a': f_args, 'x': 1, 'y': 2}, '1 2'),
            ('{{ a(x, arg2=y) }}', {'a': f_args, 'x': 1, 'y': 2}, '1 2'),
        )
        for src, ctx, expect in TESTS:
            self.assertRendered(src, expect, ctx)


class FilterLookupTest(TemplateTestCase):

    def setUp(self):
        library.register_filter(bye_filter)
        library.register_filter(hello_filter)

    def tearDown(self):
        library.unregister_filter('tests.test_var.bye_filter')
        library.unregister_filter('tests.test_var.hello_filter')

    def test_pipe_precendence(self):
        # A list of (template, context, output)
        TESTS = (
            # ASSIGN
            ('{{ "foo"|join(sep="::"|join(",")) }}', {}, 'f:,:o:,:o'),
            # BinOp
            ('{{ 21 + 21|quote }}', {}, '&quot;42&quot;'),
            ('{{ 21 - 21|quote }}', {}, '&quot;0&quot;'),
            ('{{ 21 * 21|quote }}', {}, '&quot;441&quot;'),
            ('{{ 21 / 21|quote }}',
             {},
             '&quot;1.0&quot;' if PY3 else '&quot;1&quot;'),
            # LSQB / RSQB
            ('{{ a[1]|join(",") }}', {'a': ['yes', 'no']}, 'n,o'),
        )
        for src, ctx, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_single_filter(self):
        ctx = {'hello_filter': hello_filter}
        TESTS = (
            ('{{ 42|hello_filter }}', 'Hello 42!'),
            ('{{ 13.37|hello_filter }}', 'Hello 13.37!'),
            ('{{ "world"|hello_filter }}', 'Hello world!'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_multiple_filters(self):
        ctx = {'hello_filter': hello_filter}
        TESTS = (
            ('{{ 42|bye_filter|hello_filter }}', 'Hello Bye 42!!'),
            ('{{ 13.37|bye_filter|hello_filter }}', 'Hello Bye 13.37!!'),
            ('{{ "world"|hello_filter|bye_filter }}', 'Bye Hello world!!'),
            ('{{ "world"|bye_filter|hello_filter }}', 'Hello Bye world!!'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_single_filter_short_name(self):
        TESTS = (
            ('{{ 42|quote }}', '&quot;42&quot;'),
            ('{{ 13.37|quote }}', '&quot;13.37&quot;'),
            ('{{ "world"|quote }}', '&quot;world&quot;'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)

    def test_single_filter_full_name(self):
        TESTS = (
            ('{{ 42|tests.filters.quote }}', '&quot;42&quot;'),
            ('{{ 13.37|tests.filters.quote }}', '&quot;13.37&quot;'),
            ('{{ "world"|tests.filters.quote }}', '&quot;world&quot;'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)

    def test_multiple_filter_full_name(self):
        TESTS = (
            ('{{ 42|tests.filters.quote|tests.filters.squote }}',
             '&#39;&quot;42&quot;&#39;'),
            ('{{ 13.37|tests.filters.quote|tests.filters.squote }}',
             '&#39;&quot;13.37&quot;&#39;'),
            ('{{ "world"|tests.filters.quote|tests.filters.squote }}',
             '&#39;&quot;world&quot;&#39;'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)

    def test_multiple_filter_short_name(self):
        TESTS = (
            ('{{ 42|quote|squote }}', '&#39;&quot;42&quot;&#39;'),
            ('{{ 13.37|quote|squote }}', '&#39;&quot;13.37&quot;&#39;'),
            ('{{ "world"|quote|squote }}', '&#39;&quot;world&quot;&#39;'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)

    def test_full_name_short_name(self):
        TESTS = (
            ('{{ 42|tests.filters.quote|squote }}',
             '&#39;&quot;42&quot;&#39;'),
            ('{{ 13.37|tests.filters.quote|squote }}',
             '&#39;&quot;13.37&quot;&#39;'),
            ('{{ "world"|tests.filters.quote|squote }}',
             '&#39;&quot;world&quot;&#39;'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)

    def test_short_name_full_name(self):
        TESTS = (
            ('{{ 42|quote|tests.filters.squote }}',
             '&#39;&quot;42&quot;&#39;'),
            ('{{ 13.37|quote|tests.filters.squote }}',
             '&#39;&quot;13.37&quot;&#39;'),
            ('{{ "world"|quote|tests.filters.squote }}',
             '&#39;&quot;world&quot;&#39;'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)

    def test_empty_call(self):
        TESTS = (
            ('{{ "world"|quote() }}', '&quot;world&quot;'),
            ('{{ "world"|tests.filters.quote() }}', '&quot;world&quot;'),
            ('{{ "world"|tests.filters.quote()|tests.filters.squote }}',
             '&#39;&quot;world&quot;&#39;'),
            ('{{ "world"|quote()|squote }}', '&#39;&quot;world&quot;&#39;'),
            ('{{ "world"|tests.filters.quote()|squote }}',
             '&#39;&quot;world&quot;&#39;'),
            ('{{ "world"|quote()|tests.filters.squote }}',
             '&#39;&quot;world&quot;&#39;'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)

    def test_args_call(self):
        ctx = {'a': ['A', 'B']}
        TESTS = (
            ('{{ a|join(",") }}', 'A,B'),
            ('{{ a|tests.filters.join(",") }}', 'A,B'),
            ('{{ a|join(",")|join(":") }}', 'A:,:B'),
            ('{{ a|tests.filters.join(",")|tests.filters.join(":") }}',
             'A:,:B'),
            ('{{ a|tests.filters.join(",")|join(":") }}',
             'A:,:B'),
            ('{{ a|join(",")|tests.filters.join(":") }}',
             'A:,:B'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_args_call_legacy(self):
        TESTS = (
            ('{{ a|join:"," }}', {'a': ['1', '2', '3']}, '1,2,3'),
        )
        for src, ctx, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_kwargs_call(self):
        ctx = {'a': ['A', 'B']}
        TESTS = (
            ('{{ a|join(sep=",") }}', 'A,B'),
            ('{{ a|tests.filters.join(sep=",") }}', 'A,B'),
            ('{{ a|join(sep=",")|join(sep=":") }}', 'A:,:B'),
            ('{{ a|tests.filters.join(sep=",")|tests.filters.join(sep=":") }}',
             'A:,:B'),
            ('{{ a|tests.filters.join(sep=",")|join(sep=":") }}',
             'A:,:B'),
            ('{{ a|join(sep=",")|tests.filters.join(sep=":") }}',
             'A:,:B'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_full_call_args(self):
        ctx = {'a': ['A', 'B']}
        TESTS = (
            ('{{ a|lcjoin(",", True) }}', 'a,b'),
            ('{{ a|tests.filters.lcjoin(",", True) }}',
             'a,b'),
            ('{{ a|lcjoin(",", True)|lcjoin(":", True) }}',
             'a:,:b'),
            ('{{ a|tests.filters.lcjoin(",", True)|tests.filters.lcjoin(":", True) }}',
             'a:,:b'),
            ('{{ a|tests.filters.lcjoin(",", True)|lcjoin(":", True) }}',
             'a:,:b'),
            ('{{ a|lcjoin(",", True)|tests.filters.lcjoin(":", True) }}',
             'a:,:b'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_full_call_kwargs(self):
        ctx = {'a': ['A', 'B']}
        TESTS = (
            ('{{ a|lcjoin(sep=",", lower=True) }}', 'a,b'),
            ('{{ a|tests.filters.lcjoin(sep=",", lower=True) }}',
             'a,b'),
            ('{{ a|lcjoin(sep=",", lower=True)|lcjoin(sep=":", lower=True) }}',
             'a:,:b'),
            (('{{ a|tests.filters.lcjoin(sep=",", lower=True)'
              '|tests.filters.lcjoin(sep=":", lower=True) }}'),
             'a:,:b'),
            (('{{ a|tests.filters.lcjoin(sep=",", lower=True)'
              '|lcjoin(sep=":", lower=True) }}'),
             'a:,:b'),
            (('{{ a|lcjoin(sep=",", lower=True)'
              '|tests.filters.lcjoin(sep=":", lower=True) }}'),
             'a:,:b'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_full_call_mixed(self):
        ctx = {'a': ['A', 'B']}
        TESTS = (
            ('{{ a|lcjoin(",", lower=True) }}', 'a,b'),
            ('{{ a|tests.filters.lcjoin(",", lower=True) }}',
             'a,b'),
            ('{{ a|lcjoin(",", lower=True)|lcjoin(":", lower=True) }}',
             'a:,:b'),
            (('{{ a|tests.filters.lcjoin(",", lower=True)'
              '|tests.filters.lcjoin(":", lower=True) }}'),
             'a:,:b'),
            (('{{ a|tests.filters.lcjoin(",", lower=True)'
              '|lcjoin(":", lower=True) }}'),
             'a:,:b'),
            (('{{ a|lcjoin(",", lower=True)'
              '|tests.filters.lcjoin(":", lower=True) }}'),
             'a:,:b'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect, ctx)


class BinaryOperatorsTest(TemplateTestCase):

    def test_add(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ 1 + 2 }}', {}, '3'),
            ('{{ a + 2 }}', {'a': 1}, '3'),
            ('{{ 1 + b }}', {'b': 2}, '3'),
            ('{{ a + b }}', {'a': 1, 'b': 2}, '3'),
            ('{{ a + a }}', {'a': 1}, '2'),

            ('{{ 1.8 + 2.9 }}', {}, '4.7'),
            ('{{ a + 2.9 }}', {'a': 1.8}, '4.7'),
            ('{{ 1.8 + b }}', {'b': 2.9}, '4.7'),
            ('{{ a + b }}', {'a': 1.8, 'b': 2.9}, '4.7'),
            ('{{ a + a }}', {'a': 1.8}, '3.6'),
        )
        for src, ctx, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_sub(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ 2 - 1 }}', {}, '1'),
            ('{{ a - 1 }}', {'a': 2}, '1'),
            ('{{ 2 - b }}', {'b': 1}, '1'),
            ('{{ a - b }}', {'a': 2, 'b': 1}, '1'),
            ('{{ a - a }}', {'a': 2}, '0'),

            ('{{ 2.9 - 1.7 }}', {}, '1.2'),
            ('{{ a - 1.7 }}', {'a': 2.9}, '1.2'),
            ('{{ 2.9 - b }}', {'b': 1.7}, '1.2'),
            ('{{ a - b }}', {'a': 2.9, 'b': 1.7}, '1.2'),
            ('{{ a - a }}', {'a': 2.9}, '0.0'),
        )
        for src, ctx, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_mult(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ 2 * 3 }}', {}, '6'),
            ('{{ a * 3 }}', {'a': 2}, '6'),
            ('{{ 2 * b }}', {'b': 3}, '6'),
            ('{{ a * b }}', {'a': 2, 'b': 3}, '6'),
            ('{{ a * a }}', {'a': 2}, '4'),

            ('{{ 1.5 * 3.9 }}', {}, '5.85'),
            ('{{ a * 3.9 }}', {'a': 1.5}, '5.85'),
            ('{{ 1.5 * b }}', {'b': 3.9}, '5.85'),
            ('{{ a * b }}', {'a': 1.5, 'b': 3.9}, '5.85'),
            ('{{ a * a }}', {'a': 1.5}, '2.25'),
        )
        for src, ctx, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_div(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ 6 / 3 }}', {}, '2.0' if PY3 else '2'),
            ('{{ a / 3 }}', {'a': 6}, '2.0' if PY3 else '2'),
            ('{{ 6 / b }}', {'b': 3}, '2.0' if PY3 else '2'),
            ('{{ a / b }}', {'a': 6, 'b': 3}, '2.0' if PY3 else '2'),
            ('{{ a / a }}', {'a': 6}, '1.0' if PY3 else '1'),

            ('{{ 3.5 / 1.4 }}', {}, '2.5'),
            ('{{ a / 1.4 }}', {'a': 3.5}, '2.5'),
            ('{{ 3.5 / b }}', {'b': 1.4}, '2.5'),
            ('{{ a / b }}', {'a': 3.5, 'b': 1.4}, '2.5'),
            ('{{ a / a }}', {'a': 3.5}, '1.0'),
        )
        for src, ctx, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_mod(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ 6 % 4 }}', {}, '2'),
            ('{{ a % 4 }}', {'a': 6}, '2'),
            ('{{ 6 % b }}', {'b': 4}, '2'),
            ('{{ a % b }}', {'a': 6, 'b': 4}, '2'),
            ('{{ a % a }}', {'a': 6}, '0'),

            ('{{ 2.0 % 1.2 }}', {}, '0.8'),
            ('{{ a % 1.2 }}', {'a': 2.0}, '0.8'),
            ('{{ 2.0 % b }}', {'b': 1.2}, '0.8'),
            ('{{ a % b }}', {'a': 2.0, 'b': 1.2}, '0.8'),
            ('{{ a % a }}', {'a': 2.0}, '0.0'),
        )
        for src, ctx, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_mixed(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ 1 + 2 - 3 + 4 }}', {}, '4'),
            ('{{ 1 + 2 * 3 }}', {}, '7'),
            ('{{ 1 + (2 * 3) }}', {}, '7'),
            ('{{ (1 + 2) * 3 }}', {}, '9'),
            ('{{ a(b + 3, 4) }}', {'a': lambda x, y: x * y, 'b': 2}, '20'),
            ('{{ a[0] + a[1] * a[2] }}', {'a': [2, 3, 4]}, '14'),
            ('{{ a[0].x + a[1].x * b.y[0] }}',
             {'a': [Mock(x=2), Mock(x=3)], 'b': Mock(y=[4])},
             '14'),
            ('{{ (a[0].x + a[1].x) * b.y[0] }}',
             {'a': [Mock(x=2), Mock(x=3)], 'b': Mock(y=[4])},
             '20'),
        )
        for src, ctx, expect in TESTS:
            self.assertRendered(src, expect, ctx)


class ComparatorsTest(TemplateTestCase):

    def test_equal(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ 1==0 }}', 'False'),
            ('{{ 1==1 }}', 'True'),
            ('{{ 1==2 }}', 'False'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)

    def test_nequal(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ 1!=0 }}', 'True'),
            ('{{ 1!=1 }}', 'False'),
            ('{{ 1!=2 }}', 'True'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)

    def test_less_equal(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ 1<=0 }}', 'False'),
            ('{{ 1<=1 }}', 'True'),
            ('{{ 1<=2 }}', 'True'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)

    def test_less(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ 1<0 }}', 'False'),
            ('{{ 1<1 }}', 'False'),
            ('{{ 1<2 }}', 'True'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)

    def test_greater_equal(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ 0>=1 }}', 'False'),
            ('{{ 1>=1 }}', 'True'),
            ('{{ 2>=1 }}', 'True'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)

    def test_greater(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ 0>1 }}', 'False'),
            ('{{ 1>1 }}', 'False'),
            ('{{ 2>1 }}', 'True'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)

    def test_in(self):
        TESTS = (
            ('{{ 0 in a }}', {'a': [1, 2]}, 'False'),
            ('{{ 1 in a }}', {'a': [1, 2]}, 'True'),
        )
        for src, ctx, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_notin(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ 0 not in a }}', {'a': [1, 2]}, 'True'),
            ('{{ 1 not in a }}', {'a': [1, 2]}, 'False'),
        )
        for src, ctx, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_isnot(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ a is not a }}', {'a': [1, 2], 'b': [3, 4]}, 'False'),
            ('{{ a is not b }}', {'a': [1, 2], 'b': [3, 4]}, 'True'),
        )
        for src, ctx, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_is(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ a is a }}', {'a': [1, 2], 'b': [3, 4]}, 'True'),
            ('{{ a is b }}', {'a': [1, 2], 'b': [3, 4]}, 'False'),
        )
        for src, ctx, expect in TESTS:
            self.assertRendered(src, expect, ctx)
