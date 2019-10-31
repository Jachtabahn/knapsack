from bokeh.core.properties import value
from bokeh.io import show, output_file
from bokeh.plotting import figure

output_file("bar_stacked.html")

fruits = ['Apples']
years = ["2015", "2016", "2017"]
colors = ["#c9d9d3", "#718dbf", "#e84d60"]

data = {'fruits' : fruits,
        '2015'   : [2],
        '2016'   : [5],
        '2017'   : [3]}

p = figure(x_range=fruits, plot_height=250, title="Fruit Counts by Year",
           toolbar_location=None, tools="hover", tooltips="$name @fruits: @$name")

p.vbar_stack(years, x='fruits', width=0.9, color=colors, source=data,
             legend=[value(x) for x in years])

p.y_range.start = 0
p.x_range.range_padding = 0.1
p.xgrid.grid_line_color = None
p.axis.minor_tick_line_color = None
p.outline_line_color = None
p.legend.location = "top_left"
p.legend.orientation = "horizontal"

show(p)
