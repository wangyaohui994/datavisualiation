"""PySide6 controller: all analyses and figures are displayed in memory."""
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import whosmat
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QDate
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from .ui.ui_mainwindow import Ui_MainWindow
from .data_loader import load_traffic_tensor, scan_datasets
from .preprocessing import preprocess_tensor, evaluate_imputation
from .analysis import (daily_profile, weekday_weekend_profiles, road_statistics,
                      select_typical_road, date_statistics, distribution_statistics,
                      road_correlations)
from .clustering import kmeans_road_profiles
from .anomaly_detection import detect_anomalies
from .forecasting import evaluate_baselines
from .dataset_profiles import profile_for

plt.rcParams.update({"font.family":"sans-serif", "font.sans-serif":["Microsoft YaHei","SimHei","Noto Sans SC","DejaVu Sans"],
                     "axes.unicode_minus":False})
warnings.filterwarnings("ignore",message="Mean of empty slice",category=RuntimeWarning)
warnings.filterwarnings("ignore",message="Degrees of freedom <= 0 for slice",category=RuntimeWarning)

CHARTS = ["Mean Daily Speed Profile", "Weekday vs Weekend", "Entity Day-by-Time Heatmap",
          "Day Entity-by-Time Heatmap", "Entity Mean Ranking", "Daily Network Mean",
          "Distribution and Box Plot", "Entity Correlation Heatmap", "Entity K-Means Centers", "Anomaly Distribution"]


def chart_labels(profile):
    e,k=profile.entity,profile.kind
    return [f"Mean Daily {k} Profile", f"Weekday vs Weekend {k}", f"Selected {e} Day-by-Time Heatmap",
            f"Selected Day {e}-by-Time Heatmap", f"{e} Mean {k} Ranking", f"Daily Overall Mean {k}",
            f"{k} Distribution and Box Plot", f"{e} Correlation Heatmap", f"{e} K-Means Centers", f"{k} Anomaly Distribution"]


