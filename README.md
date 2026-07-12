# Traffic Spatiotemporal Analysis Platform

A PySide6 desktop application for interactive analysis and visualization of spatiotemporal traffic datasets.

## Requirements

- Python 3.9 or later
- Dependencies listed in `requirements.txt`

## Installation

```bash
python -m pip install -r requirements.txt
```

## Run

Run the application from the project directory:

```bash
python main.py
```

The default data directory is `datasets/`. Relative data paths are resolved from the project root, so the application does not depend on machine-specific absolute paths.

## Project structure

```text
main.py
README.md
requirements.txt
datasets/
src/
  traffic_analysis/
    app.py
    data_loader.py
    dataset_profiles.py
    preprocessing.py
    analysis.py
    clustering.py
    anomaly_detection.py
    forecasting.py
    ui/
      main_window.ui
      ui_mainwindow.py
```

## Main features

- Automatic MAT, NPY, and NPZ discovery and validation
- Dataset-aware dates, units, entity names, and zero-value policies
- Daily profiles, heatmaps, rankings, distributions, and correlations
- K-Means clustering and historical Z-score anomaly detection
- Chronological forecasting evaluation and missing-value imputation tests
- Bounded computations for large datasets such as California PeMS
- In-memory chart display with optional user-selected PNG export

## Qt Designer

Edit `src/traffic_analysis/ui/main_window.ui`, then regenerate the Python UI module:

```bash
pyside6-uic src/traffic_analysis/ui/main_window.ui -o src/traffic_analysis/ui/ui_mainwindow.py
```

Do not edit `ui_mainwindow.py` manually.
