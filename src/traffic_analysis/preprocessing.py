"""Traffic tensor cleaning, indexing and imputation."""
from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class TrafficIndices:
    dates: pd.DatetimeIndex
    times: list
    date_labels: list
    has_absolute_dates: bool


def preprocess_tensor(tensor, start_date=None, zero_as_missing=True):
    """Copy tensor and optionally map zeros to NaN.

    Assumption: in these speed tensors an exact 0 usually means a missing sensor
    observation rather than a truly stopped road. Set zero_as_missing=False to
    retain zeros when that assumption is inappropriate.
    """
    x = np.asarray(tensor, dtype=float).copy()
    if zero_as_missing:
        x[x == 0] = np.nan
    slots = x.shape[2]
    absolute = start_date is not None
    dates = pd.date_range(start_date or "2000-01-03", periods=x.shape[1], freq="D")
    date_labels = dates.strftime("%Y-%m-%d").tolist() if absolute else [f"Day {i+1:03d}" for i in range(x.shape[1])]
    minutes = np.arange(slots) * (24 * 60 / slots)
    times = [f"{int(m // 60):02d}:{int(m % 60):02d}" for m in minutes]
    return x, TrafficIndices(dates, times, date_labels, absolute)


def temporal_linear_interpolation(x):
    out = np.asarray(x, float).copy()
    for r in range(out.shape[0]):
        s = pd.Series(out[r].reshape(-1))
        out[r] = s.interpolate(limit_direction="both").to_numpy().reshape(out.shape[1:])
    return out


def historical_mean_imputation(x):
    """Fill from the same road/time-slot mean across days, then global mean."""
    out = np.asarray(x, float).copy()
    means = np.nanmean(out, axis=1, keepdims=True)
    means = np.where(np.isnan(means), np.nanmean(out), means)
    return np.where(np.isnan(out), means, out)


def knn_imputation(x, k=5):
    """Simple road-neighbour KNN fill based on mean daily profiles."""
    out = np.asarray(x, float).copy()
    profiles = np.nanmean(out, axis=1)
    fallback = historical_mean_imputation(out)
    for road in np.where(np.isnan(out).any(axis=(1, 2)))[0]:
        overlap = np.isfinite(profiles[road])[None, :] & np.isfinite(profiles)
        count = overlap.sum(axis=1)
        dist = np.sqrt(np.nansum(np.where(overlap, profiles - profiles[road], 0) ** 2, axis=1) / np.maximum(count, 1))
        dist[(count == 0) | (np.arange(len(out)) == road)] = np.inf
        neighbours = np.argsort(dist)[:k]
        estimate = np.nanmean(out[neighbours], axis=0)
        missing = np.isnan(out[road])
        out[road][missing] = estimate[missing]
        out[road][np.isnan(out[road])] = fallback[road][np.isnan(out[road])]
    return out


def evaluate_imputation(x, method="linear", mask_ratio=.05, seed=42, k=5):
    rng = np.random.default_rng(seed); observed = np.argwhere(np.isfinite(x))
    chosen = observed[rng.choice(len(observed), max(1, int(len(observed) * mask_ratio)), replace=False)]
    masked = np.asarray(x, float).copy(); truth = masked[tuple(chosen.T)]; masked[tuple(chosen.T)] = np.nan
    funcs = {"linear": temporal_linear_interpolation, "historical_mean": historical_mean_imputation,
             "knn": lambda a: knn_imputation(a, k)}
    if method not in funcs: raise ValueError(f"Unknown imputation method: {method}")
    pred = funcs[method](masked)[tuple(chosen.T)]; valid = np.isfinite(pred)
    return funcs[method](x), {"method": method, "masked_count": int(len(truth)),
        "MAE": float(np.mean(np.abs(pred[valid]-truth[valid]))),
        "RMSE": float(np.sqrt(np.mean((pred[valid]-truth[valid])**2))), "coverage": float(valid.mean())}
