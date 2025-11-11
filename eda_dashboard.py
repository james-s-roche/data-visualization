"""EDA Dashboard

Run this file to start a comprehensive exploratory data analysis (EDA) Dash app.

Features:
- Tab 1 (Plot): Interactive plotting with multiple plot types
- Tab 2 (Data Table): View and explore raw data with sorting/filtering
- Tab 3 (Inspector): Analyze individual columns (stats for numeric, counts for categorical)
- Tab 4 (Correlations): Pairwise correlation heatmap with Pearson/Spearman toggle

Dependencies: dash, pandas, plotly, scipy (for Spearman correlation)
Install: pip install dash pandas plotly scipy

Run: python eda_dashboard.py
Then open http://127.0.0.1:8050 in your browser.
"""

from __future__ import annotations

import base64
import io
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from scipy.stats import spearmanr
from dash import Dash, dcc, html, Input, Output, State, callback


def safe_read_json(json_string: str) -> pd.DataFrame:
    """Safely read JSON from string using StringIO to avoid FutureWarning."""
    return pd.read_json(io.StringIO(json_string), orient="split")


def infer_column_types(df: pd.DataFrame, cat_threshold: int = 20) -> Tuple[List[str], List[str]]:
    """Return numeric and categorical column lists.

    Numeric = pandas numeric dtypes.
    Categorical = object/category/bool OR numeric columns with low cardinality.
    """
    numeric = df.select_dtypes(include=["number"]).columns.tolist()
    categorical = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

    # Consider numeric columns with low unique counts as categorical
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
    """Parse uploaded file (CSV or Excel)."""
    header, encoded = contents.split(",", 1)
    data = base64.b64decode(encoded)
    try:
        return pd.read_csv(io.BytesIO(data))
    except Exception:
        try:
            return pd.read_excel(io.BytesIO(data))
        except Exception as e:
            raise ValueError(f"Unable to parse uploaded file '{filename}': {e}")


def compute_numeric_stats(series: pd.Series) -> dict:
    """Compute descriptive stats for a numeric series."""
    clean = series.dropna()
    return {
        "mean": clean.mean(),
        "median": clean.median(),
        "mode": clean.mode()[0] if len(clean.mode()) > 0 else np.nan,
        "std": clean.std(),
        "min": clean.min(),
        "max": clean.max(),
        "q1": clean.quantile(0.25),
        "q3": clean.quantile(0.75),
    }


def create_correlation_matrix(df: pd.DataFrame, method: str = "pearson") -> np.ndarray:
    """Compute correlation matrix (only numeric columns).
    
    Handles missing data by dropping rows pairwise for each correlation.
    """
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.shape[1] < 2:
        return None
    
    n_cols = numeric_df.shape[1]
    corr_matrix = np.zeros((n_cols, n_cols))
    col_names = numeric_df.columns.tolist()
    
    for i in range(n_cols):
        for j in range(n_cols):
            if i == j:
                corr_matrix[i, j] = 1.0
            else:
                # Drop rows where either column has NaN (pairwise deletion)
                valid_mask = numeric_df.iloc[:, i].notna() & numeric_df.iloc[:, j].notna()
                valid_data_i = numeric_df.iloc[:, i][valid_mask].values
                valid_data_j = numeric_df.iloc[:, j][valid_mask].values
                
                if len(valid_data_i) > 1:  # Need at least 2 points for correlation
                    if method == "spearman":
                        corr, _ = spearmanr(valid_data_i, valid_data_j)
                    else:  # pearson
                        corr = np.corrcoef(valid_data_i, valid_data_j)[0, 1]
                    corr_matrix[i, j] = corr if not np.isnan(corr) else 0.0
                else:
                    corr_matrix[i, j] = 0.0
    
    return corr_matrix


