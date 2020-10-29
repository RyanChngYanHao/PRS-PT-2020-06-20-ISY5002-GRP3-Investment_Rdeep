# RSI
import importlib as imp  
import DataPrep; imp.reload(DataPrep)
import DataSource; imp.reload(DataSource)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tensorflow.keras
import sklearn.metrics as metrics

from DataSource import dR, wL, wF, tL, dfname
from DataPrep import df
from tensorflow.keras.utils import plot_model
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import Dense, Input
from matplotlib.backends.backend_pdf import PdfPages

# 1. Data Preparation & Calculations
def getDiff(dat):    
    diff = []
    for i in range(dR):
        if i == 0:
            diff.append(float('NaN'))
        else:
            dd = dat.iloc[i]-dat.iloc[i-1] 
            diff.append(dd) 
    return diff

def getGainLoss(dat):
    gain = []
    loss = []
    for j in range(dR):
        if dat[j] >= 0:
            gain.append(dat[j])
            loss.append(0.0)
        elif dat[j] < 0:
            gain.append(0.0)
            loss.append(abs(dat[j]))
        else:
            gain.append(float('NaN'))
            loss.append(float('NaN'))
    return gain, loss

def listRSI(dat, wLi):
    gain = dat[0]
    loss = dat[1]
    avg_gain = []
    avg_loss = []
    RSI_wLi_list = []
    for i in range(len(gain)):        
        if i < wLi:
            RSI_wLi_list.append(float('NaN'))
            avg_gain.append(0.0)
            avg_loss.append(0.0)
        elif i == wL:            
            u = sum(gain[1:wLi+1]) / wLi
            avg_gain.append(u)
            d = sum(loss[1:wLi+1]) / wLi
            avg_loss.append(d)
            if (u == 0 and d == 0):
                RS = 1
            elif d == 0:
                RS = 99
            else:
                RS = u / d               
            RSI = 100 - (100 / (1 + RS))
            RSI_wLi_list.append(RSI)
        else:
            u = (avg_gain[i-1]*(wLi-1) + gain[i])/wLi
            avg_gain.append(u)
            d = (avg_loss[i-1]*(wLi-1) + loss[i])/wLi
            avg_loss.append(d)
            if (u == 0 and d == 0):
                RS = 1
            elif d == 0:
                RS = 99
            else:
                RS = u / d
            RSI = 100 - (100 / (1 + RS))
            RSI_wLi_list.append(RSI)
    return RSI_wLi_list

def getRSI(dat):
    diff = getDiff(dat['Close'])
    gl = getGainLoss(diff)
    for i in range(wF, wL+1):
        RSI_wLi = listRSI(gl, i)
        colname = 'RSI_' + str(i)        
        dat.insert(0, colname, RSI_wLi)
    return dat

def getPred(dat):
    for i in dat.columns:
        for j in range(len(dat)):
            # domain knowledge of under 30 is over sold
            if dat[i][j] <= 30:
                dat[i][j] = 1.0
            else:
                dat[i][j] = 0.0        
    return dat

## Prep Data
fullDat     = getRSI(df)
RSIpred     = getPred(fullDat.iloc[:,:-2])

# 2. Model
## max data with label
labelDat    = fullDat.iloc[wL:dR-wF,:]
RSIpred1    = RSIpred.iloc[wL:dR-wF,:]

Xtr1        = RSIpred1.iloc[:-tL,:]
ytr1        = labelDat.iloc[:-tL,-1]
Xts1        = RSIpred1.iloc[-tL:,:]
yts1        = labelDat.iloc[-tL:,-1]

