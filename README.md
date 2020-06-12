# Quick Start

On Linux, do
```bash
git clone git@github.com:Jachtabahn/knapsack.git
cd knapsack
python knapsack.py  < madcat/inst/kp/knap_10_9052.kp
```

# Approach to the Knapsack problem

Here, I take a Knapsack instance given by a list of costs, a list of benefits and a budget, and for each item,
I want to find the costs which are truly necessary to find the total benefits of all the items before it.
I do it by computing sums of costs coming from left and sums of costs coming from right, on the sorted list of costs.

## Forward sums = Possible budgets

From left, the sums of the first i costs are what has to be subtracted from the total budget
to get the budget we might end up having after processing the first i items.

For example, before deciding anything at the first item, we will always have the exact same budget, namely the
total given budget. At the first item, we might have that, too, or we have the total budget minus the cost
of the first item, and so on.

The number of possible budgets grows from left to right. To the left, we have only made few decisions, and so
there are only few possibilities for what our actual budget at some item might be. To the right, we have
already made lots of decisions, and since there are so many variations as to what I could have done to arrive
at this item to decide whether to take it, there are lots of possible budgets that I actually might have at this
point.

## Backward sums = Budget intervals

From right, the ordered sums of the last i costs represent a set of intervals. These intervals are over
the budgets, and any budget in some fixed interval at some item i will have the same total benefit. This
means that we can compute the total benefit only once for this whole interval.

For example, the last item might have cost 200. The only two intervals that matter are when I have a budget at least
200, or when I have a budget smaller than 200.

The number of intervals grows from right to left. To the right, there are only few possibilities for me to change
my budget in the future because the future is short. To the left, there are many possibilities to change
my budget because the future is long, and I can buy this and not that item in many different variations.

## Their combination = Relevant budget intervals

Now, both sums, from left and from right, exclude a lot of budgets for which I don't need any total benefit
for some i-th item. They cancel each other out.

For example, at the last item, I might end up having lots of different budgets, but almost all of them are going to get the same total benefit, because there are only two intervals, namely the one going from negative infinity to 200 and the one going from 200 to positive infinity.

Or at the first item, I have lots of intervals because there are so many things I could do in the future, and so I have to differentiate a lot of cases. But in fact there is exactly one possible budget I could possibly have here, the total
budget. This one will be in exactly one of the intervals. So I can just compute the total benefit for that one interval
and leave out all the others.

We compute the possible budgets and the budget intervals after we **sort the list of costs**. Because if we don't, the *containment property* from below will not hold.

So, after we have for each item the possible budgets and the budget intervals, we just extract those budget intervals that actually can occur for the given total budget, that is, those budget intervals at some item i that actually contain
at least one possible budget that I could have at this item going from left.

Then I do dynamic programming going from right. I can easily compute to the total benefit for the last item for the two
intervals: Namely, the interval below the last item's cost gets total benefit 0 and the other interval gets the total
benefit the benefit of this item. At the second-to-last item I now have a refinement of the intervals at the last step. This is so because the sums of costs including some new cost are a superset of the sums of costs without this new cost.
Now, I have my relevant budget intervals at the second-to-last item. If I subtract this item's cost or if I don't subtract anything from this budget interval, the resulting budget interval will, from my experiments, always be completely inside some of the budget intervals at the next item. I call this the *containment property* of the budget intervals. This property will not hold if the list of costs is unsorted. This unsorted example will not work
```
budget = 225
costs = [5, 7, 100, 100, 105, 150, 200, 8, 5, 7, 12]
benefits = [10, 1, 100, 5, 17, 42, 52, 1, 1, 1, 1]
```

I believe, the *containment property* can be proven. I just didn't have the time to do it yet. It goes like this:


*Containment property*: Given a sorted list of costs and all lists of budget intervals computed from this list of costs. Then for all i (except the last), every budget interval in the i-th list is completely contained in some budget interval in the (i+1)-th list.
