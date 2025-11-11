"""Simple Plotter

Usage:
  python simple_plotter.py [-i csv_path] [-o output.html]

Produces an interactive Plotly scatter plot with dropdowns for selecting
which columns to use for x, y, color, size and theme. Saves an HTML file when
`-o/--out` is provided, otherwise opens the generated HTML in the default
web browser.

If no csv_path is provided the script will use Plotly's built-in `iris` dataset.

Output is fully encapsualted interactive html file for data exploration
Use dash_plotter.py to run web_server with additional functionality


Dependencies: pandas, plotly
Install: pip install pandas plotly
"""

from __future__ import annotations

import argparse
import tempfile
import webbrowser
from pathlib import Path
from typing import List

import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import plotly.io as pio


def load_data(csv_path: str | None) -> pd.DataFrame:
	"""Load a DataFrame from CSV or return a default sample dataset.

	Args:
		csv_path: Path to CSV file or None.

	Returns:
		DataFrame with the loaded data.
	"""
	if csv_path:
		df = pd.read_csv(csv_path)
	else:
		# Use Plotly's example iris dataset as a sensible default
		df = px.data.iris()
	# Reset index to provide a stable text label if needed
	df = df.reset_index(drop=True)
	return df


def is_numeric_series(s: pd.Series) -> bool:
	try:
		return pd.api.types.is_numeric_dtype(s)
	except Exception:
		return False


