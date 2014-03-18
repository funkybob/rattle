
import unittest

from rattle import Template

class VariableSyntaxTest(unittest.TestCase):

    # A list of (template, context, output)
    TESTS = (
        ('{{ a }}', {'a': 'yes'}, 'yes'),
        ('{{ a[1] }}', {'a': ['yes', 'no']}, 'no'),
        ('{{ a["b"] }}', {'a': {'b': 'yes'}}, 'yes'),
        ('{{ a[c] }}', {'a': {'b': 'yes', 'c': 'no'}, 'c': 'b'}, 'yes'),
    )

    def test_rendering(self):
        for src, context, expect in self. TESTS:
            tmpl = Template(src)
            output = tmpl.render(context)
            self.assertEqual(output, expect)

