"""Leakage-safe supervised preparation, baselines and optional GRU interface."""
import numpy as np


def make_supervised(x, lookback=12, horizon=1):
    """Flatten days chronologically and return samples shaped (N, lookback, roads)."""
    if lookback < 1 or horizon < 1: raise ValueError("lookback and horizon must be positive integers.")
    series=np.transpose(x,(1,2,0)).reshape(-1,x.shape[0])
    X,y=[],[]
    for end in range(lookback,len(series)-horizon+1):
        X.append(series[end-lookback:end]); y.append(series[end:end+horizon])
    return np.asarray(X),np.asarray(y)


def chronological_split(X,y,train_ratio=.7,val_ratio=.15):
    if train_ratio+val_ratio>=1: raise ValueError("Training and validation ratios must sum to less than 1.")
    n=len(X); a,b=int(n*train_ratio),int(n*(train_ratio+val_ratio))
    return (X[:a],y[:a]),(X[a:b],y[a:b]),(X[b:],y[b:])


def _fill_features(a,means=None):
    if means is None: means=np.nanmean(a,axis=0,keepdims=True)
    return np.where(np.isnan(a),means,a),means


def metrics(y_true,y_pred):
    valid=np.isfinite(y_true)&np.isfinite(y_pred); e=y_pred[valid]-y_true[valid]
    denom=np.abs(y_true[valid]); nz=denom>1e-8
    return {"MAE":float(np.mean(np.abs(e))),"RMSE":float(np.sqrt(np.mean(e**2))),
            "MAPE_percent":float(np.mean(np.abs(e[nz])/denom[nz])*100) if nz.any() else None}


class HistoricalAverage:
    def fit(self,X,y): self.profile=np.nanmean(y,axis=0); return self
    def predict(self,X): return np.broadcast_to(self.profile,(len(X),)+self.profile.shape).copy()


class LinearRegressionForecaster:
    """Multi-output ridge linear regression implemented with NumPy."""
    def __init__(self,alpha=1e-3): self.alpha=alpha
    def fit(self,X,y):
        a=X.reshape(len(X),-1); b=y.reshape(len(y),-1)
        a,self.means=_fill_features(a); self.y_shape=y.shape[1:]
        design=np.c_[np.ones(len(a)),a]; reg=np.eye(design.shape[1])*self.alpha; reg[0,0]=0
        self.coef=np.linalg.solve(design.T@design+reg,design.T@np.nan_to_num(b,nan=np.nanmean(b,axis=0)))
        return self
    def predict(self,X):
        a=X.reshape(len(X),-1); a,_=_fill_features(a,self.means)
        return (np.c_[np.ones(len(a)),a]@self.coef).reshape((len(X),)+self.y_shape)


class GRUForecaster:
    """Optional PyTorch GRU. Import occurs only when this model is requested."""
    def __init__(self,input_size,horizon=1,hidden_size=64,epochs=10,lr=1e-3):
        self.input_size,self.horizon,self.hidden_size,self.epochs,self.lr=input_size,horizon,hidden_size,epochs,lr
    def fit(self,X,y):
        try: import torch; from torch import nn
        except ImportError as exc: raise ImportError("GRU requires the optional PyTorch dependency: pip install torch") from exc
        self.torch=torch
        class Net(nn.Module):
            def __init__(s): super().__init__(); s.gru=nn.GRU(self.input_size,self.hidden_size,batch_first=True); s.fc=nn.Linear(self.hidden_size,self.horizon*self.input_size)
            def forward(s,a): return s.fc(s.gru(a)[0][:,-1]).reshape(-1,self.horizon,self.input_size)
        self.model=Net(); opt=torch.optim.Adam(self.model.parameters(),lr=self.lr); lossfn=nn.L1Loss()
        xf=np.nan_to_num(X,nan=np.nanmean(X)); yf=np.nan_to_num(y,nan=np.nanmean(y))
        tx,ty=torch.tensor(xf,dtype=torch.float32),torch.tensor(yf,dtype=torch.float32)
        self.model.train()
        for _ in range(self.epochs): opt.zero_grad(); loss=lossfn(self.model(tx),ty); loss.backward(); opt.step()
        return self
    def predict(self,X):
        self.model.eval()
        with self.torch.no_grad(): return self.model(self.torch.tensor(np.nan_to_num(X),dtype=self.torch.float32)).numpy()


def evaluate_baselines(x,lookback=12,horizon=1):
    X,y=make_supervised(x,lookback,horizon); train,val,test=chronological_split(X,y)
    results={}
    for name,model in (("Historical Average",HistoricalAverage()),("Linear Regression",LinearRegressionForecaster())):
        model.fit(*train); results[name]={"validation":metrics(val[1],model.predict(val[0])),"test":metrics(test[1],model.predict(test[0]))}
    return results,{"samples":len(X),"train":len(train[0]),"validation":len(val[0]),"test":len(test[0]),"lookback":lookback,"horizon":horizon}
