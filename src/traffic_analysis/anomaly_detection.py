"""Historical road/time-position Z-score anomaly detection."""
import numpy as np
import pandas as pd


def detect_anomalies(x, dates, times, z_threshold=3.0, sensor_low=1.0, sensor_high=150.0,
                     max_records=None, batch_roads=256, return_z=True):
    """Detect anomalies in road batches to avoid a second full-tensor allocation.

    ``max_records`` limits UI detail rows while ``total_count`` in DataFrame.attrs
    still reports the exact count across the whole dataset.
    """
    rows=[]; total=0; z_parts=[] if return_z else None
    for start in range(0,x.shape[0],batch_roads):
        block=x[start:start+batch_roads]
        mean=np.nanmean(block,axis=1,keepdims=True); std=np.nanstd(block,axis=1,keepdims=True)
        z=(block-mean)/np.where(std==0,np.nan,std)
        mask=((np.abs(z)>=z_threshold)|(block<sensor_low)|(block>sensor_high))&np.isfinite(block)
        rr,dd,tt=np.where(mask); total += len(rr)
        room=len(rr) if max_records is None else max(0,max_records-len(rows))
        for r,d,t in zip(rr[:room],dd[:room],tt[:room]):
            value=block[r,d,t]; score=z[r,d,t]
            kind="Suspected sensor error" if value<sensor_low or value>sensor_high else ("Anomalous low" if score<0 else "Anomalous high")
            date_value=dates[d].strftime("%Y-%m-%d") if hasattr(dates[d],"strftime") else str(dates[d])
            rows.append((start+r,date_value,times[t],value,score,kind))
        if return_z: z_parts.append(z)
    frame=pd.DataFrame(rows,columns=["road_id","date","time","speed_kmh","z_score","anomaly_type"])
    frame.attrs.update(total_count=total,truncated=(len(frame)<total))
    return frame, (np.concatenate(z_parts) if return_z else None)
