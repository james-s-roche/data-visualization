# Data Visualization Tools

A comprehensive suite of interactive data exploration and visualization tools built with **Dash** and **Plotly**. Choose between a lightweight plotter or a full-featured EDA dashboard.


## **Simple Plotter** (`simple_plotter.py`)
Very basic script to generate interactive html files. Dynamically adjust x, y, color and size variables of a scatterplot for quick visualizations. Useful for easily generating images (save html with command line or use the UI to save PNG images after defining styling attributes). 

## 🎯 Two Applications

### 1. **Dash Plotter** (`dash_plotter.py`)
A focused tool for interactive plotting with multiple plot types and dynamic column selection.
Initial implementation with limited features. 

**Features:**
- Upload CSV files or use built-in datasets
- Multiple plot types (Scatter, Box, Bar, Histogram, Violin)
- Dynamic column selection based on data types
- Intelligent UI (selectors hide/show based on plot type)
- Responsive layout (graph left, controls right)

### 2. **EDA Dashboard** (`eda_dashboard.py`) ⭐ **COMPREHENSIVE**
A full-featured exploratory data analysis dashboard with four specialized tabs.

**Features:**
- **Tab 1 — Plot** — Interactive plotting (same as Dash Plotter)
- **Tab 2 — Data Table** — Browse raw data with sorting, filtering, pagination
- **Tab 3 — Inspector** — Analyze individual columns:
  - **Numeric columns:** Mean, Median, Mode, IQR, Std Dev, Min/Max, Histogram
  - **Categorical columns:** Value counts with percentages, Bar chart
  - **Both:** Missing value detection 
- **Tab 4 — Correlations** — Pairwise correlation heatmap with Pearson/Spearman methods
  - Conditional formatting
  - Toggle between Pearson and Spearman correlations
**Features:**
- 📈 **Tab 1 — Plot** — Interactive plotting (same as Dash Plotter)
- 📋 **Tab 2 — Data Table** — Browse raw data with sorting, filtering, pagination
- 🔍 **Tab 3 — Inspector** — Analyze individual columns with stats and visualizations
- 📊 **Tab 4 — Correlations** — Pairwise correlation heatmap with Pearson/Spearman
- 📁 Single file upload for all tabs
- 🎨 Responsive, professional UI

## Installation & Setup

### Option 1: Docker (Recommended) 🐳

**Prerequisites:**
- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop))

**Quick Start:**
```bash
cd /Users/james/code/portfolio/data_exploration
docker-compose up --build
```

Then open:
- **EDA Dashboard:** http://localhost:8050
- **Dash Plotter:** http://localhost:8051

For detailed Docker commands and troubleshooting, see [DOCKER_SETUP.md](DOCKER_SETUP.md).

### Option 2: Local Python Environment

**Prerequisites:**
- Python 3.7+
- pip

**Setup:**
```bash
cd /Users/james/code/portfolio/data_exploration

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### With Docker
```bash
docker-compose up --build
```

### With Python

**Run EDA Dashboard (Recommended):**
```bash
python eda_dashboard.py
```
Open: http://127.0.0.1:8050

**Run Dash Plotter:**
```bash
python dash_plotter.py
```
Open: http://127.0.0.1:8050

### Workflow

1. **Load Data** — Upload a CSV file or use the default `tips` dataset
2. **Select Tool** — Choose from 4 tabs in EDA Dashboard or plot types in Dash Plotter
3. **Configure** — Pick columns and visualization options
4. **Analyze** — Explore your data interactively

### Example Data

The app ships with the built-in `tips` dataset from Plotly. To use your own CSV:
- Ensure your CSV has headers in the first row
- Numeric columns are used for axes (X, Y) and size
- Categorical columns (text, low-cardinality numeric) are used for X in Box/Violin or Bar plots

## Project Structure

```
data-visualization/
├── eda_dashboard.py         # ⭐ Full-featured EDA dashboard (4 tabs)
├── dash_plotter.py          # Lightweight interactive plotter
├── simple_plotter.py        # CLI-based Plotly scatter plotter
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker container definition
├── docker-compose.yml      # Multi-service Docker setup
├── DOCKER_SETUP.md         # Docker usage guide
├── README.md               # This file
└── .gitignore             # Git ignore rules
```

## Dependencies

- **dash** — Web framework for interactive apps
- **pandas** — Data manipulation and analysis
- **plotly** — Interactive graphing library
- **scipy** — Scientific computing (for Spearman correlations)

See `requirements.txt` for dependency list.

## Tips & Tricks

**General:**
- **Numeric Column Threshold** — Columns with ≤ 20 unique values are treated as categorical. Feel free to modify **def infer_column_types()**
- **Custom Port** — For running both apps simultaneously or multiple instances. Change the port by modifying the `app.run()` call:
  ```python
  app.run(debug=True, port=8051)
  ```
- **Production Deployment** — Use Gunicorn: `gunicorn app:server`

**EDA Dashboard:**
- **Correlations Tab** — Spearman is better for non-linear relationships; Pearson is better for linear relationships
- **Data Table Tab** — Click column headers to sort; use the search box to filter rows. Numeric accepts filters or exact values or <, <=, >, >=
- **Missing Values** — The Inspector shows missing value % clearly; check all columns before analysis. Useful for imputation.

**Dash Plotter:**
- **Empty Dropdowns** — If controls are empty, the plot type may not support that parameter, 
- **Color by Category** — Use the Color dropdown to add a third dimension to scatter plots
## Troubleshooting

**ModuleNotFoundError: No module named 'dash' (or 'scipy', 'plotly', etc.)**
- Ensure you've created and activated a virtual environment
- Run: `pip install -r requirements.txt`

**Port 8050 already in use**
- Kill the process on port 8050, or
- Change the port: `app.run(debug=True, port=8051)`
- Or find which process is using it: `lsof -i :8050` (macOS/Linux)

**CSV Upload not working**
- Check that your file is UTF-8 encoded
- Ensure the first row contains column headers
- Check browser console (F12) for error details

**EDA Dashboard — Correlation tab shows "Need at least 2 numeric columns"**
- Your dataset may have only 1 numeric column or mostly categorical data
- Use the Inspector tab to check column types

**Slow performance with large datasets**
- DataTable pagination is set to 20 rows per page; adjust in `eda_dashboard.py` if needed
- Consider downsampling very large CSV files before upload
- TODO: test and implement WebGL 

## Contributing

Ideas for enhancements:
- Support for Excel, JSON, Parquet file formats
- Outlier detection and removal tools
- Data quality report (duplicates, missing patterns, etc.)
- Distribution comparison across multiple columns
- Export plots as PNG/SVG
- Data validation and cleaning tools
- Add regression lines to scatter plots
- Column correlation filtering (hide weak correlations)
- Support for factor plots for higher dimensionality visualization
- Support for aggregations 
- Export code used generate plot for use elsewhere
- Additional plot types (heatmaps, 3D, marginal distributions)  
- Better support for time series data

## License

This project is open source. Feel free to use, modify, and share!

---

**Built with  Dash, Plotly, Pandas, and Scipy**

