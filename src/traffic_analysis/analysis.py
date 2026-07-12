"""Descriptive traffic analyses returning tidy tables."""
import numpy as np
import pandas as pd


def daily_profile(x, times):
    return pd.DataFrame({"time": times, "mean_speed_kmh": np.nanmean(x, axis=(0, 1))})


def weekday_weekend_profiles(x, dates, times):
    weekday = np.asarray(dates.weekday < 5)
    rows, summary = [], []
    for name, mask in (("Weekday", weekday), ("Weekend", ~weekday)):
        if not mask.any():
            rows.extend({"group": name, "time": t, "mean_speed_kmh": np.nan} for t in times)
            summary.append({"group": name, "overall_mean_speed_kmh": np.nan,
                            "peak_min_speed_kmh": np.nan, "peak_min_time": "No matching dates"})
            continue
        curve = np.nanmean(x[:, mask, :], axis=(0, 1))
        rows.extend({"group": name, "time": t, "mean_speed_kmh": v} for t, v in zip(times, curve))
        idx = int(np.nanargmin(curve))
        summary.append({"group": name, "overall_mean_speed_kmh": float(np.nanmean(x[:, mask, :])),
                        "peak_min_speed_kmh": float(curve[idx]), "peak_min_time": times[idx]})
    return pd.DataFrame(rows), pd.DataFrame(summary)


def road_statistics(x):
    valid=np.isfinite(x).any(axis=(1,2))
    mean=np.full(x.shape[0],np.nan); minimum=np.full(x.shape[0],np.nan); std=np.full(x.shape[0],np.nan)
    mean[valid]=np.nanmean(x[valid],axis=(1,2)); minimum[valid]=np.nanmin(x[valid],axis=(1,2)); std[valid]=np.nanstd(x[valid],axis=(1,2))
    return pd.DataFrame({"road_id": np.arange(x.shape[0]), "mean_speed_kmh": mean,
        "min_speed_kmh": minimum, "speed_std_kmh": std,
        "suspected_missing_rate": np.isnan(x).mean(axis=(1, 2))})


def select_typical_road(x, mode="closest"):
    means = np.nanmean(x, axis=(1, 2)); valid = np.isfinite(means)
    if not valid.any(): raise ValueError("Every entity contains only NaN values.")
    if mode == "lowest": return int(np.nanargmin(means))
    if mode == "highest": return int(np.nanargmax(means))
    if mode == "closest": return int(np.nanargmin(np.abs(means - np.nanmean(means))))
    raise ValueError("mode must be 'lowest', 'highest', or 'closest'")


def date_statistics(x, dates):
    means = np.nanmean(x, axis=(0, 2))
    labels = dates.strftime("%Y-%m-%d") if hasattr(dates,"strftime") else list(dates)
    table = pd.DataFrame({"date": labels, "mean_speed_kmh": means})
    summary = {"most_congested_date": table.iloc[int(np.nanargmin(means))]["date"],
               "most_congested_speed_kmh": float(np.nanmin(means)),
               "most_free_date": table.iloc[int(np.nanargmax(means))]["date"],
               "most_free_speed_kmh": float(np.nanmax(means))}
    return table, summary


def distribution_statistics(x):
    a = x[np.isfinite(x)]; q1, q3 = np.percentile(a, [25, 75]); iqr = q3-q1
    low, high = q1-1.5*iqr, q3+1.5*iqr
    return {"count": int(a.size), "q1": float(q1), "median": float(np.median(a)), "q3": float(q3),
            "iqr": float(iqr), "lower_outlier_bound": float(low), "upper_outlier_bound": float(high),
            "outlier_count": int(np.sum((a < low) | (a > high)))}


def road_correlations(x):
    flat = x.reshape(x.shape[0], -1)
    # Pairwise-complete correlations; constant/all-NaN roads stay NaN.
    corr = pd.DataFrame(flat.T).corr(min_periods=2).to_numpy()
    pairs=[]
    for i in range(len(corr)):
        for j in range(i+1, len(corr)):
            if np.isfinite(corr[i,j]): pairs.append((corr[i,j], i, j))
    if not pairs: raise ValueError("Insufficient valid entity data to calculate correlations.")
    return corr, {"most_similar": {"road_1": max(pairs)[1], "road_2": max(pairs)[2], "correlation": float(max(pairs)[0])},
                  "least_similar": {"road_1": min(pairs)[1], "road_2": min(pairs)[2], "correlation": float(min(pairs)[0])}}
