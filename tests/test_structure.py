from tests.utils import TemplateTestCase


class CommentTest(TemplateTestCase):

    def test_inline_comment(self):
        TESTS = (
            ('{# abc #}', ''),
            ('abc{# def #}', 'abc'),
            ('abc {# def #}', 'abc '),
            ('{# abc #}def', 'def'),
            ('{# abc #} def', ' def'),
            ('abc{# def #}ghi', 'abcghi'),
            ('abc {# def #} ghi', 'abc  ghi'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)

    def test_multiple_inline_comment(self):
        TESTS = (
            ('{# abc #}{# ABC #}', ''),
            ('abc{# def #}ABC{# DEF #}', 'abcABC'),
            ('abc {# def #}ABC {# DEF #}', 'abc ABC '),
            ('{# abc #}def{# ABC #}DEF', 'defDEF'),
            ('{# abc #} def{# ABC #} DEF', ' def DEF'),
            ('abc{# def #}ghiABC{# DEF #}GHI', 'abcghiABCGHI'),
            ('abc {# def #} ghiABC {# DEF #} GHI', 'abc  ghiABC  GHI'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)


class IfTest(TemplateTestCase):

    def test_if_true(self):
        TESTS = (
            ('{% if True %}Hello{% endif %}', 'Hello'),
            ('{% if True %}Hello{% endif %} world', 'Hello world'),
            ('{% if True %}Hello {% endif %}world', 'Hello world'),
            ('Hello {% if True %}world{% endif %}', 'Hello world'),
            ('Hello{% if True %} world{% endif %}', 'Hello world'),
            ('Hello {% if True %}world{% endif %} !', 'Hello world !'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)

    def test_if_false(self):
        TESTS = (
            ('{% if False %}Hello{% endif %}', ''),
            ('{% if False %}Hello{% endif %} world', ' world'),
            ('{% if False %}Hello {% endif %}world', 'world'),
            ('Hello {% if False %}world{% endif %}', 'Hello '),
            ('Hello{% if False %} world{% endif %}', 'Hello'),
            ('Hello {% if False %}world{% endif %} !', 'Hello  !'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)

    def test_if_true_or_false(self):
        TESTS = (
            ('{% if True or False %}Hello{% endif %}', 'Hello'),
            ('{% if True or False %}Hello{% endif %} world', 'Hello world'),
            ('{% if True or False %}Hello {% endif %}world', 'Hello world'),
            ('Hello {% if True or False %}world{% endif %}', 'Hello world'),
            ('Hello{% if True or False %} world{% endif %}', 'Hello world'),
            ('Hello {% if True or False %}world{% endif %} !', 'Hello world !'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)

    def test_if_true_and_false(self):
        TESTS = (
            ('{% if True and False %}Hello{% endif %}', ''),
            ('{% if True and False %}Hello{% endif %} world', ' world'),
            ('{% if True and False %}Hello {% endif %}world', 'world'),
            ('Hello {% if True and False %}world{% endif %}', 'Hello '),
            ('Hello{% if True and False %} world{% endif %}', 'Hello'),
            ('Hello {% if True and False %}world{% endif %} !', 'Hello  !'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)


class IfElseTest(TemplateTestCase):

    def test_if_else_true(self):
        TESTS = (
            ('{% if True %}abc{% else %}def{% endif %}', 'abc'),
            ('{% if True %}abc{% else %}def{% endif %} ghi', 'abc ghi'),
            ('{% if True %}abc {% else %}def {% endif %}ghi', 'abc ghi'),
            ('abc {% if True %}def{% else %}ghi{% endif %}', 'abc def'),
            ('abc{% if True %} def{% else %} ghi{% endif %}', 'abc def'),
            ('abc {% if True %}def{% else %}ghi{% endif %} jkl', 'abc def jkl'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)

    def test_if_else_false(self):
        TESTS = (
            ('{% if False %}abc{% else %}def{% endif %}', 'def'),
            ('{% if False %}abc{% else %}def{% endif %} ghi', 'def ghi'),
            ('{% if False %}abc {% else %}def {% endif %}ghi', 'def ghi'),
            ('abc {% if False %}def{% else %}ghi{% endif %}', 'abc ghi'),
            ('abc{% if False %} def{% else %} ghi{% endif %}', 'abc ghi'),
            ('abc {% if False %}def{% else %}ghi{% endif %} jkl', 'abc ghi jkl'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)

    def test_if_else_true_or_false(self):
        TESTS = (
            ('{% if True or False %}abc{% else %}def{% endif %}', 'abc'),
            ('{% if True or False %}abc{% else %}def{% endif %} ghi', 'abc ghi'),
            ('{% if True or False %}abc {% else %}def {% endif %}ghi', 'abc ghi'),
            ('abc {% if True or False %}def{% else %}ghi{% endif %}', 'abc def'),
            ('abc{% if True or False %} def{% else %} ghi{% endif %}', 'abc def'),
            ('abc {% if True or False %}def{% else %}ghi{% endif %} jkl', 'abc def jkl'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)

    def test_if_else_true_and_false(self):
        TESTS = (
            ('{% if True and False %}abc{% else %}def{% endif %}', 'def'),
            ('{% if True and False %}abc{% else %}def{% endif %} ghi', 'def ghi'),
            ('{% if True and False %}abc {% else %}def {% endif %}ghi', 'def ghi'),
            ('abc {% if True and False %}def{% else %}ghi{% endif %}', 'abc ghi'),
            ('abc{% if True and False %} def{% else %} ghi{% endif %}', 'abc ghi'),
            ('abc {% if True and False %}def{% else %}ghi{% endif %} jkl', 'abc ghi jkl'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect)


class ForTest(TemplateTestCase):

    def test_for(self):
        ctx = {'b': [1, 2, 3]}
        TESTS = (
            ('{% for a in b %}.{% endfor %}', '...'),
            ('{% for a in b %}.{% endfor %} world', '... world'),
            ('{% for a in b %}. {% endfor %} world', '. . .  world'),
            ('Hello {% for a in b %}.{% endfor %}', 'Hello ...'),
            ('Hello{% for a in b %} .{% endfor %}', 'Hello . . .'),
            ('Hello {% for a in b %}.{% endfor %} !', 'Hello ... !'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_for_replacement(self):
        ctx = {'b': [1, 2, 3]}
        TESTS = (
            ('{% for a in b %}{{ a }}{% endfor %}', '123'),
            ('{% for a in b %}{{ a }}{% endfor %} world', '123 world'),
            ('{% for a in b %}{{ a }} {% endfor %} world', '1 2 3  world'),
            ('Hello {% for a in b %}{{ a }}{% endfor %}', 'Hello 123'),
            ('Hello{% for a in b %} {{ a }}{% endfor %}', 'Hello 1 2 3'),
            ('Hello {% for a in b %}{{ a }}{% endfor %} !', 'Hello 123 !'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_for_nested(self):
        ctx = {'b': [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}
        TESTS = (
            ('{% for a in b %}{% for c in a %}.{% endfor %}-{% endfor %}', '...-...-...-'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_for_nested_replacement(self):
        ctx = {'b': [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}
        TESTS = (
            ('{% for a in b %}{% for c in a %}{{ c }}{% endfor %}-{% endfor %}', '123-456-789-'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect, ctx)


class ForEmptyTest(TemplateTestCase):

    def test_for_empty(self):
        ctx = {'b': []}
        TESTS = (
            ('{% for a in b %}.{% empty %}-{% endfor %}', '-'),
            ('{% for a in b %}.{% empty %}-{% endfor %} world', '- world'),
            ('{% for a in b %}. {% empty %}- {% endfor %} world', '-  world'),
            ('Hello {% for a in b %}.{% empty %}-{% endfor %}', 'Hello -'),
            ('Hello{% for a in b %} .{% empty %} -{% endfor %}', 'Hello -'),
            ('Hello {% for a in b %}.{% empty %}-{% endfor %} !', 'Hello - !'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_for_empty_replacement(self):
        ctx = {'b': [], 'c': 'x'}
        TESTS = (
            ('{% for a in b %}.{% empty %}{{ c }}{{ c }}{% endfor %}', 'xx'),
            ('{% for a in b %}.{% empty %}{{ c }}{% endfor %} world', 'x world'),
            ('{% for a in b %}. {% empty %}{{ c }} {% endfor %} world', 'x  world'),
            ('Hello {% for a in b %}.{% empty %}{{ c }}{% endfor %}', 'Hello x'),
            ('Hello{% for a in b %} .{% empty %} {{ c }}{% endfor %}', 'Hello x'),
            ('Hello {% for a in b %}.{% empty %}{{ c }}{% endfor %} !', 'Hello x !'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_for_else(self):
        ctx = {'b': []}
        TESTS = (
            ('{% for a in b %}.{% else %}-{% endfor %}', '-'),
            ('{% for a in b %}.{% else %}-{% endfor %} world', '- world'),
            ('{% for a in b %}. {% else %}- {% endfor %} world', '-  world'),
            ('Hello {% for a in b %}.{% else %}-{% endfor %}', 'Hello -'),
            ('Hello{% for a in b %} .{% else %} -{% endfor %}', 'Hello -'),
            ('Hello {% for a in b %}.{% else %}-{% endfor %} !', 'Hello - !'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect, ctx)

    def test_for_else_replacement(self):
        ctx = {'b': [], 'c': 'x'}
        TESTS = (
            ('{% for a in b %}.{% else %}{{ c }}{% endfor %}', 'x'),
            ('{% for a in b %}.{% else %}{{ c }}{% endfor %} world', 'x world'),
            ('{% for a in b %}. {% else %}{{ c }} {% endfor %} world', 'x  world'),
            ('Hello {% for a in b %}.{% else %}{{ c }}{% endfor %}', 'Hello x'),
            ('Hello{% for a in b %} .{% else %} {{ c }}{% endfor %}', 'Hello x'),
            ('Hello {% for a in b %}.{% else %}{{ c }}{% endfor %} !', 'Hello x !'),
        )
        for src, expect in TESTS:
            self.assertRendered(src, expect, ctx)
