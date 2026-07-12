# Traffic Spatiotemporal Analysis Platform

A desktop traffic-data analysis application built with Qt Designer, PySide6, NumPy, pandas, SciPy, and Matplotlib. The application uses a single entry point and keeps analysis results in memory. Files are written only when the user explicitly saves a chart.

## Project structure

```text
.
├── main.py                         # Single application entry point
├── README.md
├── requirements.txt
├── datasets/                       # Source datasets and original metadata
└── src/
    ├── __init__.py
    └── traffic_analysis/
        ├── __init__.py
        ├── app.py                  # PySide6 controller and interactive charts
        ├── data_loader.py          # Discovery, loading, validation, reshaping
        ├── dataset_profiles.py     # Dataset-specific semantics and defaults
        ├── preprocessing.py        # Missing values, indexes, imputation
        ├── analysis.py             # Descriptive and correlation analysis
        ├── clustering.py           # K-Means road/entity clustering
        ├── anomaly_detection.py    # Historical Z-score anomaly detection
        ├── forecasting.py          # HA, linear regression, optional GRU
        └── ui/
            ├── __init__.py
            ├── main_window.ui      # Qt Designer source
            └── ui_mainwindow.py    # Generated PySide6 UI module
```

## Installation

Python 3.9 or later is recommended.

```powershell
python -m pip install -r requirements.txt
```

## Run

```powershell
python main.py
```

The configured environment can run the application with:

```powershell
D:\miniconda\envs\lora\python.exe main.py
```

## Workflow

1. Select or refresh the `datasets` directory.
2. Hover over a data source to inspect its type, unit, date mode, and zero-value policy.
3. Select a source. Variables such as `tensor` and `arr_0` are selected automatically.
4. Review the dynamically configured date, entity, cluster, anomaly, and missing-value settings.
5. Click **Load and Analyze Current Data**.
6. Switch among the ten dynamically named charts. The chart, result table, summary, and inspection tabs update together.
7. Use **Save Current Chart as PNG** only when a local image is required.

## Dataset-aware behavior

- Known absolute dates are configured per dataset. Unknown dates use `Day 001`, `Day 002`, and so on.
- Weekday/weekend comparisons are disabled when absolute dates are unavailable.
- Zero-value handling changes by data semantics and remains user-configurable.
- Two-dimensional continuous time series are reshaped using common daily resolutions.
- NYC origin-destination tensors are converted to `(OD pair, day, time slot)`.
- Large California tensors retain all entities for descriptive statistics, ranking, clustering, and profiles. Correlation, distribution, anomaly detail, and imputation evaluation use bounded computations to prevent memory exhaustion.
- Graph CSV files, adjacency matrices, and notebook helper tables are not presented as analysis-ready time-series sources.

All 25 analysis-ready data files in the repository have passed the complete analysis workflow.

## Regenerate the Qt module

After changing the Designer file, run:

```powershell
pyside6-uic src/traffic_analysis/ui/main_window.ui -o src/traffic_analysis/ui/ui_mainwindow.py
```

Do not edit `ui_mainwindow.py` manually; edit `main_window.ui` and regenerate it instead.
