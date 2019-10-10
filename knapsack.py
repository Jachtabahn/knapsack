import sys

'''
    If the 'subtract' argument is no given:
    For a given list of weights, computes a list where the i-th element is an list containing
    all the sums of the first i weights minus all the sums of the first i-1 weights. The i-th list contains
    the new sums that including the i-th weight brings to the set of sums of the first i-1 weights.

    If a 'subtract' argument is given:
    For a given list of weights, computes a list where the i-th element is an list containing
    all the sums of the first i+1 weights minus all the sums of the first i weights. The i-th list contains
    the new sums that including the (i+1)-th weight brings to the set of sums of the first i weights.
    Except that the function subtracts every sum from 'subtract' and if the result is positive,
    puts it in those lists instead, and if the difference is not positive, does not put
    this difference in the list.

    @param weights List of weights, positive numbers
    @param subtract A number to subtract every number in the weights list from
    @return list of lists where each list contains sums of weights as described above
'''
def all_sums(weights, subtract=None):
    sum_lists = [[0]]
    i = 1
    for weight in weights:
        print(f'Done weight {i}')
        i += 1
        new_sums = []
        for prior_list in sum_lists:
            for prior_sum in prior_list:
                new_sum = weight + prior_sum
                if new_sum not in sum(sum_lists, []):
                    new_sums.append(new_sum)
        sum_lists.append(new_sums)

    # subtract everything from the given budget (for forward sums)
    if subtract is not None:
        del sum_lists[len(sum_lists)-1]
        for sum_list in sum_lists:
            for i in range(len(sum_list)):
                sum_list[i] = subtract - sum_list[i]

        # delete everything non-positive
        for i in range(len(sum_lists)):
            sum_lists[i] = [s for s in sum_lists[i] if s > 0]
    else:
        del sum_lists[0]

    return sum_lists

'''
    Takes a list of those new sums of weights, and transforms it to a list where each contained list additionally
    contains all the element of its predecessors. Now the returned list contains ordered lists
    where the i-th list contains all the sums of the first i weights. And if 'infinity' is given, also puts
    the negative and positive infinity into each of those ordered lists.

    @my_list List with lists of numbers
    @param infinity A boolean to indicate whether or not to include the negative and positive infinity
    @return List of sorted lists where each list contains all the numbers of itself and predecessors
'''
def accumulate(my_list, infinity=False):
    base_list = [-float("inf"), float("inf")] if infinity else []
    return [sorted(sum(my_list[:i+1], base_list)) for i in range(len(my_list))]

'''
    Finds intervals from the second list which contain at least one point from the first list.

    The first given list is interpreted as a list of 1-D scalars and the second as a list of intervals
    over 1-D scalars. In the second list, every two consective numbers a, b form an interval that fits
    all scalars x with a <= x < b.

    Each interval is output as a pair (a, b). This function outputs a list of such pairs.

    @param accumulated_forward The scalars
    @param accumulated_backward The intervals
    @return list of pairs defining non-empty intervals from the second list
'''
def emptyness_check(accumulated_forward, accumulated_backward):
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
def get_total_benefit(solution, step, lower, upper):
    if step >= len(solution):
        return .0
    for (l, u), total_benefit in solution[step].items():
        if l <= lower < upper <= u:
            print(f'At step {step}, queried interval ({lower}, {upper}); got total profit of interval ({l}, {u})')
            return total_benefit
    print(f'At step {step}, queried interval ({lower}, {upper}) is not contained in any available interval')
    print(solution[step].keys())
    return None

class Item:

    def __init__(self, weight, profit):
        self.weight = weight
        self.profit = profit

def parse(file):
    total_capacity = None
    knapsack_items = []
    for line in file:
        info = line.split(' ')
        if info[0] == 't':
            total_capacity = int(info[1])
        else:
            weight = int(info[0])
            profit = int(info[1])
            item = Item(weight, profit)
            knapsack_items.append(item)
    if total_capacity is None: return None
    return total_capacity, knapsack_items

knapsack_problem = parse(sys.stdin)
if knapsack_problem is None:
    print('Error parsing the knapsack instance')
total_capacity = knapsack_problem[0]
knapsack_items = knapsack_problem[1]

knapsack_items.sort(key=lambda item: item.weight)
weights = [item.weight for item in knapsack_items]
profits = [item.profit for item in knapsack_items]
# compute the relevant total_capacity intervals
forward_sums = all_sums(weights, subtract=total_capacity)
backward_sums = all_sums(weights[::-1])
accumulated_forward_sums = accumulate(forward_sums)
accumulated_backward_sums = accumulate(backward_sums, infinity=True)[::-1]
print('The accumulated forward sums are')
for step, sums_list in enumerate(accumulated_forward_sums):
    print(f'Item {step+1}: {sums_list}')
print()
print('The accumulated backward sums are')
for step, sums_list in enumerate(accumulated_backward_sums):
    print(f'Item {step+1}: {sums_list}')
print()
budget_intervals_per_step = emptyness_check(accumulated_forward_sums, accumulated_backward_sums)
print(f'The non-empty intervals are')
for step, budget_intervals in enumerate(budget_intervals_per_step):
    print(f'Item {step+1}: {budget_intervals}')
print()

num_items = len(knapsack_items)
solution = [dict() for _ in range(num_items)]
for step in range(num_items)[::-1]:
    for lower_budget, upper_budget in budget_intervals_per_step[step]:
        max_total_benefit = get_total_benefit(solution, step+1, lower_budget, upper_budget)

        weight = weights[step]
        if weight <= lower_budget:
            profit = profits[step]
            one_total_benefit = profit \
                + get_total_benefit(solution, step+1, lower_budget-weight, upper_budget-weight)
            if one_total_benefit > max_total_benefit:
                max_total_benefit = one_total_benefit

        solution[step][(lower_budget, upper_budget)] = max_total_benefit

print('The solution of the Knapsack problem is')
for step, total_benefits in enumerate(solution):
    print(f'Item {step+1}: {total_benefits}')
