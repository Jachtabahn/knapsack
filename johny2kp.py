import argparse
import logging

'''
A file with content
20 878
44 92
46 4
90 43
72 83
91 84
40 68
75 92
35 82
8 6
54 44
78 32
40 18
77 56
15 83
61 25
17 96
75 70
29 48
75 14
63 58

should be converted to a .kp file with content
t 878
92 44
4 46
43 90
83 72
84 91
68 40
92 75
82 35
6 8
44 54
32 78
18 40
56 77
83 15
25 61
96 17
70 75
48 29
14 75
58 63

'''

class Knapsack:

    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []

    def add(self, weight, profit):
        item = Item(weight, profit)
        self.items.append(item)

    def save(self, filepath):
        with open(filepath, 'w') as f:
            f.write(f't {self.capacity}\n')
            for item in self.items:
                f.write(f'{item.weight} {item.profit}\n')

    def __len__(self): return len(self.items)

class Item:
    def __init__(self, weight, profit):
        self.weight = weight
        self.profit = profit

    def __str__(self):
        return f'Weight {self.weight}, Profit {self.profit}'

    def show_all(my_items):
        for step, item in enumerate(my_items):
            logging.info(f'Item {step+1}: {item}')
        logging.info('')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('basenames', nargs='+')
    parser.add_argument('--verbose', '-v', action='count')
    args = parser.parse_args()

    log_levels = {
        None: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }
    if args.verbose is not None and args.verbose >= len(log_levels):
        args.verbose = len(log_levels)-1
    logging.basicConfig(format='%(message)s', level=log_levels[args.verbose])

    for basename in args.basenames:
        with open(basename) as file:
            line = file.readline()
            info = line.split()
            try: capacity = int(info[1])
            except: capacity = float(info[1])
            knapsack = Knapsack(capacity)
            for line in file:
                info = line.split()
                try: weight = int(info[1])
                except: weight = float(info[1])
                try: profit = int(info[0])
                except: profit = float(info[0])
                knapsack.add(weight, profit)
            knapsack.save(f'{basename}.kp')