def fit():
    model = Sequential()
    model.add(Dense(50, activation='relu', input_shape=(RSIpred.shape[1],)))
    model.add(Dense(25, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(optimizer='adam', loss='binary_crossentropy')
    return model

model1      = fit()
model1.fit(Xtr1, ytr1, validation_data=(Xts1, yts1),
              epochs=50, batch_size=wF, shuffle=True)   


tr_p1       = model1.predict(Xtr1)
tr_p1       = tr_p1.round(0)                                                    # convert to binary guess
ts_p1       = model1.predict(Xts1)
ts_p1       = ts_p1.round(0)                                                    # convert to binary guess    

Xtr2        = RSIpred.iloc[wL:dR-wF,:]
ytr2        = fullDat.iloc[wL:dR-wF,-1]
Xts2        = RSIpred.iloc[-wF:,:]

model2      = fit()
model2.fit(Xtr2, ytr2, epochs=50, batch_size=wF, shuffle=True)   

tr_p2       = model2.predict(Xtr2)
tr_p2       = tr_p2.round(0)    
ts_p2       = model2.predict(Xts2)

# 3. Visual and Validation
## vis
def getVis():   
    fig, ax = plt.subplots(figsize=(4, 3.5))
    fullDat.iloc[:,:-2].plot(ax=ax, x_compat=True, lw=0.3,
                         title = 'RSI', figsize=(4, 3.5))    
    ax.axhline(y=70, color='r', linestyle='--', lw=0.3)
    ax.text(fullDat.index[int(dR/2)], 70, 'Over-Bought', fontsize=8)
    ax.axhline(y=30, color='g', linestyle='--', lw=0.3)
    ax.text(fullDat.index[int(dR/2)], 30, 'Over-Sold', fontsize=8)
    if len(fullDat.columns) <= 7:
        lg = fullDat.columns
    else:
        lg = list(fullDat.columns[:2]) + ['...'] + list(fullDat.columns[-4:-2])
    ax.legend(lg, loc='upper left', prop={'size': 8})
    return fig
vis = getVis()
## feed
def getFeed():
    vbny = ts_p2[-1,][0]
    vbny = vbny.round(0)
    if vbny == 1:
        tbny = 'Buy'
    else:
        tbny = 'Hold'
        
    vacc = metrics.accuracy_score(yts1, ts_p1)
    tacc = str(round(vacc*100,1)) + '%'
    
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
    ax.text(0, 1.5, '(Supervised) MLP with different RSIs', ha='left', fontsize=font_size, fontweight='bold')
    ax.text(0, 1.3, 'True: Buy -- current price <=25%tile of future(wF) days', ha='left', fontsize=10)
    ax.text(0, 1.1, 'Pred: Buy -- fed # of RSIs, pressume <=30 as over-sold', ha='left', fontsize=10)
    ax.text(0.44, -0.2, acc, ha='left', fontsize=font_size)
    ax.text(0.21, -0.4, mse, ha='left', fontsize=font_size)
    ax.text(0, -0.6, '** Final model uses full data set, not training set.', ha='left', fontsize=10)
    return ax.get_figure(), ax

def getRpt(dat):
    # stock chart
    sc, ax = plt.subplots()    
    dat['Close'].plot(kind='line', legend=True, ax=ax, color='b', marker=',', fontsize=5)
    m = dat['Close'].mean()
    ax.axhline(y=m, color='g', linestyle='--', lw=0.5)
    ax.set_title('<' + dfname + '> rows = ' + str(dR) + ', mean = ' + str(round(m,2)))
    
    # cf_metrics and scores
    mse = 'Mean-Squared-Error:                ' + str(round(metrics.mean_squared_error(yts1, ts_p1),3))
    accuracy = 'Accuracy:                ' + getFeed()[1]
    cf = metrics.confusion_matrix(yts1, ts_p1)
    cf_matrix = pd.DataFrame({'RSI <= 30':['True: Hold', 'True: Buy '],
                          'Pred: Hold':[cf[0,0], cf[1,0]],
                          'Pred: Buy ':[cf[0,1], cf[1,1]]})
    cf_vis = render_mpl_table(cf_matrix, accuracy, mse)[0]

    with PdfPages('./rpt/RSI.pdf') as pdf:
        pdf.savefig(sc, bbox_inches='tight', orientation='landscape')
        pdf.savefig(vis, bbox_inches='tight', orientation='landscape')
        pdf.savefig(cf_vis, bbox_inches='tight', orientation='landscape')
    return
getRpt(df)

# developer check
print('@RSI: ', feed)
