
import unittest

from rattle import Template

class Mock(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class VariableSyntaxTest(unittest.TestCase):

    # A list of (template, context, output)
    TESTS = (
        ('{{ a }}', {'a': 'yes'}, 'yes'),
        ('{{ a[1] }}', {'a': ['yes', 'no']}, 'no'),
        ('{{ a["b"] }}', {'a': {'b': 'yes'}}, 'yes'),
        ('{{ a[c] }}', {'a': {'b': 'yes', 'c': 'no'}, 'c': 'b'}, 'yes'),
        ('{{ a["b"].c }}', {'a': {'b': Mock(c=1)}}, '1'),
    )

    def test_rendering(self):
        for src, context, expect in self. TESTS:
            tmpl = Template(src)
            output = tmpl.render(context)
            self.assertEqual(output, expect)