class DataFrameModel(QAbstractTableModel):
    def __init__(self): super().__init__(); self.frame=pd.DataFrame()
    def set_frame(self,frame): self.beginResetModel(); self.frame=frame.iloc[:5000,:200].copy(); self.endResetModel()
    def rowCount(self,parent=QModelIndex()): return 0 if parent.isValid() else len(self.frame)
    def columnCount(self,parent=QModelIndex()): return 0 if parent.isValid() else len(self.frame.columns)
    def data(self,index,role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole or not index.isValid(): return None
        value=self.frame.iat[index.row(),index.column()]
        if isinstance(value,(float,np.floating)): return "NaN" if np.isnan(value) else f"{value:.6g}"
        return str(value)
    def headerData(self,section,orientation,role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole: return None
        return str(self.frame.columns[section]) if orientation==Qt.Orientation.Horizontal else str(self.frame.index[section])


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.ui=Ui_MainWindow(); self.ui.setupUi(self)
        self.file_paths=[]; self.selected_variable=None; self.profile=None; self.dataset=None; self.x=None; self.indices=None; self.results={}
        self.figure=Figure(constrained_layout=True); self.canvas=FigureCanvasQTAgg(self.figure)
        self.ui.plotLayout.addWidget(NavigationToolbar2QT(self.canvas,self)); self.ui.plotLayout.addWidget(self.canvas)
        self.model=DataFrameModel(); self.ui.tableView.setModel(self.model); self.ui.splitter.setSizes([350,1090])
        self.ui.chartList.addItems(CHARTS); self.ui.chartList.setEnabled(False); self._connect(); self.refresh_sources()

    def _connect(self):
        self.ui.browseButton.clicked.connect(self.choose_directory); self.ui.refreshButton.clicked.connect(self.refresh_sources)
        self.ui.fileList.currentRowChanged.connect(self.source_changed); self.ui.analyzeButton.clicked.connect(self.analyze)
        self.ui.chartList.currentRowChanged.connect(self.show_chart); self.ui.saveFigureButton.clicked.connect(self.save_figure)
        self.ui.typicalCombo.currentIndexChanged.connect(lambda i:self.ui.roadSpin.setEnabled(i==0))
        self.ui.roadSpin.valueChanged.connect(self._parameter_redraw); self.ui.dateSpin.valueChanged.connect(self._parameter_redraw)
        self.ui.clusterSpin.valueChanged.connect(self._cluster_changed)

    def choose_directory(self):
        path=QFileDialog.getExistingDirectory(self,"Select Data Directory",self.ui.dirEdit.text())
        if path: self.ui.dirEdit.setText(path); self.refresh_sources()

    def refresh_sources(self):
        root=Path(self.ui.dirEdit.text().strip() or "datasets")
        # Show analysis tensors only. Graph/adjacency and notebook helper tables
        # are supporting metadata, not road-speed time series.
        self.file_paths=[p for p in scan_datasets(root) if Path(p).suffix.lower() in (".mat",".npy",".npz")
                         and "graph" not in Path(p).name.lower() and not Path(p).stem.endswith("_A")]
        self.ui.fileList.clear()
        for p in self.file_paths:
            try: label=str(Path(p).relative_to(root))
            except ValueError: label=p
            self.ui.fileList.addItem(label)
            item=self.ui.fileList.item(self.ui.fileList.count()-1); profile=profile_for(p)
            date_text=f"Absolute start date: {profile.start_date}" if profile.start_date else "Absolute date unknown: using Day 001, Day 002, and so on"
            zero_text="Zero is treated as suspected missing by default" if profile.zero_as_missing else "Zero is retained as a valid observation by default"
            item.setToolTip(f"<b>{profile.entity} {profile.kind}</b> | Unit: {profile.unit}<br>{date_text}<br>{profile.note}<br>{zero_text}")
        self.statusBar().showMessage(f"Found {len(self.file_paths)} analysis-ready data files.")
        preferred=next((i for i,p in enumerate(self.file_paths) if "Guangzhou-data-set" in p and p.endswith("tensor.mat")),0)
        if self.file_paths: self.ui.fileList.setCurrentRow(preferred)

    def source_changed(self,row):
        self.selected_variable=None; self.dataset=None; self.x=None; self.results={}; self.ui.chartList.setEnabled(False)
        # Do not leave the previous source's chart visible while the new source
        # has not been analysed yet.
        self.figure.clear(); ax=self.figure.add_subplot(111)
        ax.text(.5,.5,"Data source changed. Click 'Load and Analyze Current Data'.",ha="center",va="center",transform=ax.transAxes)
        ax.axis("off"); self.canvas.draw_idle(); self.model.set_frame(pd.DataFrame())
        if not 0<=row<len(self.file_paths): return
        p=Path(self.file_paths[row])
        try:
            if p.suffix.lower()==".mat": names=[name for name,shape,dtype in whosmat(p) if len(shape) in (2,3)]
            elif p.suffix.lower()==".npz":
                with np.load(p,allow_pickle=False) as z: names=[k for k in z.files if z[k].ndim in (2,3)]
            elif p.suffix.lower()==".npy": names=[p.stem]
            else: names=[]
            preferred=next((n for n in ("tensor","arr_0") if n in names),names[0] if names else None)
            self.selected_variable=preferred
            self.profile=profile_for(p); self.ui.zeroMissingCheck.setChecked(self.profile.zero_as_missing)
            for i,label in enumerate(chart_labels(self.profile)): self.ui.chartList.item(i).setText(label)
            self.ui.roadLabel.setText(f"{self.profile.entity} ID"); self.ui.typicalLabel.setText(f"Auto {self.profile.entity}")
            self.ui.typicalCombo.setItemText(0,f"Manual {self.profile.entity} ID")
            self.ui.typicalCombo.setItemText(1,f"Lowest mean {self.profile.kind}")
            self.ui.typicalCombo.setItemText(2,f"Highest mean {self.profile.kind}")
            self.ui.typicalCombo.setItemText(3,"Closest to overall mean")
            self.ui.zeroMissingCheck.setText(f"Treat zero as suspected missing (default: {'yes' if self.profile.zero_as_missing else 'no'})")
            self.ui.zeroMissingCheck.setToolTip(self.profile.note); self.ui.zSpin.setValue(self.profile.z_threshold)
            if self.profile.start_date:
                self.ui.startDateEdit.setDate(QDate.fromString(self.profile.start_date,"yyyy-MM-dd")); self.ui.startDateEdit.setEnabled(True)
                date_text=f"Start date: {self.profile.start_date}"
            else:
                self.ui.startDateEdit.setEnabled(False); date_text="Absolute date unknown: using relative day labels"
            if not names: self.ui.analyzeButton.setEnabled(False)
            else: self.ui.analyzeButton.setEnabled(True)
            self.statusBar().showMessage(f"Selected {p.name}. Click 'Load and Analyze Current Data'.")
        except Exception as exc: self.ui.analyzeButton.setEnabled(False); QMessageBox.warning(self,"Cannot Inspect Data Source",str(exc))

    def analyze(self):
        row=self.ui.fileList.currentRow()
        if not 0<=row<len(self.file_paths): return
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor); self.ui.analyzeButton.setEnabled(False)
        self.statusBar().showMessage("Computing analysis results in memory..."); QApplication.processEvents()
        try:
            self.dataset=load_traffic_tensor(self.file_paths[row],self.selected_variable,allow_2d=True)
            start=self.ui.startDateEdit.date().toString("yyyy-MM-dd") if self.profile.start_date else None
            self.x,self.indices=preprocess_tensor(self.dataset.tensor,start,self.ui.zeroMissingCheck.isChecked())
            self.ui.roadSpin.setMaximum(self.x.shape[0]-1); self.ui.dateSpin.setMaximum(self.x.shape[1]-1); self.ui.clusterSpin.setMaximum(self.x.shape[0])
            self.ui.clusterSpin.blockSignals(True); self.ui.clusterSpin.setValue(min(self.x.shape[0],6 if self.x.shape[0]>=1000 else 4)); self.ui.clusterSpin.blockSignals(False)
            self._calculate_results(); self._show_quality(); self._show_summary()
            self.ui.chartList.setEnabled(True)
            # Preserve the user's selected chart type across data sources and
            # redraw explicitly even when the row number did not change.
            chart_row=self.ui.chartList.currentRow()
            if chart_row < 0: chart_row=0; self.ui.chartList.setCurrentRow(chart_row)
            self.show_chart(chart_row); self.ui.resultTabs.setCurrentIndex(0)
            self.statusBar().showMessage(f"Analysis complete: {Path(self.dataset.source).name} / {self.dataset.variable_name}. Results remain in memory.")
        except Exception as exc:
            QMessageBox.critical(self,"Analysis Failed",str(exc))
        finally: QApplication.restoreOverrideCursor(); self.ui.analyzeButton.setEnabled(True)

    def _calculate_results(self):
        x,idx=self.x,self.indices
        profile=daily_profile(x,idx.times)
        if idx.has_absolute_dates: ww,wws=weekday_weekend_profiles(x,idx.dates,idx.times)
        else:
            ww=pd.DataFrame(columns=["group","time","mean_speed_kmh"])
            wws=pd.DataFrame([{"note":"The data source has no absolute dates; weekday/weekend classification is unavailable."}])
        roads=road_statistics(x); dates,date_summary=date_statistics(x,idx.date_labels)
        corr_limit=400; corr_ids=np.arange(x.shape[0]) if x.shape[0]<=corr_limit else np.linspace(0,x.shape[0]-1,corr_limit,dtype=int)
        corr,corr_summary=road_correlations(x[corr_ids])
        for item in corr_summary.values(): item["road_1"],item["road_2"]=int(corr_ids[item["road_1"]]),int(corr_ids[item["road_2"]])
        clusters,centers,counts=kmeans_road_profiles(x,self.ui.clusterSpin.value())
        anomalies,_=detect_anomalies(x,idx.date_labels,idx.times,self.ui.zSpin.value(),max_records=100000,return_z=False)
        forecasts,split=evaluate_baselines(np.nanmean(x,axis=0,keepdims=True),12,1)
        # Imputation assessment is statistically sampled; filling a full large
        # tensor several times is unnecessary for an error estimate.
        imp_ids=np.arange(x.shape[0]) if x.shape[0]<=200 else np.linspace(0,x.shape[0]-1,200,dtype=int)
        _,imputation=evaluate_imputation(x[imp_ids],"historical_mean",.01,42)
        self.results=dict(profile=profile,weekday=ww,weekday_summary=wws,roads=roads,dates=dates,date_summary=date_summary,
                          distribution=distribution_statistics(x.ravel()[::max(1,x.size//2000000)]),corr=corr,corr_ids=corr_ids,corr_summary=corr_summary,clusters=clusters,
                          centers=centers,cluster_counts=counts,anomalies=anomalies,forecasts=forecasts,split=split,imputation=imputation)

    def _selected_road(self):
        modes={1:"lowest",2:"highest",3:"closest"}
        return select_typical_road(self.x,modes[self.ui.typicalCombo.currentIndex()]) if self.ui.typicalCombo.currentIndex() else self.ui.roadSpin.value()

    def _parameter_redraw(self):
        if self.x is not None and self.ui.chartList.currentRow() in (2,3): self.show_chart(self.ui.chartList.currentRow())

    def _cluster_changed(self):
        if self.x is None: return
        clusters,centers,counts=kmeans_road_profiles(self.x,self.ui.clusterSpin.value()); self.results.update(clusters=clusters,centers=centers,cluster_counts=counts)
        self._show_summary()
        if self.ui.chartList.currentRow()==8: self.show_chart(8)

    def _time_ticks(self,ax):
        times=self.indices.times; pos=np.arange(0,len(times),max(1,len(times)//8)); ax.set_xticks(pos,[times[i] for i in pos],rotation=30)

    def show_chart(self,row):
        if self.x is None or not 0<=row<self.ui.chartList.count(): return
        self.figure.clear(); table=pd.DataFrame(); r=self.results; unit=self.profile.unit; entity=self.profile.entity
        chart_title=self.ui.chartList.item(row).text()
        if row==0:
            ax=self.figure.add_subplot(111); ax.plot(r["profile"].mean_speed_kmh,label=f"Overall mean {self.profile.kind}"); self._time_ticks(ax); ax.set(title=chart_title,xlabel="Time",ylabel=f"{self.profile.kind} ({unit})"); ax.legend(); table=r["profile"]
        elif row==1:
            ax=self.figure.add_subplot(111)
            for name,g in r["weekday"].groupby("group",sort=False): ax.plot(g.mean_speed_kmh.to_numpy(),label=name)
            self._time_ticks(ax); ax.set(title=chart_title,xlabel="Time",ylabel=f"{self.profile.kind} ({unit})")
            if len(r["weekday"]): ax.legend()
            else: ax.text(.5,.5,"No reliable absolute dates; weekday/weekend comparison is unavailable.",ha="center",va="center",transform=ax.transAxes)
            table=r["weekday_summary"]
        elif row in (2,3):
            ax=self.figure.add_subplot(111)
            if row==2:
                road=self._selected_road(); data=self.x[road]; ylabels=self.indices.date_labels; title=f"{entity} {road}: Day-by-Time {self.profile.kind} Heatmap"; ylabel="Day"
            else:
                day=self.ui.dateSpin.value(); data=self.x[:,day,:]; ylabels=[str(i) for i in range(self.x.shape[0])]; title=f"{self.indices.date_labels[day]}: {entity}-by-Time {self.profile.kind} Heatmap"; ylabel=f"{entity} ID"
            im=ax.imshow(data,aspect="auto",interpolation="nearest",cmap="viridis"); self._time_ticks(ax); yp=np.arange(0,len(ylabels),max(1,len(ylabels)//10)); ax.set_yticks(yp,[ylabels[i] for i in yp]); ax.set(title=title,xlabel="Time",ylabel=ylabel); self.figure.colorbar(im,ax=ax,label=f"{self.profile.kind} ({unit})"); table=pd.DataFrame(data)
        elif row==4:
            axes=self.figure.subplots(1,2); low=r["roads"].nsmallest(15,"mean_speed_kmh"); high=r["roads"].nlargest(15,"mean_speed_kmh").sort_values("mean_speed_kmh")
            axes[0].barh(low.road_id.astype(str),low.mean_speed_kmh,color="#d84315"); axes[0].invert_yaxis(); axes[0].set(title=f"Lowest Mean {self.profile.kind} {entity}s",xlabel=unit,ylabel=f"{entity} ID")
            axes[1].barh(high.road_id.astype(str),high.mean_speed_kmh,color="#2e7d32"); axes[1].set(title=f"Highest Mean {self.profile.kind} {entity}s",xlabel=unit,ylabel=f"{entity} ID"); table=r["roads"]
        elif row==5:
            ax=self.figure.add_subplot(111); ax.plot(r["dates"].date,r["dates"].mean_speed_kmh,marker="o",ms=3); ax.tick_params(axis="x",rotation=60); ax.set(title=f"Daily Overall Mean {self.profile.kind}",xlabel="Day",ylabel=f"{self.profile.kind} ({unit})"); table=r["dates"]
        elif row==6:
            axes=self.figure.subplots(1,2); sample=self.x.ravel()[::max(1,self.x.size//2000000)]; a=sample[np.isfinite(sample)]; axes[0].hist(a,bins=60,color="#1976d2"); axes[0].set(title=f"{self.profile.kind} Histogram (sampled for large data)",xlabel=unit,ylabel="Frequency"); axes[1].boxplot(a,vert=False); axes[1].set(title=f"{self.profile.kind} Box Plot",xlabel=unit,yticks=[]); table=pd.DataFrame([r["distribution"]])
        elif row==7:
            ax=self.figure.add_subplot(111); im=ax.imshow(r["corr"],vmin=-1,vmax=1,cmap="coolwarm"); ax.set(title=f"{chart_title} ({len(r['corr_ids'])} representative {entity}s)",xlabel=f"Sampled {entity} index",ylabel=f"Sampled {entity} index"); self.figure.colorbar(im,ax=ax,label="Pearson correlation"); table=pd.DataFrame(r["corr"],index=r["corr_ids"],columns=r["corr_ids"])
        elif row==8:
            ax=self.figure.add_subplot(111)
            for i,c in enumerate(r["centers"]): ax.plot(c,label=f"Cluster {i}")
            self._time_ticks(ax); ax.set(title=chart_title,xlabel="Time",ylabel=f"Standardized {self.profile.kind} (Z-score)"); ax.legend(); table=r["clusters"]
        else:
            ax=self.figure.add_subplot(111); a=r["anomalies"]; colors={"Anomalous low":"#d32f2f","Anomalous high":"#1976d2","Suspected sensor error":"#7b1fa2"}
            for name,g in a.groupby("anomaly_type"): ax.scatter(g.road_id,g.speed_kmh,s=5,alpha=.35,label=name,color=colors.get(name))
            ax.set(title=chart_title,xlabel=f"{entity} ID",ylabel=f"Anomalous {self.profile.kind} ({unit})")
            if len(a): ax.legend()
            else: ax.text(.5,.5,"No anomalies detected at the current threshold.",ha="center",va="center",transform=ax.transAxes)
            table=a
        self.model.set_frame(table); self.canvas.draw_idle()

    def _show_quality(self):
        s=self.dataset.raw_statistics.copy(); s["zero_handling"]="converted to NaN" if self.ui.zeroMissingCheck.isChecked() else "retained as valid"
        s["dataset_kind"]=self.profile.kind; s["unit"]=self.profile.unit; s["date_mode"]="absolute" if self.indices.has_absolute_dates else "relative_day"
        s["profile_note"]=self.profile.note
        self.ui.qualityText.setPlainText(json.dumps(s,ensure_ascii=False,indent=2))

    def _show_summary(self):
        r=self.results; ds=r["date_summary"]; cs=r["corr_summary"]
        lines=[f"Data source: {self.dataset.source}",f"Auto-selected variable: {self.dataset.variable_name}; shape: {self.dataset.tensor.shape}",
               f"Data type: {self.profile.kind}; unit: {self.profile.unit}; date mode: {'absolute dates' if self.indices.has_absolute_dates else 'relative day index'}",
               f"Zero policy: {'convert to NaN' if self.ui.zeroMissingCheck.isChecked() else 'retain as valid'}","",
               "Weekday / weekend:",r["weekday_summary"].to_string(index=False),"",
               f"Lowest-mean day: {ds['most_congested_date']} ({ds['most_congested_speed_kmh']:.2f} {self.profile.unit})",
               f"Highest-mean day: {ds['most_free_date']} ({ds['most_free_speed_kmh']:.2f} {self.profile.unit})",
               f"Most similar {self.profile.entity}s: {cs['most_similar']}",f"Least similar {self.profile.entity}s: {cs['least_similar']}","",
               f"Cluster sizes by {self.profile.entity}:",r["cluster_counts"].to_string(index=False),"",
               f"Total anomalies: {r['anomalies'].attrs.get('total_count',len(r['anomalies'])):,}; displayed details: {len(r['anomalies']):,}",
               f"Correlation matrix: {len(r['corr_ids']):,} representative objects from {self.x.shape[0]:,} {self.profile.entity}s (bounded to prevent quadratic memory growth).","",
               "Forecast evaluation (strict chronological split):",json.dumps(r["forecasts"],ensure_ascii=False,indent=2),"",
               "Historical-mean imputation masking evaluation:",json.dumps(r["imputation"],ensure_ascii=False,indent=2)]
        self.ui.summaryText.setPlainText("\n".join(lines))

    def save_figure(self):
        if self.x is None: return
        name=self.ui.chartList.currentItem().text() if self.ui.chartList.currentItem() else "analysis_chart"
        path,_=QFileDialog.getSaveFileName(self,"Save Current Chart",f"{name}.png","PNG (*.png)")
        if path: self.figure.savefig(path,dpi=300,bbox_inches="tight"); self.statusBar().showMessage(f"Saved: {path}",5000)


def run_gui():
    app=QApplication.instance() or QApplication(sys.argv); app.setStyle("Fusion"); window=MainWindow(); window.show(); return app.exec()
