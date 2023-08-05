import sys

from truthy import generate


def main():
    for line in sys.stdin:
        parse_tree, table = generate(line)

        print(parse_tree)
        print(table)


if __name__ == '__main__':
    main()
