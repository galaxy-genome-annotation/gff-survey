import re

class List(list):

    @property
    def strip(self):
        return List([x.strip() for x in self])

    def select(self, expr):
        return List([x for x in self if expr(x)])

    @property
    def len(self):
        return len(self)

    @property
    def length(self):
        return len(self)

    def map(self, expr):
        return List(map(expr, self))

    @property
    def uniq(self):
        return List(set(self))


class String(str):

    def match(self, expr):
        return re.match(expr, self)


class Dict(dict):

    def sorted(self, expr):
        return sorted(self.items(), key=expr)
