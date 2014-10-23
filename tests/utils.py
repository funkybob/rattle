import unittest

from rattle.template import Template


class Mock(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class TemplateTestCase(unittest.TestCase):

    def assertRendered(self, source, expected, context=None):
        try:
            tmpl = Template(source)
            rendered = tmpl.render({} if context is None else context)
            self.assertEqual(rendered, expected)
        except Exception as e:
            if hasattr(e, 'message'):
                standardMsg = e.message
            elif hasattr(e, 'args') and len(e.args) > 0:
                standardMsg = e.args[0]
            else:
                standardMsg = ''
            msg = 'Failed rendering template %s:\n%s: %s' % (
                source, e.__class__.__name__, standardMsg)
            self.fail(msg)
