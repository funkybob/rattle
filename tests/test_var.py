import sys
import unittest

from rattle import Template

from .utils import Mock


PY3 = sys.version_info[0] == 3


class TemplateTestCase(unittest.TestCase):

    def assertRendered(self, actual, expected, template):
        try:
            self.assertEqual(actual, expected)
        except Exception as e:
            standardMsg = e.message
            if isinstance(template, Template):
                source = template.source
            else:
                source = template
            msg = 'Failed rendering template %s:\n%s' % (source, standardMsg)
            self.fail(self._formatMessage(msg, standardMsg))


class LiteralSyntaxTest(TemplateTestCase):

    def test_renderStringLiteral(self):
        tmpl = Template("{{ 'hello' }}")
        output = tmpl.render()
        self.assertRendered(output, 'hello', tmpl)

    def test_renderNumLiteral(self):
        tmpl = Template('{{ 23 }}')
        output = tmpl.render()
        self.assertRendered(output, '23', tmpl)


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


class OperatorsTest(TemplateTestCase):

    def test_add(self):
        # A list of (template, context, output)
        TESTS = (
            ('{{ 1 + 2 }}', {}, '3'),
            ('{{ a + 2 }}', {'a': 1}, '3'),
            ('{{ 1 + b }}', {'b': 2}, '3'),
            ('{{ a + b }}', {'a': 1, 'b': 2}, '3'),
            ('{{ a + a }}', {'a': 1}, '2'),
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
