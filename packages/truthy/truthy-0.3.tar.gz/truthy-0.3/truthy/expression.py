class VarExpr(object):

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def evaluate(self, assignment):
        return assignment[self.name]

    def get_vars(self):
        return [self.name]

    def get_table(self, assignments):
        col = [self.name]
        for assignment in assignments:
            col.append(assignment[self.name])
        return [col]


class NotExpr(object):

    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return '(~{})'.format(self.expr)

    def evaluate(self, assignment):
        return not self.expr.evaluate(assignment)

    def get_vars(self):
        return self.expr.get_vars()

    def get_table(self, assignments):
        col = ["~"]
        for assignment in assignments:
            col.append(self.evaluate(assignment))
        return [col] + self.expr.get_table(assignments)


def generate_BinaryExpr(symbol_str, operator_f):
    class AbstractBinaryExpr(object):

        def __init__(self, expr1, expr2):
            self.expr1 = expr1
            self.expr2 = expr2

        def __repr__(self):
            return '({} {} {})'.format(self.expr1, symbol_str, self.expr2)

        def evaluate(self, assignment):
            return operator_f(self.expr1.evaluate(assignment),
                              self.expr2.evaluate(assignment))

        def get_vars(self):
            return self.expr1.get_vars() + self.expr2.get_vars()

        def get_table(self, assignments):
            col = [symbol_str]
            for assignment in assignments:
                col.append(self.evaluate(assignment))
            res = self.expr1.get_table(assignments) + [col] + self.expr2.get_table(assignments)
            res[0][0] = '(' + res[0][0]
            res[-1][0] += ')'
            return res

    return AbstractBinaryExpr

ConjunctionExpr = generate_BinaryExpr("&", lambda a, b: a and b)
DisjunctionExpr = generate_BinaryExpr("v", lambda a, b: a or b)
ConditionalExpr = generate_BinaryExpr("->", lambda a, b: (not a) or (a and b))
BiconditionalExpr = generate_BinaryExpr("<->", lambda a, b: a == b)
