import sys
import json
from os import path
import time
import logging
import argparse

'''
    Computes a list for a given list of numbers. This list has length len(numbers)+1. This list contains
    lists of sums of elements of the given list. The very first sum list is the list of all sums of the first
    zero elements of the given list, that is [0]. The second includes the first element a of the given list
    and as such contains [0, a] and so on.

    @param numbers given list of numbers, whose partial sums are to be computed
    @return list of partial sums of given list
'''
def make_sum_combinations(numbers):
    sum_lists = [[0]]
    w = 1
    logging.debug(f'There are {len(numbers)} numbers to make sums of')
    for number in numbers:
        prior_sums = sum_lists[-1]
        next_sums = list(prior_sums)
        for prior_sum in prior_sums:
            new_sum = number + prior_sum
            if new_sum not in next_sums:
                next_sums.append(new_sum)
        sum_lists.append(next_sums)
        logging.debug(f'Computed {len(next_sums)} sums up to {w}th number')
        w += 1
    return sum_lists

'''
    Computes a list of all non-empty, partial sums of the first so-and-so-many weights,
    going from left to right. The list of non-empty, partial sums of the first zero weights,
    that is the empty list, is left out. Additionally, every computed list contains two additional elements:
    the negative and positive infinity.

    @param weights list of positive numbers
    @return list of lists of partial sums
'''
def compute_backward_sums(weights):
    sum_lists = make_sum_combinations(weights)

    del sum_lists[0]
    for i in range(len(sum_lists)):
        # around zero there is no change in the maximum total benefit
        sum_lists[i].remove(0)

        sum_lists[i].sort()
        sum_lists[i].insert(0, -float('inf'))
        sum_lists[i].append(float('inf'))

    return sum_lists

'''
    Finds intervals from the second list, which contain at least one point from the first list.

    The first given list is interpreted as a list of 1-D scalars and the second as a list of intervals
    over 1-D scalars. In the second list, every two consective numbers a, b form an interval that fits
    all scalars x with a <= x < b.

    Each interval is output as a pair (a, b). This function outputs a list of such pairs.

    @param accumulated_forward The scalars
    @param accumulated_backward The intervals
    @return list of pairs defining non-empty intervals from the second list
'''
def compute_relevant_intervals(accumulated_backward, weights, capacity):
    all_intervals = []
    current_accumulated = [capacity]
    logging.debug(f'There are {len(weights)-1} numbers to make sums of')
    for step in range(len(weights)):
        if step > 0:
            weight = weights[step-1]
            previous_length = len(current_accumulated)
            for old_leftover in current_accumulated[:previous_length]:
                new_leftover = old_leftover - weight
                if new_leftover >= 0 and new_leftover not in current_accumulated:
                    current_accumulated.append(new_leftover)
            logging.debug(f'Computed {len(current_accumulated)} sums up to {step}th number')
        intervals = []
        for leftover_capacity in current_accumulated:
            for (lower, upper) in zip(accumulated_backward[step][:-1], accumulated_backward[step][1:]):
                if lower <= leftover_capacity < upper:
                    if (lower, upper) not in intervals:
                        intervals.append((lower, upper))
        all_intervals.append(intervals)
    return all_intervals

'''
    Gets the value of the indicated dictionary inside 'solution' of the key, that is an interval which
    completely covers the given interval (lower, upper).

    'solution' is a list of dictionaries where each dictionary maps pairs of numbers, that is intervals,
    to some sums of the profits. Now, we are given an interval and want to find the value of this interval
    but the dictionary might not contain this exact interval, so we look for one that completely covers
    this interval.

    We use the dictionary at 'step' if it exists. It might be that 'step' shoots over the length of the list
    in which case, we return 0.

    This function is undefined if the given interval is not completely contained in some interval of the
    targeted dictionary.

    @param solution List of dictionary to query
    @param step The index of the dictionary to query
    @param lower The lower boundary of the interval, whose sum of profits we want to know
    @param upper The upper boundary of the interval, whose sum of profits we want to know
'''
def get_total_profit(solution, step, lower, upper):
    if step >= len(solution): return .0

    epsilon = 1e-8
    for (l, u), total_profit in solution[step].items():
        if -epsilon + l <= lower < upper <= u + epsilon:
            logging.debug(f'At step {step}, queried interval ({lower}, {upper}); got total profit of interval ({l}, {u})')
            return total_profit
    logging.debug(f'At step {step}, queried interval ({lower}, {upper}) is not contained in any available interval')
    logging.debug(solution[step].keys())
    return None

