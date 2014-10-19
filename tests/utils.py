import unittest

from rattle.template import Template


class Mock(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


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
