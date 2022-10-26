import re

class List(list):

    @property
    def strip(self):
        return List([x.strip() for x in self])

    def select(self, expr):
        return List([x for x in self if expr(x)])

    def len(self):
        return len(self)


class String(str):

    def match(self, expr):
        return re.match(expr, self)