class Item:
    def __init__(self, index, weight, profit):
        self.id = index
        self.weight = weight
        self.clean_weight = weight
        self.sparse_weight = None
        self.profit = profit

    def __str__(self):
        return f'Real weight {self.weight}, Clean weight {self.clean_weight}, Profit {self.profit}'

    def show_all(my_items):
        for item in my_items:
            logging.info('Item {:4d}: {}'.format(item.id, item))
        logging.info('')

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

def sparse_number(dense, base):
    sparse = dict()
    i = 0
    smaller = dense

    # preprocess the number, so we also include sparse after the comma
    after_comma = smaller - int(smaller)
    while after_comma > 0:
        i -= 1
        smaller *= base
        after_comma = smaller - int(smaller)

    smaller = int(smaller)
    while smaller > 0:
        remain = smaller % base
        if remain > 0:
            sparse[i] = remain
        smaller = int(smaller / base)
        i += 1
    return sparse

def dense_number(sparse, base):
    dense = 0
    for i, digit in sparse.items():
        dense += digit * (base**i)
    return dense

def increment(sparse, exponent, base):
    if exponent not in sparse:
        sparse[exponent] = 1
    elif sparse[exponent] < base - 1:
        sparse[exponent] += 1
    else:
        del sparse[exponent]
        increment(sparse, exponent + 1, base)

def pop(key, dictionary, default=0):
    if key not in dictionary:
        return default
    else:
        value = dictionary[key]
        del dictionary[key]
        return value

