# Dash Plotter — Interactive Data Visualization

A lightweight, interactive web application for exploratory data analysis using **Dash** and **Plotly**. Upload CSV files or use built-in datasets, select from multiple plot types, and dynamically adjust visualization parameters.

## Features

✨ **Key Capabilities:**
- 📁 **Upload CSV files** — Load your own data (client-side upload)
- 📊 **Multiple plot types** — Scatter, Box, Bar, Histogram, and Violin plots
- 🎯 **Dynamic column selection** — Dropdowns auto-populate based on data types (numeric vs. categorical)
- 🔄 **Intelligent UI** — Selectors hide/show based on plot type (e.g., Size hidden for Box/Violin, Y hidden for Histogram)
- 🎨 **Responsive design** — Graph on the left, controls stacked vertically on the right
- 🚀 **Fast & reactive** — Real-time plot updates powered by Plotly Express

## Installation

### Prerequisites
- Python 3.7+
- pip

### Setup

1. **Clone or navigate to the repository:**
   ```bash
   cd data-visualization
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the App

Start the Dash server:
```bash
python dash_plotter.py
```

Then open your browser to:
```
http://127.0.0.1:8050
```

### Workflow

1. **Load Data** — Drag & drop a CSV file onto the upload area, or use the default `tips` dataset
2. **Choose Plot Type** — Select from the Plot Type dropdown (Scatter, Box, Bar, Histogram, Violin)
3. **Configure Axes** — Pick X, Y (if applicable), Color, and Size columns from the auto-populated dropdowns
4. **Visualize** — The plot updates in real-time as you change parameters

### Example Data

The app ships with the built-in `tips` dataset from Plotly. To use your own CSV:
- Ensure your CSV has headers in the first row
- Numeric columns are used for axes (X, Y) and size
- Categorical columns (text, low-cardinality numeric) are used for X in Box/Violin or Bar plots

## Project Structure

```
data-visualization/
├── dash_plotter.py          # Main Dash application
├── simple_plotter.py        # CLI-based Plotly scatter plotter (optional)
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── .gitignore             # Git ignore rules
```

## Dependencies

- **dash** — Web framework for interactive apps
- **pandas** — Data manipulation and analysis
- **plotly** — Interactive graphing library

See `requirements.txt` for pinned versions.

## Tips & Tricks

- **Numeric Column Threshold** — Columns with ≤ 20 unique values are treated as categorical for better plot selection
- **Empty Dropdowns** — If Y or Size dropdowns appear empty, the selected plot type may not support that parameter
- **Custom CSS** — Modify `app.layout` in `dash_plotter.py` to customize styles
- **Production Deployment** — For production, use a WSGI server like Gunicorn: `gunicorn app:server`

## Troubleshooting

**ModuleNotFoundError: No module named 'dash'**
- Ensure dependencies are installed: `pip install -r requirements.txt`

**Port 8050 already in use**
- Change the port in the last line of `dash_plotter.py`:
  ```python
  app.run(debug=True, port=8051)
  ```

**Upload not working**
- Ensure the file is a valid CSV (UTF-8 encoding recommended)
- Check browser console for detailed error messages

## Contributing

Feel free to fork and submit pull requests! Ideas for enhancements:
- Save/download plots as PNG or SVG
- Add data filtering and aggregation options
- Support for other file formats (Excel, JSON, etc.)
- Advanced statistics and regression lines

## License

This project is open source. Feel free to use and modify as needed.

---

**Built with** ❤️ **using Dash, Plotly, and Pandas**
