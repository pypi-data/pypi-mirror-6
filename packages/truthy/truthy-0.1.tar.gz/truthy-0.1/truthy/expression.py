class VarExpr(object):

    def __init__(self, label):
        self.label = label

    def __eq__(self, other):
        return self.label == other.label

    def __len__(self):
        return len(self.label)

    def __hash__(self):
        return hash(self.pretty())

    def children(self):
        return []

    def pretty(self):
        return self.label

    def value(self, perm):
        return perm[self.label]


class BinExpr(object):

    def __init__(self, left, right, op):
        self.left = left
        self.right = right
        self.op = op

    def __eq__(self, other):
        return self.pretty() == other.pretty()

    def __len__(self):
        return len(self.pretty())

    def __hash__(self):
        return hash(self.pretty())

    def children(self):
        return [self.left, self.right]

    def pretty(self):
        return '({} {} {})'.format(self.left.pretty(),
                                   self.op,
                                   self.right.pretty())

    def value(self, perm):
        lvalue = self.left.value(perm)
        rvalue = self.right.value(perm)

        if self.op == '*':
            return lvalue and rvalue
        elif self.op == '+':
            return lvalue or rvalue
        elif self.op == '->':
            return not lvalue or rvalue
        elif self.op == '<=>':
            return lvalue == rvalue


class NotExpr(object):

    def __init__(self, expr):
        self.expr = expr

    def __eq__(self, other):
        return self.pretty() == other.pretty()

    def __len__(self):
        return len(self.pretty())

    def __hash__(self):
        return hash(self.pretty())

    def children(self):
        return [self.expr]

    def pretty(self):
        return '~{}'.format(self.expr.pretty())

    def value(self, perm):
        return not self.expr.value(perm)
