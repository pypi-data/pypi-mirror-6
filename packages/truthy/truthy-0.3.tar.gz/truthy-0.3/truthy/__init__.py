import itertools

import prettytable

from truthy.parse import MyParser

parser = MyParser(debug=False)


def get_permutations(var_list):
    """Given variable names, return list of dicts with all the permutations."""
    for perm in itertools.product([True, False], repeat=len(var_list)):
        yield dict(zip(var_list, perm))


def bool_str(bool_list):
    for b in bool_list:
        yield 'T' if b else 'F'


def generate(raw_expression):
    parse_tree = parser.parse(raw_expression)
    var_list = sorted(set(parse_tree.get_vars()))
    permutations = list(get_permutations(var_list))

    table = prettytable.PrettyTable()
    for var in var_list:
        table.add_column(var,
                         list(bool_str([p[var] for p in permutations])))
    table.add_column("", ["" for _ in permutations])
    for col in parse_tree.get_table(permutations):
        table.add_column(col[0], list(bool_str(col[1:])))

    return parse_tree, table
