# ETS: Holt Winter's Exponential Smoothing (HWES)
import importlib as imp  
import DataPrep; imp.reload(DataPrep)
import DataSource; imp.reload(DataSource)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sklearn.metrics as metrics
import statsmodels.tsa.holtwinters
import scipy.stats

from DataSource import dR, wL, wF, tL, mS, dfname
from DataPrep import df
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from scipy.stats import rankdata
from matplotlib.backends.backend_pdf import PdfPages

# 1 Data Preparation & Models
def fit(dat):
    # ETS to forecast next wF days, check if today <= 25th%tile of 1 + wF days
    # return binary predict of the day and wF days of forecast
    model = ExponentialSmoothing(dat, seasonal_periods=wL, trend='add', seasonal='add')
    model_fit = model.fit()
    yfor = model_fit.forecast(1+wF)
    pct = rankdata(yfor)[0]/(1+wF)
    if pct <= 0.25:
        p = 1.0
    else:
        p = 0.0
    return p, yfor

def getPred(dat):
    pl = []
    yforl = []
    for i in range(dR):
        if i < mS:
            pl.append(float('NaN'))
            yforl.append([])
        else:
            p, yfor = fit(dat['Close'][:i])
            pl.append(p)
            yforl.append(yfor)
    return pl, yforl

def getETS(dat):
    ETS_fpred, yforl = getPred(dat)
    for i in range(mS, dR):
        if i == (dR-1):
            finalyfor = yforl[i]        
        elif i%63 == 0:
            c = pd.concat([pd.Series([float('NaN')] * (i-1)), 
                yforl[i], pd.Series([float('NaN')] * (dR-i-wF))])
            colname = 'ETS_' + str(i)
            c.index = dat.index
            dat.insert(0, colname, c)
    dat.insert(0, 'ETS_fpred', ETS_fpred)  
    return dat, finalyfor

fullDat, finalyfor = getETS(df)

# 2 Visual and Validation
def finalForecast():
    last_date = fullDat.index[-1]
    fd = pd.date_range(last_date, periods=wF+1).tolist()
    fcPreddf = pd.DataFrame({'Forecast':finalyfor.values}, index=fd)
    return fcPreddf

# vis
def getVis():    
    fig, ax = plt.subplots(figsize=(4, 3.5))
    fullDat['Close'].plot(ax=ax, x_compat=True, lw=0.3,
                       title = 'ETS', figsize=(4, 3.5))
    fidf = fullDat.drop(['ETS_fpred', 'Label', 'Close'], axis=1)
    lg = ['Close']
    for i in fidf.columns:        
        lg.append(i)
        fi = fidf[i].dropna()
        fi = fi.plot(ax=ax)
    lg.append('Forecast')
    fcPreddf = finalForecast()
    fcPreddf.plot(ax=ax)
    ax.legend(lg, loc='upper left', prop={'size': 8})
    return fig
vis = getVis()
## feed
def getFeed():
    y = fullDat['Label'][mS:dR-wF] 
    p = fullDat['ETS_fpred'][mS:dR-wF]
    vacc = metrics.accuracy_score(y,p)
    tacc = str(round(vacc*100,1)) + '%'
    vbny = fullDat['ETS_fpred'][-1]
    if vbny == 1:
        tbny = 'Buy'
    else:
        tbny = 'Hold'
    tdate = str(fullDat.index[-1])
    return [tbny, tacc, tdate, vbny, vacc]
feed = getFeed()
## report
def render_mpl_table(data, acc, mse,
                     col_width=2.0, row_height=0.625, font_size=14,
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')
    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)
    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)
    

    for k, cell in mpl_table._cells.items():
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    ax.text(0, 1.5, '(Unsupervised) Multiple ETS Forecast', ha='left', fontsize=font_size, fontweight='bold')
    ax.text(0, 1.3, 'True: Buy -- current price <=25%tile of future(wF) days', ha='left', fontsize=10)
    ax.text(0, 1.1, 'Pred: Buy -- daily ETS in range -' + str(mS) + ':' + str(dR), ha='left', fontsize=10)
    ax.text(0.44, -0.2, acc, ha='left', fontsize=font_size)
    ax.text(0.21, -0.4, mse, ha='left', fontsize=font_size)
    ax.text(0, -0.6, '** Final model uses full data set.', ha='left', fontsize=10)
    ax.text(0, -0.8, '** Buy: day <=25%tile of (last day, wF days ahead).', ha='left', fontsize=10)
    return ax.get_figure(), ax

def getRpt(dat):
    # stock chart
    sc, ax = plt.subplots()    
    dat['Close'].plot(kind='line', legend=True, ax=ax, color='b', marker=',', fontsize=5)
    m = dat['Close'].mean()
    ax.axhline(y=m, color='g', linestyle='--', lw=0.5)
    ax.set_title('<' + dfname + '> rows = ' + str(dR) + ', mean = ' + str(round(m,2)))
    
    # cf_metrics and scores
    yts1 = fullDat['ETS_fpred'].iloc[-mS:-wF].values
    ts_p1 = fullDat['Label'].iloc[-mS:-wF].values
    mse = 'Mean-Squared-Error:                 ' + str(round(metrics.mean_squared_error(yts1, ts_p1),3))
    accuracy = 'Accuracy:                ' + getFeed()[1]
    cf = metrics.confusion_matrix(yts1, ts_p1)
    cf_matrix = pd.DataFrame({'_':['True: Hold', 'True: Buy '],
                          'Pred: Hold':[cf[0,0], cf[1,0]],
                          'Pred: Buy ':[cf[0,1], cf[1,1]]})
    cf_vis = render_mpl_table(cf_matrix, accuracy, mse)[0]

    with PdfPages('./rpt/ETS.pdf') as pdf:
        pdf.savefig(sc, bbox_inches='tight', orientation='landscape')
        pdf.savefig(vis, bbox_inches='tight', orientation='landscape')
        pdf.savefig(cf_vis, bbox_inches='tight', orientation='landscape')
    return
getRpt(df)

# developer check
print('@ETS: ', feed)




