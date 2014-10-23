from unittest import TestCase

from rattle.utils.parser import split_tag_args_string


class ParserUtilsTest(TestCase):

    def test_split_tag_args_string(self):
        TESTS = (
            (' ', []),
            ('    ', []),
            ('arg', ['arg']),
            ('arg1 arg2', ['arg1', 'arg2']),
            ('  arg  ', ['arg']),
            ('  arg1   arg2  ', ['arg1', 'arg2']),
            ('kwarg=1', ['kwarg=1']),
            ('kwarg1=1 kwarg2=2', ['kwarg1=1', 'kwarg2=2']),
            ('  kwarg=1  ', ['kwarg=1']),
            ('  kwarg1=1   kwarg2=2  ', ['kwarg1=1', 'kwarg2=2']),

            ('" "', ['" "']),
            ('"    "', ['"    "']),
            ('"arg"', ['"arg"']),
            ('"arg1 arg2"', ['"arg1 arg2"']),
            ('"  arg  "', ['"  arg  "']),
            ('"  arg1   arg2  "', ['"  arg1   arg2  "']),
            ('"kwarg=1"', ['"kwarg=1"']),
            ('"kwarg1=1 kwarg2=2"', ['"kwarg1=1 kwarg2=2"']),
            ('"  kwarg=1  "', ['"  kwarg=1  "']),
            ('"  kwarg1=1   kwarg2=2  "', ['"  kwarg1=1   kwarg2=2  "']),

            ("' '", ["' '"]),
            ("'    '", ["'    '"]),
            ("'arg'", ["'arg'"]),
            ("'arg1 arg2'", ["'arg1 arg2'"]),
            ("'  arg  '", ["'  arg  '"]),
            ("'  arg1   arg2  '", ["'  arg1   arg2  '"]),
            ("'kwarg=1'", ["'kwarg=1'"]),
            ("'kwarg1=1 kwarg2=2'", ["'kwarg1=1 kwarg2=2'"]),
            ("'  kwarg=1  '", ["'  kwarg=1  '"]),
            ("'  kwarg1=1   kwarg2=2  '", ["'  kwarg1=1   kwarg2=2  '"]),

            ('kwarg="k v"', ['kwarg="k v"']),
            ('kwarg1="k v 1" kwarg2="  k  v  2  "',
             ['kwarg1="k v 1"', 'kwarg2="  k  v  2  "']),
            ('  kwarg="  kv  1  " ', ['kwarg="  kv  1  "']),

            ('(1 + 2)', ['(1 + 2)']),
            (' ( 1 + 2 ) ', ['( 1 + 2 )']),
            (' ( 1 + 2 )  ( 3 + 4 ) ', ['( 1 + 2 )', '( 3 + 4 )']),
            (' ( 1 + 2 )  kwarg=( 3 + 4 ) ', ['( 1 + 2 )', 'kwarg=( 3 + 4 )']),
            (' ( 1 + 2 )  kwarg1=( 3 + 4 )  kwarg2="kwarg2" ',
             ['( 1 + 2 )', 'kwarg1=( 3 + 4 )', 'kwarg2="kwarg2"']),

            # Test cases taken from Django:
            # https://github.com/django/django/blob/3c6ac0bab8bfaf1f1bb79a8b6a7a36533666908c/tests/utils_tests/test_text.py#L30
            ('This is "a person" test.',
             ['This', 'is', '"a person"', 'test.']),
            ('This is "a person\'s" test.',
             ['This', 'is', '"a person\'s"', 'test.']),
            ('This is "a person\\"s" test.',
             ['This', 'is', '"a person\\"s"', 'test.']),
            ("all friends\\' tests",
             ['all', "friends\\'", 'tests']),
            ('url search_page words="something else"',
             ['url', 'search_page', 'words="something else"']),
            ("url search_page words='something else'",
             ['url', 'search_page', "words='something else'"]),
            ('url search_page words "something else"',
             ['url', 'search_page', 'words', '"something else"']),
            ('url search_page words-"something else"',
             ['url', 'search_page', 'words-"something else"']),
            ('url search_page words=hello',
             ['url', 'search_page', 'words=hello']),
            ('url search_page words=\\"something else',
             ['url', 'search_page', 'words=\\"something', 'else']),
            ("cut:','|cut:' '",
             ["cut:','|cut:' '"]),
        )
        for src, expect in TESTS:
            self.assertEqual(split_tag_args_string(src), expect, "Parsing `%s`." % src)

    def test_split_tag_args_string_invalid(self):
        TESTS = (
            # Test cases taken from Django:
            # https://github.com/django/django/blob/3c6ac0bab8bfaf1f1bb79a8b6a7a36533666908c/tests/utils_tests/test_text.py#L30
            ('"a" \'one',
             ['"a', "'one"]),
            ('all friends\' tests',
             ['all', 'friends\'', 'tests']),
            ('url search_page words="something else',
             ['url', 'search_page', 'words="something', 'else']),
        )
        for src, expect in TESTS:
            try:
                split_tag_args_string(src)
                self.fail("Parsing `%s` failed." % src)
            except ValueError:
                pass
