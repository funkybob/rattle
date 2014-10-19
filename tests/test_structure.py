import sys

from rattle import Template

from tests.utils import TemplateTestCase


PY3 = sys.version_info[0] == 3


class IfTest(TemplateTestCase):

    def test_if(self):
        TESTS = (
            ('{% if True %}Hello{% endif %}', 'Hello'),
            ('{% if True %}Hello{% endif %} world', 'Hello world'),
            ('{% if True %}Hello {% endif %}world', 'Hello world'),
            ('Hello {% if True %}world{% endif %}', 'Hello world'),
            ('Hello{% if True %} world{% endif %}', 'Hello world'),
            ('Hello {% if True %}world{% endif %} !', 'Hello world !'),
            # ('{% if False %}Hello{% endif %}', ''),

            # ('Foo {% if True %}Hello{% endif %} Bar', 'Foo Hello Bar'),
            # ('Foo {% if False %}Hello{% endif %} Bar', 'Foo  Bar'),
        )
        for src, expect in TESTS:
            tmpl = Template(src)
            output = tmpl.render()
            self.assertRendered(output, expect, src)
