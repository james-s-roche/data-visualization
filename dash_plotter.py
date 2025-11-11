"""Dash Plotter

Run this file to start a small Dash app for interactive data exploration.

Features:
- Upload CSV files (client side) or use the default pandas `iris` dataset
    or pd.util.testing.makeMixedDataFrame()
    or pd.util.testing.makeMissingDataframe()
    or px.data.gapminder(datetimes=True)
    or px.data.stocks(datetimes=True)
- Automatic column type inference (numeric vs categorical)
- Select plot type (scatter, box, bar, histogram, violin)
- Dropdowns for x, y, color, size that update to show only relevant columns
- Responsive interactive Plotly figures

Dependencies: dash, pandas, plotly
Install: pip install dash pandas plotly

Run: python dash_plotter.py
Then open http://127.0.0.1:8050 in your browser.
"""

from __future__ import annotations

import base64
import io
from typing import List, Optional

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State


def infer_column_types(df: pd.DataFrame, cat_threshold: int = 20):
    """Return numeric and categorical column lists.

    Numeric = pandas numeric dtypes.
    Categorical = object/category/bool OR numeric columns with low cardinality.
    """
    numeric = df.select_dtypes(include=["number"]).columns.tolist()
    categorical = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

    # Consider numeric columns with low unique counts as categorical (e.g., small enums)
    for col in numeric:
        try:
            if df[col].nunique(dropna=True) <= cat_threshold:
                categorical.append(col)
        except Exception:
            pass

    # Dedupe
    categorical = [c for i, c in enumerate(categorical) if c not in categorical[:i]]
    return numeric, categorical


def parse_upload(contents: str, filename: str) -> pd.DataFrame:
    header, encoded = contents.split(",", 1)
    data = base64.b64decode(encoded)
    # try common formats
    try:
        return pd.read_csv(io.BytesIO(data))
    except Exception:
        try:
            return pd.read_excel(io.BytesIO(data))
        except Exception as e:
            raise ValueError(f"Unable to parse uploaded file '{filename}': {e}")


