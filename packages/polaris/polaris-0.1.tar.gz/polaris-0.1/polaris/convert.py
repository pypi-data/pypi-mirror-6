"""
    polaris.convert
    ~~~~~~~~~~~~~~~

    :copyright: (c) 2013 Eleme, http://polaris.eleme.io
    :license: MIT

    Convert from DataFrame to other types for response.
"""

import copy
import io
import json

import vincent

from flask import current_app


def to_df(chart, **kwargs):
    """Convert chart to dataframe.
    """
    app = current_app
    assert(chart.source in app.config["source"])
    options = dict(chart.options)
    options.update(kwargs)
    df = app.config["source"][chart.source].get(**options)
    df.name = chart.name
    return df


def to_vega(df, vega_type, grid=True):
    """Convert dataframe to vega.
    """
    vega_type = vega_type.strip().lower()
    cls_map = {
        "line": vincent.Line,
        "scatter": vincent.Scatter,
        "bar": vincent.Bar,
        "groupedbar": vincent.GroupedBar,
        "area": vincent.Area,
        "pie": vincent.Pie,
        "word": vincent.Word
    }

    # Test if data has multi values
    stacked = len(df.columns) >= 2

    # normalize font size to range(10, 70) for word cloud
    if vega_type == "word":
        col_name = df.columns[0]
        col = df[col_name]
        c_min, c_max = min(col), max(col)
        scale = lambda x: int(((x - c_min) * (70 - 10)) / (c_max - c_min)) + 10
        df[col_name] = df[col_name].apply(scale)

    vega_data = cls_map[vega_type](df, width=800, height=500)

    # convert x-ax to datetime when possible.
    if vega_type in ("bar", "groupedbar") and vega_data._is_datetime:
        scale_x = [i for i in vega_data.scales if i.name == "x"][0]
        dt_x = copy.deepcopy(scale_x)
        dt_x.grammar.update({
            "name": "dt_x",
            "type": "time"
        })
        vega_data.scales.append(dt_x)

        ax_x = [i for i in vega_data.axes if i.scale == "x"][0]
        ax_x.scale = "dt_x"

        mark = vega_data.marks[0].marks[0]
        mark.properties.enter.x.scale = "dt_x"

    # offset y axis if it exists
    axes_y = [i for i in vega_data.axes if i.scale == "y"]
    if axes_y:
        ax_y = axes_y[0]
        ax_y.offset = 3
        if grid:
            ax_y.grid = True
            ax_y.layer = "back"

    if stacked or vega_type == "pie":
        vega_data.legend(title='')

    vega = json.loads(vega_data.to_json())
    vega["name"] = df.name
    return vega


def to_data(df, data_type):
    """Convert dataframe to data.
    """
    data_type = data_type.strip().lower()

    if data_type == "csv":
        with io.StringIO() as csv:
            df.to_csv(csv)
            return csv.getvalue()

    elif data_type == "html":
        return df.to_html()

    elif data_type == "json":
        df.insert(0, 'idx', df.index)
        return df.to_json(orient="records", date_format="iso",
                          force_ascii=False)

    elif data_type == "table":
        df.insert(0, 'idx', df.index)
        table = json.loads(df.to_json(orient="records",
                                      date_format="iso",
                                      force_ascii=False))
        return json.dumps({'name': df.name, "table": table})
