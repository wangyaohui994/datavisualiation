"""Dependency-light K-Means clustering of mean daily road profiles."""
import numpy as np
import pandas as pd


def kmeans_road_profiles(x, n_clusters=4, seed=42, max_iter=200):
    if not 2 <= n_clusters <= x.shape[0]: raise ValueError("The cluster count must be between 2 and the entity count.")
    profiles = np.nanmean(x, axis=1)
    valid = ~np.isnan(profiles).all(axis=1)
    fill = np.nanmean(profiles, axis=0); fill = np.where(np.isnan(fill), 0, fill)
    profiles = np.where(np.isnan(profiles), fill, profiles)
    mu, sd = profiles.mean(axis=1, keepdims=True), profiles.std(axis=1, keepdims=True)
    z = (profiles-mu)/np.where(sd == 0, 1, sd)
    rng=np.random.default_rng(seed); centers=z[rng.choice(len(z), n_clusters, replace=False)].copy()
    labels=np.zeros(len(z), int)
    for _ in range(max_iter):
        new=np.argmin(((z[:,None,:]-centers[None,:,:])**2).sum(axis=2), axis=1)
        if np.array_equal(new, labels) and _ > 0: break
        labels=new
        for k in range(n_clusters):
            members=z[labels==k]
            centers[k]=members.mean(axis=0) if len(members) else z[rng.integers(len(z))]
    result=pd.DataFrame({"road_id":np.arange(len(z)),"cluster":labels,"valid_profile":valid})
    counts=result.groupby("cluster").size().rename("road_count").reset_index()
    return result, centers, counts
