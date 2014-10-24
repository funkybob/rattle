import rply

from ..lexer import lexers


__all__ = ('parsers',)


class Parsers(object):

    def __init__(self):
        self._fpg = None
        self._fp = None
        self._spg = None
        self._sp = None

    @property
    def fpg(self):
        if self._fpg is None:
            self._fpg = rply.ParserGenerator(
                [rule.name for rule in lexers.flg.rules],
                precedence=[]
            )
        return self._fpg

    @property
    def fp(self):
        if self._fp is None:
            self._fp = self.fpg.build()
        return self._fp

    @property
    def spg(self):
        if self._spg is None:
            self._spg = rply.ParserGenerator(
                [rule.name for rule in lexers.slg.rules],
                precedence=[]
            )
        return self._spg

    @property
    def sp(self):
        if self._sp is None:
            self._sp = self.spg.build()
        return self._sp


parsers = Parsers()

# Load productions
from .filter import fpg  # noqa
from .structure import spg  # noqa