def make_scatter_with_dropdowns(df: pd.DataFrame, default_x: str = None, default_y: str = None) -> go.Figure:
	"""Create a Plotly Figure with dropdowns for x, y, color and size.

	This implementation embeds arrays for each column into button `args` so
	that the pure HTML file is fully interactive without any server.
	"""
	cols: List[str] = list(df.columns)
	# Choose defaults: first two numeric columns or first two columns
	numeric_cols = [c for c in cols if is_numeric_series(df[c])]
	if default_x is None:
		default_x = numeric_cols[0] if len(numeric_cols) >= 1 else cols[0]
	if default_y is None:
		default_y = numeric_cols[1] if len(numeric_cols) >= 2 else (cols[1] if len(cols) > 1 else cols[0])

	default_color = default_x if default_x != default_y else (numeric_cols[0] if numeric_cols else cols[0])

	# Prepare the base scatter trace
	marker_kwargs = dict(size=10)
	# initial color
	marker_kwargs["color"] = df[default_color].tolist()

	trace = go.Scatter(
		x=df[default_x].tolist(),
		y=df[default_y].tolist(),
		mode="markers",
		marker=marker_kwargs,
		# text=[str(i) for i in df.index],
		# hovertemplate="%{text}<br>X: %{x}<br>Y: %{y}<extra></extra>",
	)

	fig = go.Figure(data=[trace])

	# Build updatemenus (dropdowns)
	updatemenus = []

	# Helper to create buttons for a property
	def make_buttons_for_attr(
		attr_path: str,
		transform=lambda col: col.tolist(),
		method: str = "restyle",
		relayout_fn: Optional[Callable[[str], dict]] = None,
		extra_payload: Optional[dict] = None,
		):
		"""
		Build button dicts for updatemenu.

		- attr_path: e.g. "x", "y", "marker.color", "marker.size"
		- transform: function(series) -> list (how to extract the column values)
		- method: "restyle" | "update" | "relayout"
		- "restyle": args = [restyle_dict, [0]]  (change trace attributes for trace 0)
		- "update": args = [restyle_dict, relayout_dict]  (change trace data AND layout)
		- "relayout": args = [relayout_dict]  (change layout only)
		- relayout_fn: callable(col_name) -> dict to be used as relayout_dict (only for "update"/"relayout")
		- extra_payload: dict of additional restyle items; values may be callables that accept col_name
		"""
		buttons = []
		for col in cols:
			arr = transform(df[col])

			# Build restyle dict only when relevant
			restyle_dict = None
			if method in ("restyle", "update"):
				restyle_dict = {attr_path: [arr]}  # wrap in list for per-trace values
				if extra_payload:
					for k, v in extra_payload.items():
						restyle_dict[k] = v(col) if callable(v) else v

			if method == "restyle":
				args = [restyle_dict, [0]] 
			elif method == "update":
				relayout = relayout_fn(col) if relayout_fn else {}  # layout updates (axis titles, annotations, etc.)
				args = [restyle_dict, relayout]
			elif method == "relayout":
				relayout = relayout_fn(col) if relayout_fn else {}
				# args = [relayout]
				args = [[0], relayout]
			else:
				# fallback to restyle behavior
				args = [restyle_dict, [0]]

			buttons.append({"method": method, "label": col, "args": args})
		return buttons

	positions = {"x": 0.0,
			  	 "y": 0.2,
			  	 "color": 0.4,
			  	 "size": 0.6,
			  	 "theme": 0.8}
	
	# X dropdown
	x_buttons = make_buttons_for_attr(
		"x",
		transform=lambda s: s.astype(str).tolist() if not is_numeric_series(s) else s.tolist(),
		method="update",
		relayout_fn=lambda col: {'xaxis': {'title': {'text': col}}}
	)
	updatemenus.append(dict(active=cols.index(default_x), 
								buttons=x_buttons, 
								x=positions["x"], 
								xanchor="left", 
								y=1.1, 
								direction="down", 
								showactive=True)
								)

	# Y dropdown
	y_buttons = make_buttons_for_attr(
		"y",
		transform=lambda s: s.astype(str).tolist() if not is_numeric_series(s) else s.tolist(),
		method="update",
		relayout_fn=lambda col: {'yaxis': {'title': {'text': col}}}
	)
	updatemenus.append(dict(active=cols.index(default_y), 
						    buttons=y_buttons, 
							x=positions["y"], 
							xanchor="left", 
							y=1.05, 
							direction="down", 
							showactive=True))

	# Color dropdown
	def color_payload(col_name: str):
		s = df[col_name]
		if is_numeric_series(s):
			return {"marker.colorscale": "Viridis", "marker.showscale": True}
		else:
			return {"marker.colorscale": None, "marker.showscale": False}

	color_buttons = make_buttons_for_attr("marker.color", lambda s: s.tolist(), extra_payload={"marker.colorscale": lambda col: ("Viridis" if is_numeric_series(df[col]) else None), "marker.showscale": lambda col: (True if is_numeric_series(df[col]) else False)})
	default_color_index = cols.index(default_color) if default_color in cols else 0
	updatemenus.append(dict(active=default_color_index, 
						    buttons=color_buttons, 
							x=positions["color"], 
							xanchor="left", 
							y=1.1, 
							direction="down", 
							showactive=True)
							)

	# Size dropdown: for non-numeric columns use a constant size (10). Otherwise scale to resonable sizes (5-25)
	def size_transform(s: pd.Series):
		if not is_numeric_series(s):
			return [10] * len(s)
		arr = s.astype(float)
		rng = arr.max() - arr.min()
		if rng == 0 or pd.isna(rng):
			return [10] * len(arr)
		scaled = 5 + ((arr - arr.min()) / rng) * 20
		return scaled.tolist()

	size_buttons = make_buttons_for_attr("marker.size", size_transform)
	updatemenus.append(dict(active=0, 
						    buttons=size_buttons, 
							x=positions["size"], 
							xanchor="left", 
							y=1.1, 
							direction="down", 
							showactive=True)
							)
	
	# Theme dropdown (plotly templates)
	theme_buttons = []
	for t in pio.templates:
		theme_buttons.append({
			"method": "relayout",
			"label": t,
			"args": [{"template": pio.templates[t]}],
		})

	updatemenus.append(dict(active=0, 
						    buttons=theme_buttons, 
							x=positions["theme"], 
							xanchor="left", 
							y=1.1, 
							direction="down", 
							showactive=True)
							)
	# set theme to match at start
	fig.update_layout()

	# Include labels for each button
	annotations = [
		dict(text="X:", x=positions["x"] - 0.015, xref="paper", y=1.02, yref="paper", showarrow=False, xanchor="left", yanchor="middle"),
		dict(text="Y:", x=positions["y"] - 0.015, xref="paper", y=1.02, yref="paper", showarrow=False, xanchor="left", yanchor="middle"),
		dict(text="Color:", x=positions["color"] - 0.03, xref="paper", y=1.02, yref="paper", showarrow=False, xanchor="left", yanchor="middle"),
		dict(text="Size:", x=positions["size"] - 0.025, xref="paper", y=1.02, yref="paper", showarrow=False, xanchor="left", yanchor="middle"),
		dict(text="Theme:", x=positions["theme"] - 0.04, xref="paper", y=1.02, yref="paper", showarrow=False, xanchor="left", yanchor="middle"),
	]

	fig.update_layout(
		updatemenus=updatemenus,
		annotations=annotations,
		margin=dict(t=120),
		title_text="Interactive scatter — choose columns from dropdowns",
	)

	fig.update_xaxes(title_text=default_x)
	fig.update_yaxes(title_text=default_y)

	return fig


def parse_args(argv=None):
	p = argparse.ArgumentParser(description="Create an interactive scatter plot from a CSV with dropdowns for axes, color and size.")
	p.add_argument("-i", "--input", nargs="?", 
				   help="Path to CSV file. If omitted, a sample dataset is used.")
	p.add_argument("-o", "--out", 
				   help="Output HTML file path. If omitted the HTML is opened in the browser.")
	return p.parse_args(argv)


def main(argv=None):
	args = parse_args(argv)
	df = load_data(args.input)

	# Build figure
	fig = make_scatter_with_dropdowns(df)
	if args.out:
		out_path = Path(args.out)
		fig.write_html(out_path, 
					   include_plotlyjs="cdn",
					   config= {'displaylogo': False,
				 	   			'modeBarButtonsToRemove': ['lasso2d','select2d']
				 })
		print(f"Saved interactive plot to: {out_path}")
	else:
		# save to a temporary file and open it. 
		with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
			tmp_path = Path(tmp.name)
		fig.write_html(tmp_path, 
				       include_plotlyjs="cdn",
					   config= {'displaylogo': False})
		print(f"Opening interactive plot: {tmp_path}")
		webbrowser.open(tmp_path.as_uri())


if __name__ == "__main__":
	main()

