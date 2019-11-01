import sys
import time
import logging
import argparse

class Item:
    def __init__(self, index, weight, profit):
        self.id = index
        self.weight = weight
        self.profit = profit

    def __str__(self):
        if self.clean_weight != self.weight:
            return f'Real weight {self.weight}, Clean weight {self.clean_weight}, Profit {self.profit}'
        return f'Real weight {self.weight}, Profit {self.profit}'

def parse_knapsack(file):
    capacity = None
    knapsack_items = []
    index = 1
    for line in file:
        info = line.split(' ')
        if info[0] == 'c':
            continue
        if info[0] == 't':
            try: capacity = int(info[1])
            except: capacity = float(info[1])
        else:
            try: weight = int(info[0])
            except: weight = float(info[0])
            try: profit = int(info[1])
            except: profit = float(info[1])
            item = Item(index, weight, profit)
            knapsack_items.append(item)
        index += 1
    if capacity is None: return None
    return capacity, knapsack_items

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
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

    # parse the knapsack instance from given file
    start_time = time.time()
    knapsack_problem = parse_knapsack(sys.stdin)
    if knapsack_problem is None:
        logging.error('Could not parse the knapsack instance given through stdin')
        exit(1)
    capacity, knapsack_items = knapsack_problem

    print(f'NumItems = {len(knapsack_items)};\n')

    print(f'Capacity = {capacity};\n')

    weights = [item.weight for item in knapsack_items]
    print(f'Weights = {weights};\n')

    profits = [item.profit for item in knapsack_items]
    print(f'Profits = {profits};')
