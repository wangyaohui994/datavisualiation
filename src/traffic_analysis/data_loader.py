"""Dataset discovery/loading with strict traffic-tensor validation."""
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from scipy.io import loadmat

SUPPORTED = (".npz", ".npy", ".mat", ".csv", ".tsv")
PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class TrafficDataset:
    tensor: np.ndarray
    variable_name: str
    source: Path
    raw_statistics: Dict[str, Any]


def scan_datasets(base_dir="datasets"):
    base = Path(base_dir)
    if not base.is_absolute():
        base = PROJECT_ROOT / base
    return sorted(str(p) for p in base.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED) if base.exists() else []


def inspect_array(a: np.ndarray) -> Dict[str, Any]:
    finite = a[np.isfinite(a)]
    return {"shape": list(a.shape), "ndim": a.ndim, "dtype": str(a.dtype),
            "min": float(np.min(finite)) if finite.size else None,
            "max": float(np.max(finite)) if finite.size else None,
            "mean": float(np.mean(finite)) if finite.size else None,
            "median": float(np.median(finite)) if finite.size else None,
            "std": float(np.std(finite)) if finite.size else None,
            "zero_count": int(np.sum(a == 0)), "zero_ratio": float(np.mean(a == 0)),
            "nan_count": int(np.isnan(a).sum()), "nan_ratio": float(np.isnan(a).mean())}


def load_traffic_tensor(path, variable="tensor", expected_shape: Optional[tuple] = None, allow_2d=False) -> TrafficDataset:
    """Load a numeric (road, day, time-slot) tensor from MAT/NPY/NPZ."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Data file does not exist: {p}")
    if p.suffix.lower() == ".mat":
        content = {k: v for k, v in loadmat(p).items() if not k.startswith("__")}
        if variable not in content:
            raise KeyError(f"Variable {variable!r} does not exist; available variables: {list(content)}")
        a = content[variable]
    elif p.suffix.lower() == ".npy":
        a = np.load(p, mmap_mode="r", allow_pickle=False)
        variable = p.stem
    elif p.suffix.lower() == ".npz":
        with np.load(p, allow_pickle=False) as z:
            key = variable if variable in z.files else (z.files[0] if len(z.files) == 1 else None)
            if key is None:
                raise KeyError(f"Variable {variable!r} does not exist; available variables: {z.files}")
            a, variable = z[key], key
    else:
        raise ValueError(f"Unsupported traffic tensor file type: {p.suffix}")
    a = np.asarray(a)
    raw_stats = inspect_array(a)
    # NYC tensors encode (origin zone, destination zone, continuous time).
    # Convert them to the common (OD pair, day, intraday slot) representation.
    if a.ndim == 3 and "NYC-data-set" in str(p) and a.shape[2] > 1000:
        slots = 48 if a.shape[2] % 48 == 0 else (24 if a.shape[2] % 24 == 0 else None)
        if slots:
            target=(a.shape[0]*a.shape[1],a.shape[2]//slots,slots)
            a=a.reshape(target)
            raw_stats["automatic_reshape"]={"from":raw_stats["shape"],"to":list(target),"slots_per_day":slots,
                                             "meaning":"OD pair x day x intraday slot"}
    if a.ndim == 2 and allow_2d:
        # Common traffic resolutions: 5, 10, 15 minutes, NGSIM-style 100 slots,
        # or hourly. The first exact factor is used and reported in the UI.
        slots = next((v for v in (288, 144, 96, 100, 24) if a.shape[1] % v == 0), None)
        if slots is None:
            raise ValueError(f"Cannot infer daily slots for 2-D data {a.shape}; it may be an adjacency matrix rather than time-series data.")
        a = a.reshape(a.shape[0], a.shape[1] // slots, slots)
        raw_stats["automatic_reshape"] = {"from": raw_stats["shape"], "to": list(a.shape), "slots_per_day": slots}
    if a.ndim != 3:
        raise ValueError(f"Expected 3-D (entity, day, time slot) data; received {a.shape}")
    if not np.issubdtype(a.dtype, np.number):
        raise TypeError(f"Data must be numeric; received {a.dtype}")
    if expected_shape and tuple(a.shape) != tuple(expected_shape):
        raise ValueError(f"Expected shape {expected_shape}; received {a.shape}")
    return TrafficDataset(a.astype(float, copy=True), variable, p, raw_stats)


# Compatibility API used by the desktop viewer.
def load_data(path):
    p, ext = Path(path), Path(path).suffix.lower()
    try:
        if ext == ".npy":
            a = np.load(p, mmap_mode="r", allow_pickle=False); return {"type": "array", "content": a, "meta": inspect_array(a)}
        if ext in (".npz", ".mat"):
            if ext == ".npz":
                with np.load(p, allow_pickle=False) as z: content = {k: z[k] for k in z.files}
            else: content = {k: v for k, v in loadmat(p).items() if not k.startswith("__")}
            return {"type": "archive", "content": content, "meta": {k: inspect_array(v) for k, v in content.items()}}
        if ext in (".csv", ".tsv"):
            df = pd.read_csv(p, sep="\t" if ext == ".tsv" else ",")
            return {"type": "table", "content": df, "meta": {"rows": len(df), "columns": len(df.columns)}}
        raise ValueError(f"Unsupported file type: {ext}")
    except Exception as exc:
        return {"type": "error", "error": str(exc), "meta": {}}
