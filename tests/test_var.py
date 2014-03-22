
import unittest

from rattle import Template

from .utils import Mock


class LiteralSyntaxTest(unittest.TestCase):

    def test_renderStringLiteral(self):
        tmpl = Template("{{ 'hello' }}")
        output = tmpl.render()
        self.assertEqual(output, 'hello')

    def test_renderNumLiteral(self):
        tmpl = Template('{{ 23 }}')
        output = tmpl.render()
        self.assertEqual(output, '23')


class VariableSyntaxTest(unittest.TestCase):

    # A list of (template, context, output)
    TESTS = (
        ('{{ a }}', {'a': 'yes'}, 'yes'),
        ('{{ a[1] }}', {'a': ['yes', 'no']}, 'no'),
        ('{{ a["b"] }}', {'a': {'b': 'yes'}}, 'yes'),
        ('{{ a[c] }}', {'a': {'b': 'yes', 'c': 'no'}, 'c': 'b'}, 'yes'),
        ('{{ a["b"].c }}', {'a': {'b': Mock(c=1)}}, '1'),
        ('{{ a(1) }}', {'a': lambda x: x}, '1'),
        ('{{ a(b,1) }}', {'a': lambda x, y: x + y, 'b': 6}, '7'),
    )

    def test_rendering(self):
        for src, context, expect in self. TESTS:
            tmpl = Template(src)
            output = tmpl.render(context)
            self.assertEqual(output, expect)

