import datetime
from os.path import dirname, join
import pandas as pd
from scipy.signal import savgol_filter
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, DataRange1d, Select
from bokeh.palettes import Blues4
from bokeh.plotting import figure

df = pd.read_csv(join(dirname(__file__), "data/weatherAUS.csv"))

STATISTICS = ["record_min_temp", "record_max_temp"]


def get_dataset(src, name, distribution):
    df = src[src.location == name].copy()
    del df["location"]
    df["date"] = pd.to_datetime(df.date)
    df["left"] = df.date - datetime.timedelta(days=0.5)
    df["right"] = df.date + datetime.timedelta(days=0.5)
    df = df.set_index(["date"])
    df.sort_index(inplace=True)
    if distribution == "Smoothed":
        window, order = 51, 3
        for key in STATISTICS:
            df[key] = savgol_filter(df[key], window, order)

    return ColumnDataSource(data=df)


def make_plot(source, title):
    plot = figure(x_axis_type="datetime", width=800, tools="", toolbar_location=None)
    plot.title.text = title
    plot.quad(
        top="record_max_temp",
        bottom="record_min_temp",
        left="left",
        right="right",
        color="#CE1141",
        source=source,
        legend_label="Temperature",
    )
    plot.xaxis.axis_label = None
    plot.yaxis.axis_label = "Temperature (C)"
    plot.axis.axis_label_text_font_style = "bold"
    plot.x_range = DataRange1d(range_padding=0.0)
    plot.grid.grid_line_alpha = 0.3

    return plot


def update_plot(attrname, old, new):
    city = city_select.value
    plot.title.text = "Data Cuaca " + cities[city]["title"]

    src = get_dataset(df, cities[city]["location"], distribution_select.value)
    source.data.update(src.data)


city = "Albury"
distribution = "Discrete"

cities = {
    "Albury": {
        "location": "Albury",
        "title": "Albury, AUS",
    },
    "Badgerys Creek": {
        "location": "BadgerysCreek",
        "title": "Badgerys Creek, AUS",
    },
    "Melbourne": {
        "location": "Melbourne",
        "title": "Melbourne, AUS",
    },
}

city_select = Select(value=city, title="City", options=sorted(cities.keys()))
distribution_select = Select(
    value=distribution, title="Distribution", options=["Discrete", "Smoothed"]
)

source = get_dataset(df, cities[city]["location"], distribution)
plot = make_plot(source, "Data Cuaca " + cities[city]["title"])

city_select.on_change("value", update_plot)
distribution_select.on_change("value", update_plot)

controls = column(city_select, distribution_select)

curdoc().add_root(row(plot, controls))
curdoc().title = "Weather"
