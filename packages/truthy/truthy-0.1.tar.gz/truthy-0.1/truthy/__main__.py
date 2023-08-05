import sys

from truthy import evaluate


for line in sys.stdin:
    print(evaluate(line))
