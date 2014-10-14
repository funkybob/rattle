import sys
import unittest

from rattle import library, Template

import tests.filters  # necessary to register test filters
from tests.utils import Mock


PY3 = sys.version_info[0] == 3


def bye_filter(arg1):
    return 'Bye %s!' % arg1

def hello_filter(arg1):
    return 'Hello %s!' % arg1


class TemplateTestCase(unittest.TestCase):

    def assertRendered(self, actual, expected, template):
        try:
            self.assertEqual(actual, expected)
        except Exception as e:
            if hasattr(e, 'message'):
                standardMsg = e.message
            else:
                standardMsg = ''
            if isinstance(template, Template):
                source = template.source
            else:
                source = template
            msg = 'Failed rendering template %s:\n%s' % (source, standardMsg)
            self.fail(msg)


class LiteralSyntaxTest(TemplateTestCase):

    def test_render_plain_text(self):
        tmpl = Template("Hello {{ 'world' }}!")
        output = tmpl.render()
        self.assertRendered(output, 'Hello world!', tmpl)

    def test_renderStringLiteral(self):
        tmpl = Template("{{ 'hello' }}")
        output = tmpl.render()
        self.assertRendered(output, 'hello', tmpl)

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
            tmpl = Template(src)
            output = tmpl.render()
            self.assertRendered(output, expect, src)


class VariableSyntaxTest(TemplateTestCase):

    def test_direct(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ a }}', {'a': 'yes'}, 'yes'),
        )
        for src, context, expect in TESTS:
            tmpl = Template(src)
            output = tmpl.render(context)
            self.assertRendered(output, expect, src)

    def test_index(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ a[1] }}', {'a': ['yes', 'no']}, 'no'),
            ('{{ a["b"] }}', {'a': {'b': 'yes'}}, 'yes'),
            ('{{ a[c] }}', {'a': {'b': 'yes', 'c': 'no'}, 'c': 'b'}, 'yes'),
        )
        for src, context, expect in TESTS:
            tmpl = Template(src)
            output = tmpl.render(context)
            self.assertRendered(output, expect, src)

    def test_attribute(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ a.b }}', {'a': Mock(b=1)}, '1'),
            ('{{ a.b.c }}', {'a': Mock(b=Mock(c=1))}, '1'),
            ('{{ a["b"].c }}', {'a': {'b': Mock(c=1)}}, '1'),
        )
        for src, context, expect in TESTS:
            tmpl = Template(src)
            output = tmpl.render(context)
            self.assertRendered(output, expect, src)

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
        for src, context, expect in TESTS:
            tmpl = Template(src)
            output = tmpl.render(context)
            self.assertRendered(output, expect, src)


class FilterLookupTest(TemplateTestCase):

    def setUp(self):
        library.register_filter(bye_filter)
        library.register_filter(hello_filter)

    def tearDown(self):
        library.unregister_filter('tests.test_var.bye_filter')
        library.unregister_filter('tests.test_var.hello_filter')

    def test_single_filter(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ 42|hello_filter }}',
             {'hello_filter': hello_filter},
             'Hello 42!'),
            ('{{ 13.37|hello_filter }}',
             {'hello_filter': hello_filter},
             'Hello 13.37!'),
            ('{{ "world"|hello_filter }}',
             {'hello_filter': hello_filter},
             'Hello world!'),
        )
        for src, context, expect in TESTS:
            tmpl = Template(src)
            output = tmpl.render(context)
            self.assertRendered(output, expect, src)

    def test_multiple_filters(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ 42|bye_filter|hello_filter }}',
             {'hello_filter': hello_filter},
             'Hello Bye 42!!'),
            ('{{ 13.37|bye_filter|hello_filter }}',
             {'hello_filter': hello_filter},
             'Hello Bye 13.37!!'),
            ('{{ "world"|hello_filter|bye_filter }}',
             {'hello_filter': hello_filter},
             'Bye Hello world!!'),
            ('{{ "world"|bye_filter|hello_filter }}',
             {'hello_filter': hello_filter},
             'Hello Bye world!!'),
        )
        for src, context, expect in TESTS:
            tmpl = Template(src)
            output = tmpl.render(context)
            self.assertRendered(output, expect, src)

    def test_single_filter_short_name(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ 42|quote }}', {}, '&quot;42&quot;'),
            ('{{ 13.37|quote }}', {}, '&quot;13.37&quot;'),
            ('{{ "world"|quote }}', {}, '&quot;world&quot;'),
        )
        for src, context, expect in TESTS:
            tmpl = Template(src)
            output = tmpl.render(context)
            self.assertRendered(output, expect, src)

    def test_single_filter_full_name(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ 42|tests.filters.quote }}', {}, '&quot;42&quot;'),
            ('{{ 13.37|tests.filters.quote }}', {}, '&quot;13.37&quot;'),
            ('{{ "world"|tests.filters.quote }}', {}, '&quot;world&quot;'),
        )
        for src, context, expect in TESTS:
            tmpl = Template(src)
            output = tmpl.render(context)
            self.assertRendered(output, expect, src)

    def test_multiple_filter_short_name(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ 42|quote|squote }}', {}, '&#39;&quot;42&quot;&#39;'),
            ('{{ 13.37|quote|squote }}', {}, '&#39;&quot;13.37&quot;&#39;'),
            ('{{ "world"|quote|squote }}', {}, '&#39;&quot;world&quot;&#39;'),
        )
        for src, context, expect in TESTS:
            tmpl = Template(src)
            output = tmpl.render(context)
            self.assertRendered(output, expect, src)

    def test_full_name_short_name(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ 42|tests.filters.quote|squote }}',
             {},
             '&#39;&quot;42&quot;&#39;'),
            ('{{ 13.37|tests.filters.quote|squote }}',
             {},
             '&#39;&quot;13.37&quot;&#39;'),
            ('{{ "world"|tests.filters.quote|squote }}',
             {},
             '&#39;&quot;world&quot;&#39;'),
        )
        for src, context, expect in TESTS:
            tmpl = Template(src)
            output = tmpl.render(context)
            self.assertRendered(output, expect, src)

    def test_short_name_full_name(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ 42|quote|tests.filters.squote }}',
             {},
             '&#39;&quot;42&quot;&#39;'),
            ('{{ 13.37|quote|tests.filters.squote }}',
             {},
             '&#39;&quot;13.37&quot;&#39;'),
            ('{{ "world"|quote|tests.filters.squote }}',
             {},
             '&#39;&quot;world&quot;&#39;'),
        )
        for src, context, expect in TESTS:
            tmpl = Template(src)
            output = tmpl.render(context)
            self.assertRendered(output, expect, src)


class OperatorsTest(TemplateTestCase):

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
        for src, context, expect in TESTS:
            tmpl = Template(src)
            output = tmpl.render(context)
            self.assertRendered(output, expect, src)

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
        for src, context, expect in TESTS:
            tmpl = Template(src)
            output = tmpl.render(context)
            self.assertRendered(output, expect, src)

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
        for src, context, expect in TESTS:
            tmpl = Template(src)
            output = tmpl.render(context)
            self.assertRendered(output, expect, src)

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
        for src, context, expect in TESTS:
            tmpl = Template(src)
            output = tmpl.render(context)
            self.assertRendered(output, expect, src)

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
        for src, context, expect in TESTS:
            tmpl = Template(src)
            output = tmpl.render(context)
            self.assertRendered(output, expect, src)

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
        for src, context, expect in TESTS:
            tmpl = Template(src)
            output = tmpl.render(context)
            self.assertRendered(output, expect, src)