def solve_knapsack(knapsack_problem, modulo=1, removable_exponents=[]):
    capacity, knapsack_items = knapsack_problem

    for step, item in enumerate(knapsack_items):
        item.clean_weight = item.weight
        item.sparse_weight = None

    # remove details from the weights and capacity
    removable_exponents.sort(reverse=True)
    half_base = int(modulo / 2) + 1
    if modulo > 1:
        # remove details from weights
        for item in knapsack_items:
            sparse_weight = sparse_number(item.weight, modulo)
            item.sparse_weight = sparse_weight # save this sparse representation for later

            # round only after deleting the most important exponent
            if removable_exponents:
                exponent = removable_exponents[0]
                digit = pop(exponent, sparse_weight)
                if digit >= half_base:
                    increment(sparse_weight, exponent + 1, modulo)
                for exponent in removable_exponents[1:]:
                    digit = pop(exponent, sparse_weight)

            item.clean_weight = dense_number(sparse_weight, modulo)

    # remove the zero-profit items
    zero_profit = [i for i in range(len(knapsack_items)) if knapsack_items[i].profit == 0]
    for i in sorted(zero_profit, reverse=True):
        # it is important to have the indices sorted, otherwise the wrong items will be removed
        logging.debug(f'Removing the zero-profit {i}th item with {knapsack_items[i]}')
        del knapsack_items[i]

    # lay aside the zero-weight items, and later in every case include them in the knapsack
    zero_weight = [i for i in range(len(knapsack_items)) if knapsack_items[i].clean_weight == 0]
    cheap_items = []
    for i in sorted(zero_weight, reverse=True):
        # it is important to have the indices sorted, otherwise the wrong items will be looked at
        cheap = knapsack_items[i]
        logging.debug(f'Laying aside zero-weight {i}th item with {cheap}')
        del knapsack_items[i]
        cheap_items.append(cheap)

    # sort the weights ascendingly, otherwise the intervals will not be computed correctly
    knapsack_items.sort(key=lambda item: item.clean_weight)

    logging.info(f'The Knapsack has total capacity {capacity}, and the following items are available:')
    Item.show_all(knapsack_items)

    # sum up all combinations of the first so-and-so-many weights
    weights = [item.clean_weight for item in knapsack_items]

    if modulo > 1:
        for item in knapsack_items:
            digits = item.sparse_weight
            strings_list = [' ']*16
            right = min(digits.keys())
            left = max(digits.keys())
            for i in range(right, left+1):
                digit = digits[i] if i in digits else 0
                strings_list[i] = str(digit)
            number_string = '-'.join(strings_list[::-1])
            number_string = '|' + number_string + '|'
            logging.info('Item {:4d}: {}'.format(item.id, digits))
            logging.info('Item {:4d}: {}'.format(item.id, number_string))
            logging.info('')

    # sum up all combinations of the last so-and-so-many weights
    # two subsequent weights form an interval
    accumulated_backward_sums = compute_backward_sums(weights[::-1])[::-1]
    logging.debug('The accumulated backward sums are')
    for step, sums_list in enumerate(accumulated_backward_sums):
        item = knapsack_items[step]
        logging.debug(f'Item {item.id}: {sums_list}')
    logging.debug('')

    # determine all intervals, which contain at least one forward sum
    # these are the relevant intervals, for which we will later compute maximum total benefits
    budget_intervals_per_step = compute_relevant_intervals(accumulated_backward_sums, weights, capacity)
    logging.debug(f'The non-empty intervals are')
    for step, budget_intervals in enumerate(budget_intervals_per_step):
        item = knapsack_items[step]
        logging.debug(f'Item {item.id}: {budget_intervals}')
    logging.debug('')

    # compute maximum total benefits for every pair of item index and relevant interval
    num_items = len(knapsack_items)
    solution = [dict() for _ in range(num_items)]
    profits = [item.profit for item in knapsack_items]
    for step in range(num_items)[::-1]:
        for lower_budget, upper_budget in budget_intervals_per_step[step]:
            max_total_profit = get_total_profit(solution, step+1, lower_budget, upper_budget)

            weight = weights[step]
            if weight <= lower_budget:
                profit = profits[step]
                one_total_profit = profit \
                    + get_total_profit(solution, step+1, lower_budget-weight, upper_budget-weight)
                if one_total_profit > max_total_profit:
                    max_total_profit = one_total_profit

            solution[step][(lower_budget, upper_budget)] = max_total_profit

    logging.info('Solution table of the Knapsack instance:')
    for step, total_profit in enumerate(solution):
        item = knapsack_items[step]
        logging.info(f'Item {item.id}: {total_profit}')
    logging.info('')

    # collect the items required to achieve the maximum total benefit
    taking = []
    cur_interval = list(list(solution[0].keys())[0])
    for step in range(num_items):

        # this is the total benefit, that we want to reach
        max_total_profit = get_total_profit(solution, step, cur_interval[0], cur_interval[1])

        # this is the total benefit, if we don't take this item
        zero_total_profit = get_total_profit(solution, step+1, cur_interval[0], cur_interval[1])
        if max_total_profit <= zero_total_profit:
            continue

        # take the current item
        taking.append(step)
        weight = weights[step]
        cur_interval = (cur_interval[0]-weight, cur_interval[1]-weight)

    # always take the zero-weight items
    taken_items = [knapsack_items[step] for step in taking] + cheap_items
    taken_weight = sum([item.weight for item in taken_items])
    taken_profit = sum([item.profit for item in taken_items])
    logging.info(f'Pack following {len(taken_items)} items of total real weight {taken_weight} '
        + f'and total profit {taken_profit} in the Knapsack:')
    for step in taking:
        item = knapsack_items[step]
        logging.info(f'Item {item.id}: {item}')

    return taken_profit, taken_weight, taken_items

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--modulo', '-m', type=int, default=1)
    parser.add_argument('--info', type=str, default=None)
    parser.add_argument('--exponents', '-e', type=int, action='append', default=[])
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

    if args.modulo < 1:
        logging.error('Modulo must be at least 1!')
        exit(1)

    # parse the knapsack instance from given file
    start_time = time.time()
    knapsack_problem = parse_knapsack(sys.stdin)
    if knapsack_problem is None:
        logging.error('Could not parse the knapsack instance given through stdin')
        exit(1)
    capacity = knapsack_problem[0]
    taken_profit, used_capacity, taken_items = solve_knapsack(knapsack_problem, args.modulo, args.exponents)
    if used_capacity > capacity:
        logging.warning('Knapsack problem solved incorrectly with the modulo, solving again without it..')
        taken_profit, used_capacity, taken_items = solve_knapsack((capacity, taken_items))
    taken_time = time.time() - start_time

    sys.stdout.write(f'p {taken_profit}\n')
    knapsack_items = knapsack_problem[1]
    all_ids = [item.id for item in knapsack_items]
    taken_ids = [item.id for item in taken_items]
    for item_id in sorted(all_ids):
        if item_id in taken_ids:
            sys.stdout.write('1\n')
        else:
            sys.stdout.write('0\n')

    if args.info is not None:
        info = {
            'runtime': taken_time,
            'total_profit': taken_profit
        }
        with open(args.info, 'w') as f:
            f.write(json.dumps(info, indent=4))
