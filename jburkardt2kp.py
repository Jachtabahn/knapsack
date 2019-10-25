import sys

'''
    Convert the set of three files per instance from
    https://people.sc.fsu.edu/~jburkardt/datasets/knapsack_01/knapsack_01.html
    to one file in my .kp format, which is similar to the .gr format from PACE challenges.
'''

prefix = sys.argv[1]
with open(f'{prefix}_c.txt') as f:
    total_capacity = int(f.read())

weights = []
with open(f'{prefix}_w.txt') as f:
    for line in f:
        weight = int(line[:-1])
        weights.append(weight)

profits = []
with open(f'{prefix}_p.txt') as f:
    for line in f:
        profit = int(line[:-1])
        profits.append(profit)

with open(f'{prefix}.kp', 'w') as f:
    f.write(f't {total_capacity}\n')
    for w, p in zip(weights, profits):
        f.write(f'{w} {p}\n')
