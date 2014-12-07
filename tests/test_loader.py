
import os
from unittest import TestCase

from rattle import Template
from rattle.loader import select_template

TEST_DIR = os.path.dirname(__file__)
TEMPLATE_DIRS = [
    os.path.join(TEST_DIR, 'templates/'),
]

class LoaderTest(TestCase):

    def test_loader(self):

        t = select_template('index.html', TEMPLATE_DIRS)
        self.assertTrue(isinstance(t, Template))

    def test_not_found(self):
        with self.assertRaises(ValueError):
            select_template('notfound.html', TEMPLATE_DIRS)

    def test_suspicious(self):
        with self.assertRaises(ValueError):
            select_template('../test.html', TEMPLATE_DIRS)
