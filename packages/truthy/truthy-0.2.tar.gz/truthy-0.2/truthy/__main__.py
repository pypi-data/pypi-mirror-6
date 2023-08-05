import sys
import purplex
import itertools
import prettytable


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
            return self.expr1.get_table(assignments) + [col] + self.expr2.get_table(assignments)

    return AbstractBinaryExpr

ConjunctionExpr = generate_BinaryExpr("&", lambda a, b: a and b)
DisjunctionExpr = generate_BinaryExpr("v", lambda a, b: a or b)
ConditionalExpr = generate_BinaryExpr("->", lambda a, b: (not a) or (a and b))
BiconditionalExpr = generate_BinaryExpr("<->", lambda a, b: a == b)


class MyLexer(purplex.Lexer):
    LABEL = purplex.TokenDef(r'[A-Z]+')
    AND = purplex.TokenDef(r'\&')
    BICOND = purplex.TokenDef(r'<->')
    COND = purplex.TokenDef(r'->')
    NOT = purplex.TokenDef(r'~')
    OR = purplex.TokenDef(r'v')
    LPAREN = purplex.TokenDef(r'\(')
    RPAREN = purplex.TokenDef(r'\)')
    WHITESPACE = purplex.TokenDef(r'[\s\n]+', ignore=True)


class MyParser(purplex.Parser):

    LEXER = MyLexer
    PRECEDENCE = (
        ('left', 'OR', 'AND', 'COND', 'BICOND'),
        ('left', 'NOT'),
    )

    @purplex.attach('e : LPAREN e RPAREN')
    def parens(self, *children):
        return children[1]

    @purplex.attach('e : e AND e')
    def conjunction_expr(self, *children):
        return ConjunctionExpr(children[0], children[2])

    @purplex.attach('e : e BICOND e')
    def bicondition_expr(self, *children):
        return BiconditionalExpr(children[0], children[2])

    @purplex.attach('e : e COND e')
    def conditional_expr(self, *children):
        return ConditionalExpr(children[0], children[2])

    @purplex.attach('e : e OR e')
    def disjunction_expr(self, *children):
        return DisjunctionExpr(children[0], children[2])

    @purplex.attach('e : NOT e')
    def not_expr(self, *children):
        return NotExpr(children[1])

    @purplex.attach('e : LABEL')
    def label_expr(self, *children):
        return VarExpr(children[0])

    def on_error(self, args):
        raise Exception('hello')


def get_permutations(var_list):
    """Given variable names, return list of dicts with all the permutations."""
    for perm in itertools.product([True, False], repeat=len(var_list)):
        yield dict(zip(var_list, perm))


def bool_str(bool_list):
    for b in bool_list:
        yield 'T' if b else 'F'


def main():
    parser = MyParser(debug=False)
    for line in sys.stdin:
        parse_tree = parser.parse(line)
        var_list = sorted(set(parse_tree.get_vars()))
        permutations = list(get_permutations(var_list))

        # print the parsed expression
        print(parse_tree)

        # print the table
        table = prettytable.PrettyTable()
        for var in var_list:
            table.add_column(var,
                             list(bool_str([p[var] for p in permutations])))
        table.add_column("", ["" for _ in permutations])
        for col in parse_tree.get_table(permutations):
            table.add_column(col[0], list(bool_str(col[1:])))
        print(table)


if __name__ == '__main__':
    main()
