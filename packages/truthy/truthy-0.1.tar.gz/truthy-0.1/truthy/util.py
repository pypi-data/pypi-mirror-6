import itertools

from prettytable import PrettyTable

from truthy.expression import VarExpr
from truthy.parse import MyParser

parser = MyParser(debug=False)


def collect(root):
    children = root.children()
    return list(itertools.chain([root], *[collect(c) for c in children]))


def separate(root):
    exprs = collect(root)
    simple = list(set(expr for expr in exprs if isinstance(expr, VarExpr)))
    complx = sorted(set(expr for expr in exprs
                        if not isinstance(expr, VarExpr)), key=len)
    return simple, complx


def generate(simple, complx):
    labels = [expr.pretty() for expr in simple + complx]
    table = PrettyTable(labels)

    for perm in itertools.product([True, False], repeat=len(simple)):
        cperm = dict(zip(labels[:len(simple)], perm))
        row = list(perm)
        for expr in complx:
            row.append(expr.value(cperm))
        table.add_row([value and 'T' or 'F' for value in row])

    return table


def evaluate(expression):
    expr = parser.parse(expression)
    simple, complx = separate(expr)
    return generate(simple, complx)
