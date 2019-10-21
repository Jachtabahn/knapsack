import sys
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
    logging.debug(f'There are {len(numbers)} weights')
    for number in numbers:
        prior_sums = sum_lists[-1]
        next_sums = list(prior_sums)
        for prior_sum in prior_sums:
            new_sum = number + prior_sum
            if new_sum not in next_sums:
                next_sums.append(new_sum)
        sum_lists.append(next_sums)
        logging.debug(f'Computed {len(next_sums)} sums up to {w}th weight')
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
    Computes a list of all partial sums of the first so-and-so-many weights,
    going from left to right. The list of partial sums of all weights is left out.

    @param weights list of positive numbers
    @return list of lists of partial sums
'''
def compute_forward_sums(weights, knapsack_capacity):
    sum_lists = make_sum_combinations(weights[:-1])

    # subtract from the given capacity every sum, and leave out too big weight sums
    for i, sum_list in enumerate(sum_lists):
        sum_lists[i] = [knapsack_capacity - my_sum for my_sum in sum_list if knapsack_capacity >= my_sum]
        sum_lists[i].sort()

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
def compute_relevant_intervals(accumulated_forward, accumulated_backward):
    all_intervals = []
    for step in range(len(accumulated_forward)):
        intervals = []
        for forward in accumulated_forward[step]:
            for (lower, upper) in zip(accumulated_backward[step][:-1], accumulated_backward[step][1:]):
                if lower <= forward < upper:
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

    for (l, u), total_profit in solution[step].items():
        if l <= lower < upper <= u:
            logging.debug(f'At step {step}, queried interval ({lower}, {upper}); got total profit of interval ({l}, {u})')
            return total_profit
    logging.debug(f'At step {step}, queried interval ({lower}, {upper}) is not contained in any available interval')
    logging.debug(solution[step].keys())
    return None

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

def parse_knapsack(file):
    total_capacity = None
    knapsack_items = []
    for line in file:
        info = line.split(' ')
        if info[0] == 'c':
            continue
        if info[0] == 't':
            total_capacity = int(info[1])
        else:
            weight = int(info[0])
            profit = int(info[1])
            item = Item(weight, profit)
            knapsack_items.append(item)
    if total_capacity is None: return None
    return total_capacity, knapsack_items

def solve_knapsack(file):
    # parse the knapsack instance from given file
    knapsack_problem = parse_knapsack(file)
    if knapsack_problem is None:
        logging.error('Could not parse the knapsack instance given through stdin')

    # sort the weights ascendingly
    total_capacity, knapsack_items = knapsack_problem
    knapsack_items.sort(key=lambda item: item.weight)

    logging.info(f'The Knapsack has total capacity {total_capacity}, and the following items are available:')
    Item.show_all(knapsack_items)

    # sum up all combinations of the first so-and-so-many weights
    weights = [item.weight for item in knapsack_items]
    accumulated_forward_sums = compute_forward_sums(weights, knapsack_capacity=total_capacity)
    logging.debug('The accumulated forward sums are')
    for step, sums_list in enumerate(accumulated_forward_sums):
        logging.debug(f'Item {step+1}: {sums_list}')
    logging.debug('')

    # sum up all combinations of the last so-and-so-many weights
    # two subsequent weights form an interval
    accumulated_backward_sums = compute_backward_sums(weights[::-1])[::-1]
    logging.debug('The accumulated backward sums are')
    for step, sums_list in enumerate(accumulated_backward_sums):
        logging.debug(f'Item {step+1}: {sums_list}')
    logging.debug('')

    # determine all intervals, which contain at least one forward sum
    # these are the relevant intervals, for which we will later compute maximum total benefits
    budget_intervals_per_step = compute_relevant_intervals(accumulated_forward_sums, accumulated_backward_sums)
    logging.debug(f'The non-empty intervals are')
    for step, budget_intervals in enumerate(budget_intervals_per_step):
        logging.debug(f'Item {step+1}: {budget_intervals}')
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

    logging.info('The solution table of the Knapsack instance:')
    for step, total_profit in enumerate(solution):
        logging.info(f'Item {step+1}: {total_profit}')
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

    taken_items = [knapsack_items[step] for step in taking]
    taken_weight = sum([item.weight for item in taken_items])
    taken_profit = sum([item.profit for item in taken_items])
    logging.info(f'I pack the following {len(taken_items)} items of total weight {taken_weight} '
        + f'and total profit {taken_profit} in my Knapsack:')
    for step in taking:
        item = knapsack_items[step]
        logging.info(f'Item {step+1}: {item}')

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

    solve_knapsack(sys.stdin)