def create_app() -> Dash:
    app = Dash(__name__)

    demo_df = px.data.tips()

    # Layout: main plot on the left, controls on the right stacked vertically
    app.layout = html.Div([
        html.H3("Dash Plotter — interactive data exploration"),

        html.Div([
            # Left: graph
            html.Div([
                dcc.Store(id="df-store", data=demo_df.to_json(date_format="iso", orient="split")),
                dcc.Loading(dcc.Graph(id="main-graph", style={"height": "80vh"}), type="default"),
            ], style={"flex": "1"}),

            # Right: controls column
            html.Div([
                dcc.Upload(
                    id="upload-data",
                    children=html.Div(["Drag & drop a CSV file here, or click to select file"]),
                    style={
                        "width": "100%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                    },
                    multiple=False,
                ),
                html.Div(id="upload-filename", style={"marginTop": 6}),

                html.Div(style={"height": 12}),

                html.Label("Plot type"),
                dcc.Dropdown(
                    id="plot-type",
                    options=[
                        {"label": "Scatter", "value": "scatter"},
                        {"label": "Box", "value": "box"},
                        {"label": "Bar", "value": "bar"},
                        {"label": "Histogram", "value": "hist"},
                        {"label": "Violin", "value": "violin"},
                    ],
                    value="scatter",
                    clearable=False,
                ),

                html.Hr(),

                html.Div([html.Label("X"), dcc.Dropdown(id="x-column")], id="x-container", style={"marginBottom": 8}),
                html.Div([html.Label("Y"), dcc.Dropdown(id="y-column")], id="y-container", style={"marginBottom": 8}),
                html.Div([html.Label("Color"), dcc.Dropdown(id="color-column")], id="color-container", style={"marginBottom": 8}),
                html.Div([html.Label("Size"), dcc.Dropdown(id="size-column")], id="size-container", style={"marginBottom": 8}),
            ], style={"width": "320px", "flex": "0 0 320px", "paddingLeft": 12}),

        ], style={"display": "flex", "alignItems": "flex-start", "gap": "24px", "margin": 24}),

        html.Div(id="debug", style={"display": "none"}),
    ])


    @app.callback(
        Output("df-store", "data"),
        Output("upload-filename", "children"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        State("df-store", "data"),
    )
    def handle_upload(contents, filename, current_json):
        # If no upload, keep current data
        if contents is None:
            return current_json, "Using example dataset"
        try:
            df = parse_upload(contents, filename)
        except Exception as e:
            return current_json, f"Upload failed: {e}"
        # store as json
        return df.to_json(date_format="iso", orient="split"), f"Loaded: {filename} ({len(df)} rows)"


    @app.callback(
        Output("x-column", "options"),
        Output("y-column", "options"),
        Output("color-column", "options"),
        Output("size-column", "options"),
        Output("x-column", "value"),
        Output("y-column", "value"),
        Output("color-column", "value"),
        Output("size-column", "value"),
        Input("df-store", "data"),
        Input("plot-type", "value"),
    )
    def update_column_options(df_json, plot_type):
        df = pd.read_json(df_json, orient="split")
        numeric, categorical = infer_column_types(df)

        # default options (all columns)
        all_options = [{"label": c, "value": c} for c in df.columns]

        # determine allowed columns depending on plot type
        if plot_type == "scatter":
            x_opts = [{"label": c, "value": c} for c in numeric]
            y_opts = [{"label": c, "value": c} for c in numeric]
            size_opts = [{"label": c, "value": c} for c in numeric]
            color_opts = all_options
        elif plot_type in ("box", "violin"):
            # box/violin: x categorical, y numeric
            x_opts = [{"label": c, "value": c} for c in categorical]
            y_opts = [{"label": c, "value": c} for c in numeric]
            size_opts = []
            color_opts = all_options
        elif plot_type == "bar":
            # bar: x categorical, y numeric (aggregation)
            x_opts = [{"label": c, "value": c} for c in categorical]
            y_opts = [{"label": c, "value": c} for c in numeric]
            size_opts = []
            color_opts = all_options
        elif plot_type == "hist":
            # histogram: x numeric (or categorical optionally)
            x_opts = [{"label": c, "value": c} for c in numeric + categorical]
            y_opts = []
            size_opts = []
            color_opts = all_options
        else:
            x_opts = all_options
            y_opts = all_options
            size_opts = all_options
            color_opts = all_options

        # pick sensible defaults if possible
        def first_or_none(opts):
            return opts[0]["value"] if opts else None

        return x_opts, y_opts, color_opts, size_opts, first_or_none(x_opts), first_or_none(y_opts), None, None


    @app.callback(
        Output("size-container", "style"),
        Output("y-container", "style"),
        Input("plot-type", "value"),
    )
    def toggle_visibility(plot_type):
        # Hide size for box/violin; hide y for histogram
        size_style = {"display": "none"} if plot_type in ("box", "violin") else {}
        y_style = {"display": "none"} if plot_type == "hist" else {}
        return size_style, y_style


    @app.callback(
        Output("main-graph", "figure"),
        Input("df-store", "data"),
        Input("plot-type", "value"),
        Input("x-column", "value"),
        Input("y-column", "value"),
        Input("color-column", "value"),
        Input("size-column", "value"),
    )
    def update_figure(df_json, plot_type, x, y, color, size):
        df = pd.read_json(df_json, orient="split")

        # Basic guard
        if df is None or df.shape[0] == 0:
            return {}

        try:
            if plot_type == "scatter":
                if not x or not y:
                    return px.scatter(df, title="Select X and Y columns")
                fig = px.scatter(df, x=x, y=y, color=color if color else None, size=size if size else None, hover_data=df.columns)
            elif plot_type == "box":
                if not x or not y:
                    return px.box(df, title="Select X (categorical) and Y (numeric)")
                fig = px.box(df, x=x, y=y, color=color if color else None)
            elif plot_type == "violin":
                if not x or not y:
                    return px.violin(df, title="Select X (categorical) and Y (numeric)")
                fig = px.violin(df, x=x, y=y, color=color if color else None)
            elif plot_type == "bar":
                if not x or not y:
                    return px.bar(df, title="Select X (categorical) and Y (numeric)")
                fig = px.bar(df, x=x, y=y, color=color if color else None)
            elif plot_type == "hist":
                if not x:
                    return px.histogram(df, title="Select X column")
                fig = px.histogram(df, x=x, color=color if color else None)
            else:
                fig = px.scatter(df, x=x, y=y, color=color if color else None)

            fig.update_layout(transition_duration=200)
            return fig
        except Exception as e:
            # return a simple figure with error message
            return px.scatter(title=f"Error building plot: {e}")


    return app


if __name__ == "__main__":
    app = create_app()
    # `run_server` was deprecated and replaced by `run` in newer Dash versions
    # use app.run(...) which mirrors the new API
    app.run(debug=True)