def create_app() -> Dash:
    app = Dash(__name__)

    demo_df = px.data.tips()

    app.layout = html.Div([
        html.H2("📊 EDA Dashboard — Exploratory Data Analysis", style={"textAlign": "center", "marginBottom": 20}),

        # Store for dataframe
        dcc.Store(id="eda-df-store", data=demo_df.to_json(date_format="iso", orient="split")),
        dcc.Store(id="eda-numeric-cols-store"),
        dcc.Store(id="eda-categorical-cols-store"),

        # Upload section
        html.Div([
            html.Div([
                html.Label("Upload CSV/Excel file:", style={"fontWeight": "bold", "marginBottom": 8}),
                dcc.Upload(
                    id="eda-upload-data",
                    children=html.Div(["Drag & drop file or click to select"]),
                    style={
                        "width": "100%",
                        "height": "50px",
                        "lineHeight": "50px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "marginBottom": 8,
                    },
                    multiple=False,
                ),
                html.Div(id="eda-upload-filename", style={"fontSize": 12, "color": "#666"}),
            ], style={"flex": "1", "minWidth": "200px"}),

            html.Div(
                id="eda-data-summary",
                style={"fontSize": 12, "color": "#444", "marginLeft": 20, "minWidth": "150px"}
            ),
        ], style={"display": "flex", "gap": 20, "margin": "24px", "marginBottom": 12, "alignItems": "flex-start"}),

        html.Hr(),

        # Tabs
        dcc.Tabs(id="eda-tabs", value="tab-1", children=[
            # ===== TAB 1: PLOT =====
            dcc.Tab(label="📈 Plot", value="tab-1", children=[
                html.Div([
                    # Left: graph
                    html.Div([
                        dcc.Loading(dcc.Graph(id="eda-plot-graph", 
                                              style={"height": "80vh"}, 
                                              config={"displaylogo": False, 
                                                      "modeBarButtonsToRemove": ["lasso2d", "select2d"]}
                                                      ), 
                                    type="default"),
                    ], style={"flex": "1"}),

                    # Right: controls
                    html.Div([
                        html.Label("Plot type", style={"fontWeight": "bold"}),
                        dcc.Dropdown(
                            id="eda-plot-type",
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

                        html.Div([html.Label("X"), 
                                  dcc.Dropdown(id="eda-plot-x-column")], 
                                  id="eda-plot-x-container", 
                                  style={"marginBottom": 8}),
                        html.Div([html.Label("Y"), 
                                  dcc.Dropdown(id="eda-plot-y-column")], 
                                  id="eda-plot-y-container", 
                                  style={"marginBottom": 8}),
                        html.Div([html.Label("Color"), 
                                  dcc.Dropdown(id="eda-plot-color-column")], 
                                  id="eda-plot-color-container", 
                                  style={"marginBottom": 8}),
                        html.Div([html.Label("Size"), 
                                  dcc.Dropdown(id="eda-plot-size-column")], 
                                  id="eda-plot-size-container", 
                                  style={"marginBottom": 8}),
                    ], style={"width": "320px", "flex": "0 0 320px", "paddingLeft": 12}),

                ], style={"display": "flex", "alignItems": "flex-start", "gap": "24px", "margin": 24}),
            ]),

            # ===== TAB 2: DATA TABLE =====
            dcc.Tab(label="📋 Data Table", value="tab-2", children=[
                html.Div([
                    html.Div(id="eda-table-summary", style={"marginBottom": 12, "fontSize": 12, "color": "#666"}),
                    dcc.Loading(
                        id="eda-table-loading",
                        children=[
                            html.Div(
                                id="eda-data-table-container",
                                style={"overflowX": "auto", "maxHeight": "85vh"}
                            )
                        ],
                        type="default"
                    ),
                ], style={"margin": 24}),
            ]),

            # ===== TAB 3: COLUMN INSPECTOR =====
            dcc.Tab(label="🔍 Inspector", value="tab-3", children=[
                html.Div([
                    html.Div([
                        html.Label("Select column to inspect:", style={"fontWeight": "bold"}),
                        dcc.Dropdown(id="eda-inspector-column", style={"marginBottom": 12}),
                    ], style={"maxWidth": "400px"}),

                    html.Div(id="eda-inspector-missing-alert", style={"marginBottom": 12}),

                    html.Div([
                        html.Div(id="eda-inspector-stats", style={"flex": "0 0 350px", "marginRight": 24}),
                        html.Div(id="eda-inspector-plot", style={"flex": "1"}),
                    ], style={"display": "flex", "gap": 12, "alignItems": "flex-start"}),
                ], style={"margin": 24}),
            ]),

            # ===== TAB 4: CORRELATIONS =====
            dcc.Tab(label="📊 Correlations", value="tab-4", children=[
                html.Div([
                    html.Div([
                        html.Label("Correlation method:", style={"fontWeight": "bold"}),
                        dcc.RadioItems(
                            id="eda-corr-method",
                            options=[
                                {"label": " Pearson", "value": "pearson"},
                                {"label": " Spearman", "value": "spearman"},
                            ],
                            value="pearson",
                            inline=True,
                            style={"marginBottom": 20}
                        ),
                    ], style={"maxWidth": "400px"}),

                    dcc.Loading(
                        dcc.Graph(id="eda-corr-heatmap", 
                                  style={"height": "85vh"}, 
                                  config={"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]}),
                        type="default"
                    ),
                ], style={"margin": 24}),
            ]),
        ]),
    ])

    # ===== CALLBACKS =====

    @app.callback(
        Output("eda-df-store", "data"),
        Output("eda-upload-filename", "children"),
        Output("eda-data-summary", "children"),
        Input("eda-upload-data", "contents"),
        State("eda-upload-data", "filename"),
        State("eda-df-store", "data"),
    )
    def handle_eda_upload(contents, filename, current_json):
        if contents is None:
            df = safe_read_json(current_json)
            return current_json, "Using example dataset", f"{len(df)} rows × {len(df.columns)} columns"
        try:
            df = parse_upload(contents, filename)
            return df.to_json(date_format="iso", orient="split"), f"✓ Loaded: {filename}", f"{len(df)} rows × {len(df.columns)} columns"
        except Exception as e:
            return current_json, f"❌ Upload failed: {e}", ""

    @app.callback(
        Output("eda-numeric-cols-store", "data"),
        Output("eda-categorical-cols-store", "data"),
        Input("eda-df-store", "data"),
    )
    def update_column_type_stores(df_json):
        df = safe_read_json(df_json)
        numeric, categorical = infer_column_types(df)
        return numeric, categorical

    # ===== TAB 1: PLOT CALLBACKS =====

    @app.callback(
        Output("eda-plot-x-column", "options"),
        Output("eda-plot-y-column", "options"),
        Output("eda-plot-color-column", "options"),
        Output("eda-plot-size-column", "options"),
        Output("eda-plot-x-column", "value"),
        Output("eda-plot-y-column", "value"),
        Output("eda-plot-color-column", "value"),
        Output("eda-plot-size-column", "value"),
        Input("eda-df-store", "data"),
        Input("eda-plot-type", "value"),
    )
    def eda_update_plot_options(df_json, plot_type):
        df = safe_read_json(df_json)
        numeric, categorical = infer_column_types(df)

        all_options = [{"label": c, "value": c} for c in df.columns]

        if plot_type == "scatter":
            x_opts = [{"label": c, "value": c} for c in numeric]
            y_opts = [{"label": c, "value": c} for c in numeric]
            size_opts = [{"label": c, "value": c} for c in numeric]
            color_opts = all_options
        elif plot_type in ("box", "violin"):
            x_opts = [{"label": c, "value": c} for c in categorical]
            y_opts = [{"label": c, "value": c} for c in numeric]
            size_opts = []
            color_opts = all_options
        elif plot_type == "bar":
            x_opts = [{"label": c, "value": c} for c in categorical]
            y_opts = [{"label": c, "value": c} for c in numeric]
            size_opts = []
            color_opts = all_options
        elif plot_type == "hist":
            x_opts = [{"label": c, "value": c} for c in numeric + categorical]
            y_opts = []
            size_opts = []
            color_opts = all_options
        else:
            x_opts = all_options
            y_opts = all_options
            size_opts = all_options
            color_opts = all_options

        def first_or_none(opts):
            return opts[0]["value"] if opts else None

        return x_opts, y_opts, color_opts, size_opts, first_or_none(x_opts), first_or_none(y_opts), None, None

    @app.callback(
        Output("eda-plot-size-container", "style"),
        Output("eda-plot-y-container", "style"),
        Input("eda-plot-type", "value"),
    )
    def eda_toggle_plot_visibility(plot_type):
        size_style = {"display": "none"} if plot_type in ("box", "violin") else {}
        y_style = {"display": "none"} if plot_type == "hist" else {}
        return size_style, y_style

    @app.callback(
        Output("eda-plot-graph", "figure"),
        Input("eda-df-store", "data"),
        Input("eda-plot-type", "value"),
        Input("eda-plot-x-column", "value"),
        Input("eda-plot-y-column", "value"),
        Input("eda-plot-color-column", "value"),
        Input("eda-plot-size-column", "value"),
    )
    def eda_update_plot(df_json, plot_type, x, y, color, size):
        df = safe_read_json(df_json)

        if df is None or df.shape[0] == 0:
            return {}

        try:
            if plot_type == "scatter":
                if not x or not y:
                    return px.scatter(df, title="Select X and Y columns")
                fig = px.scatter(df, x=x, y=y, 
                                 color=color if color else None, 
                                 size=size if size else None, 
                                 hover_data=df.columns)
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
                fig = px.scatter(df, x=x, y=y)

            fig.update_layout(transition_duration=200)
            return fig
        except Exception as e:
            return px.scatter(title=f"Error: {e}")

    # ===== TAB 2: DATA TABLE CALLBACKS =====

    @app.callback(
        Output("eda-table-summary", "children"),
        Input("eda-df-store", "data"),
    )
    def eda_update_table_summary(df_json):
        df = safe_read_json(df_json)
        return f"Showing {len(df)} rows × {len(df.columns)} columns"

    @app.callback(
        Output("eda-data-table-container", "children"),
        Input("eda-df-store", "data"),
    )
    def eda_update_data_table(df_json):
        from dash import dash_table

        df = safe_read_json(df_json)
        return dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": i, "id": i} for i in df.columns],
            style_cell={"textAlign": "left", "padding": "8px"},
            style_header={"backgroundColor": "#f0f0f0", "fontWeight": "bold", "borderBottom": "2px solid #ccc"},
            style_data={"border": "1px solid #eee"},
            page_size=20,
            filter_action="native",
            sort_action="native",
            page_action="native",
        )

    # ===== TAB 3: INSPECTOR CALLBACKS =====

    @app.callback(
        Output("eda-inspector-column", "options"),
        Output("eda-inspector-column", "value"),
        Input("eda-df-store", "data"),
    )
    def eda_update_inspector_columns(df_json):
        df = safe_read_json(df_json)
        opts = [{"label": c, "value": c} for c in df.columns]
        return opts, df.columns[0] if len(df.columns) > 0 else None

    @app.callback(
        Output("eda-inspector-missing-alert", "children"),
        Input("eda-df-store", "data"),
        Input("eda-inspector-column", "value"),
    )
    def eda_update_inspector_missing(df_json, column):
        if not column:
            return ""

        df = safe_read_json(df_json)
        missing_count = df[column].isna().sum()
        missing_pct = (missing_count / len(df)) * 100

        if missing_count > 0:
            return html.Div(
                [
                    html.Span(f"⚠️ Missing: {missing_count} ({missing_pct:.1f}%)", 
                              style={"color": "#d9534f", "fontWeight": "bold"}),
                ],
                style={"padding": "12px", 
                       "backgroundColor": "#fff3cd", 
                       "borderRadius": "5px", 
                       "borderLeft": "4px solid #d9534f"}
            )
        return ""

    @app.callback(
        Output("eda-inspector-stats", "children"),
        Input("eda-df-store", "data"),
        Input("eda-inspector-column", "value"),
        Input("eda-numeric-cols-store", "data"),
        Input("eda-categorical-cols-store", "data"),
    )
    def eda_update_inspector_stats(df_json, column, numeric_cols, categorical_cols):
        if not column:
            return ""

        df = safe_read_json(df_json)

        if column in numeric_cols:
            stats = compute_numeric_stats(df[column])
            return html.Div([
                html.H4(f"📊 {column}", style={"marginBottom": 12}),
                html.P(f"Type: Numeric"),
                html.Hr(),
                html.P([html.Strong("Mean: "), f"{stats['mean']:.2f}"]),
                html.P([html.Strong("Median: "), f"{stats['median']:.2f}"]),
                html.P([html.Strong("Mode: "), f"{stats['mode']:.2f}" if not np.isnan(stats['mode']) else "N/A"]),
                html.P([html.Strong("Std Dev: "), f"{stats['std']:.2f}"]),
                html.P([html.Strong("Min: "), f"{stats['min']:.2f}"]),
                html.P([html.Strong("Max: "), f"{stats['max']:.2f}"]),
                html.P([html.Strong("Q1: "), f"{stats['q1']:.2f}"]),
                html.P([html.Strong("Q3: "), f"{stats['q3']:.2f}"]),
                html.P([html.Strong("IQR: "), f"{stats['q3'] - stats['q1']:.2f}"]),
            ], style={"padding": "12px", "backgroundColor": "#f9f9f9", "borderRadius": "5px"})
        else:
            value_counts = df[column].value_counts()
            rows = [html.Tr([html.Td(f"{val}:", style={"fontWeight": "bold"}), 
                             html.Td(f"{count} ({count/len(df)*100:.1f}%)")]) for val, count in value_counts.head(10).items()]
            return html.Div([
                html.H4(f"📊 {column}", style={"marginBottom": 12}),
                html.P(f"Type: Categorical ({len(df[column].unique())} unique values)"),
                html.Hr(),
                html.Table(rows, style={"width": "100%", "fontSize": 12}),
            ], style={"padding": "12px", "backgroundColor": "#f9f9f9", "borderRadius": "5px"})

    @app.callback(
        Output("eda-inspector-plot", "children"),
        Input("eda-df-store", "data"),
        Input("eda-inspector-column", "value"),
        Input("eda-numeric-cols-store", "data"),
    )
    def eda_update_inspector_plot(df_json, column, numeric_cols):
        if not column:
            return ""

        df = safe_read_json(df_json)

        if column in numeric_cols:
            fig = px.histogram(df, x=column, nbins=30, title=f"Distribution of {column}")
        else:
            fig = px.bar(df[column].value_counts(), title=f"Value Counts for {column}")

        fig.update_layout(height=500)
        return dcc.Graph(figure=fig)

    # ===== TAB 4: CORRELATION CALLBACKS =====

    @app.callback(
        Output("eda-corr-heatmap", "figure"),
        Input("eda-df-store", "data"),
        Input("eda-corr-method", "value"),
        Input("eda-numeric-cols-store", "data"),
    )
    def eda_update_corr_heatmap(df_json, method, numeric_cols):
        df = safe_read_json(df_json)
        numeric_df = df[numeric_cols]

        if numeric_df.shape[1] < 2:
            return px.scatter(title="Need at least 2 numeric columns to compute correlations")

        corr_matrix = create_correlation_matrix(df, method=method)
        col_names = numeric_df.columns.tolist()

        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix,
            x=col_names,
            y=col_names,
            colorscale=[
                [0, "#d73027"],      # red for -1
                [0.5, "#f7f7f7"],    # white for 0
                [1, "#1a9850"],      # green for 1
            ],
            zmid=0,
            zmin=-1,
            zmax=1,
            text=np.round(corr_matrix, 2),
            texttemplate="%{text:.2f}",
            textfont={"size": 10},
            colorbar={"title": "Correlation"},
        ))

        fig.update_layout(
            title=f"Pairwise Correlations ({method.capitalize()})",
            height=700,
            xaxis={"side": "bottom"},
            yaxis={"autorange": "reversed"},  # Invert y-axis so identity line goes top-left to bottom-right
        )

        return fig

    return app


if __name__ == "__main__":
    import os
    app = create_app()
    port = int(os.environ.get("DASH_PORT", 8050))
    app.run(debug=True, port=port, host="0.0.0.0")
