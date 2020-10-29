# Data Preparation
# return df: 'Date' as index, 'Close' & 'Label'
import pandas as pd
import importlib as imp  
import DataSource; imp.reload(DataSource)

from DataSource import dseries, dR, wF
from scipy.stats import rankdata


def getLabel(dat):
    Label = []
    for i in range(len(dat)-wF):
        tmpl = dat.iloc[i:i+wF]
        pct = rankdata(tmpl)[0]/(1+wF)
        pct = round(pct, 3)
        if pct <= 0.25:
            Label.append(1.0)
        else:
            Label.append(0.0)
    for i in range(wF):
        Label.append(0.5)
    return Label

Close = dseries.tail(dR)
Label = getLabel(Close)
df = pd.DataFrame({'Close':Close, 'Label':Label})

# developer check
print('@DataPrep: ', [df.shape]) 