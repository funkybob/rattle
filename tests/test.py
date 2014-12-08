from tests.utils import TemplateTestCase


class SpecialCaseTests(TemplateTestCase):

    def test_empty_template(self):
        self.assertRendered('', '')
