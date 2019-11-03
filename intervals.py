from bokeh.core.properties import value
from bokeh.io import show, output_file
from bokeh.plotting import figure

item_ids = [12, 2]
all_intervals = [
	[4, 6, 10, 14, 18, 20, 22, 24, 25, 28, 29, 31, 32, 35],
	[9, 19, 29, 30, 31, 45, 67, 111, 145, 188, 999, 1111, 2222, 9999]
]
num_items = len(all_intervals)

plot = figure(
	title='Weight intervals',
	tools='pan,reset,wheel_zoom',
	active_scroll='wheel_zoom')
red = '#e84d60'

intervals = [4, 6, 10, 15]

widths = [b - a for a, b in zip(intervals[1:], intervals[:-1])]
xs = intervals[:-1]
xs = [x + width/2 for x, width in zip(xs, widths)]
num_intervals = len(xs)
print(xs)
print(widths)
plot.rect(xs, 1, width=widths, height=1, color=red, alpha=0.5)

plot.y_range.start = 0
plot.x_range.range_padding = 0.1
plot.xgrid.grid_line_color = None
plot.axis.minor_tick_line_color = None
plot.outline_line_color = None

output_file('bar_stacked.html')
show(plot)
