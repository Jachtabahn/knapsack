import argparse
import logging

class Knapsack:

    def __init__(self, knapsack_id, capacity):
        self.id = knapsack_id
        self.capacity = capacity
        self.items = []

    def add(self, weight, profit):
        item = Item(weight, profit)
        self.items.append(item)

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
    parser.add_argument('--basename', '-b', required=True)
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

    file = open(f'{args.basename}.inst.dat')
    for line in file:
        '''
            Example line: 9050 10 100 27 38 2 86 41 112 1 0 25 66 1 97 34 195 3 85 50 42 12 223
        '''
        info = line.split()
        assert len(info) >= 3
        knapsack_id, capacity = int(info[0]), int(info[2])
        knapsack = Knapsack(knapsack_id, capacity)
        for weight, profit in zip(info[3:-1:2], info[4::2]):
            knapsack.add(weight, profit)
        num_items = int(info[1])
        assert len(knapsack) == num_items

        with open(f'kp/{args.basename}_{knapsack.id}.kp', 'w') as f:
            f.write(f'c id {knapsack.id}\n')
            f.write(f't {knapsack.capacity}\n')
            for item in knapsack.items:
                f.write(f'{item.weight} {item.profit}\n')
    file.close()
