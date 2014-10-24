import rply


__all__ = ('lexers',)


class Lexers(object):

    def __init__(self):
        self.flg = rply.LexerGenerator()
        self.slg = rply.LexerGenerator()
        self._fl = None
        self._sl = None

    @property
    def fl(self):
        if self._fl is None:
            self._fl = self.flg.build()
        return self._fl

    @property
    def sl(self):
        if self._sl is None:
            self._sl = self.slg.build()
        return self._sl


lexers = Lexers()

from .filter import flg  # noqa
from .structure import slg  # noqa
