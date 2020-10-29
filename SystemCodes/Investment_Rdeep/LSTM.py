# LSTM
import pandas as pd
import numpy as np
import tensorflow.keras
import matplotlib.pyplot as plt
import sklearn.metrics as metrics
import scipy.stats
import sys

from DataSource import dR, wL, wF, tL, mS, dfname
from DataPrep import df
from tensorflow.keras.callbacks import ModelCheckpoint, CSVLogger
from tensorflow.keras.models import Sequential
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dense
from sklearn.preprocessing import MinMaxScaler
from scipy.stats import rankdata
from matplotlib.backends.backend_pdf import PdfPages

# 1 Data Prep
np.random.seed(21)
look_back           = wL 
epochs              = 30
batchSize           = int(wL/2)
scaler              = MinMaxScaler(feature_range=(0, 1))

# split
dat                 = df['Close'].values
tr                  = dat[:-tL]
tr                  = scaler.fit_transform(tr.reshape(-1, 1))
ts                  = dat[-tL:]
ts                  = scaler.fit_transform(ts.reshape(-1, 1))

def create_dataset(dataset, look_back):
	dataX, dataY = [], []
	for i in range(len(dataset)-look_back-1):
		a = dataset[i:(i+look_back)]
		dataX.append(a)
		dataY.append(dataset[i + look_back])
	return np.array(dataX), np.array(dataY)


Xtr, ytr            = create_dataset(tr, look_back)
Xts, yts            = create_dataset(ts, look_back)

Xtr                 = np.reshape(Xtr, (Xtr.shape[0], 1, Xtr.shape[1]))
Xts                 = np.reshape(Xts, (Xts.shape[0], 1, Xts.shape[1]))


# 2. Model
## create model skeleton
modelname   = 'lstm' 
def createModel():
    inputs = Input(shape=(Xtr.shape[1], Xtr.shape[2]))
    y = LSTM(25, return_sequences=True, dropout=0.5, recurrent_dropout=0.5)(inputs)
    y = LSTM(25, dropout=0.5, recurrent_dropout=0.5)(y)
    y = Dense(1, activation='sigmoid')(y)
    
    model = Model(inputs=inputs, outputs=y)
    model.compile(loss='mse', optimizer='adam')

    return model
model               = createModel() # initial train
modelGo             = createModel()         
modelFt             = createModel()
modelFn             = createModel() # final train
model.summary()

## setup callback
folderpath          = sys.path[0].replace('\\', '/') + '/db/'
filepath            = folderpath + modelname + ".hdf5"
checkpoint          = ModelCheckpoint(filepath, 
                                  monitor='val_loss', 
                                  verbose=0, 
                                  save_best_only=True, 
                                  mode='max')

csv_logger          = CSVLogger(folderpath+modelname +'.csv')                      
callbacks_list      = [checkpoint, csv_logger]


## start fitting
model.fit(Xtr, ytr, validation_data=(Xts, yts), epochs=epochs, batch_size=batchSize,
          callbacks=callbacks_list)
modelGo.load_weights(filepath)
print("Model weights loaded from:", filepath)
modelGo.compile(loss='mse', optimizer='adam')

trPred              = model.predict(Xtr)  # take a look at refitted                  
tsPred              = modelGo.predict(Xts)

## inverse the scaling
Xtr                 = np.reshape(Xtr, (Xtr.shape[0], Xtr.shape[2]))
Xts                 = np.reshape(Xts, (Xts.shape[0], Xts.shape[2]))
Xtr                 = scaler.inverse_transform(Xtr)
Xts                 = scaler.inverse_transform(Xts)
ytr                 = scaler.inverse_transform(ytr)
yts                 = scaler.inverse_transform(yts)
trPred              = scaler.inverse_transform(trPred)
tsPred              = scaler.inverse_transform(tsPred)

# 3. convert guesses
fullDat             = df
fulldate            = df.index
# get dates
trfd = fulldate[:-tL];  tsfd = fulldate[-tL:]
ytrd = trfd[wL+1:];     ytsd = tsfd[wL+1:] 

def getBPred():
    l = len(tsPred)
    tsBPred = []
    for i in range(l):
        if i+wF >= l-1:
            break
        ranklist = yts[i] + tsPred[i+1:i+wF+2]
        pct = rankdata(ranklist)[0]/(1+wF)
        if pct <= 0.25:
            p = 1.0
        else:
            p = 0.0
        tsBPred.append(p)
    matchingLabel = fullDat['Label'].iloc[-len(ytsd)+1:-wF]
    bp = pd.DataFrame({'tsBPred':tsBPred, 'Label':matchingLabel}, 
                      index=ytsd[1:-wF])
    return bp

# Final model phase
trF                 = dat
trF                 = scaler.fit_transform(trF.reshape(-1, 1))
XtrF, ytrF          = create_dataset(trF, look_back)

def forecast(model):
    fl  = XtrF[-1]     
    for _ in range(wF+1):
        fl = fl.reshape(1, 1, fl.shape[0]) 
        out = model.predict(fl)[0][0]
        fl = fl.reshape(-1)
        fl = np.append(fl, out)
        fl = fl[-look_back:]
    fl = fl.reshape(-1,1)
    fl = scaler.inverse_transform(fl)           
    return fl[-wF-1:]
    
def forecastDates():
    last_date = fullDat.index[-1]
    fd = pd.date_range(last_date, periods=wF+1).tolist()
    return fd

## retrain for one last forecast
fDates              = forecastDates()
XtrF                = np.reshape(XtrF, (XtrF.shape[0], 1, XtrF.shape[1]))
modelFn.fit(XtrF, ytrF, epochs=epochs, batch_size=batchSize)
XtrF                = np.reshape(XtrF, (XtrF.shape[0], XtrF.shape[2], 1))                          
fnPred              = forecast(modelFn)

def getVis():
    trPreddf = pd.DataFrame({'Train Predict':trPred.reshape(-1)}, index=ytrd)
    tsPreddf = pd.DataFrame({'Test Predict':tsPred.reshape(-1)}, index=ytsd)
    fnPreddf = pd.DataFrame({'New Forecast':fnPred.reshape(-1)}, index=fDates)
    fig, ax  = plt.subplots(figsize=(4, 3.5))
    fullDat['Close'].plot(ax=ax, x_compat=True, lw=0.3,
                           title = 'LSTM', figsize=(4, 3.5))
    trPreddf.plot(ax=ax)
    tsPreddf.plot(ax=ax)
    fnPreddf.plot(ax=ax)
    ax.legend(loc='upper left', prop={'size': 8})
    return fig
vis = getVis()
## feed
def getFeed():
    tsBPred = getBPred()
    vacc = metrics.accuracy_score(tsBPred['Label'], tsBPred['tsBPred'])
    tacc = str(round(vacc*100,1)) + '%'
    
    ranklist = np.insert(fnPred[1:], 0, dat[-1])
    pct = rankdata(ranklist)[0]/(1+wF)
    if pct <= 0.25:
        vbny = 1.0
    else:
        vbny = 0.0
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
    ax.text(0, 1.5, '(Unsupervised) LSTM readings', ha='left', fontsize=font_size, fontweight='bold')
    ax.text(0, 1.3, 'True: Buy -- current price <=25%tile of future(wF) days', ha='left', fontsize=10)
    ax.text(0, 1.1, 'Pred: Buy -- <=25%tile of first true + wF test readings', ha='left', fontsize=10)
    ax.text(0.44, -0.2, acc, ha='left', fontsize=font_size)
    ax.text(0.21, -0.4, mse, ha='left', fontsize=font_size)
    ax.text(0, -0.6, '** Train-Test model is for illustration purpose.', ha='left', fontsize=10)
    ax.text(0, -0.8, '** Required forecast should be freshly trained', ha='left', fontsize=10)
    return ax.get_figure(), ax

def getRpt(dat):
    # stock chart
    sc, ax = plt.subplots()    
    dat['Close'].plot(kind='line', legend=True, ax=ax, color='b', marker=',', fontsize=5)
    m = dat['Close'].mean()
    ax.axhline(y=m, color='g', linestyle='--', lw=0.5)
    ax.set_title('<' + dfname + '> rows = ' + str(dR) + ', mean = ' + str(round(m,2)))
    
    # cf_metrics and scores
    mse = 'Mean-Squared-Error:                ' + str(round(metrics.mean_squared_error(yts, tsPred),3))
    accuracy = 'Accuracy:                ' + getFeed()[1]
    tsBPred = getBPred()
    cf = metrics.confusion_matrix(tsBPred['Label'].values, tsBPred['tsBPred'].values)
    cf_matrix = pd.DataFrame({'Test Pred':['True: Hold', 'True: Buy '],
                          'Pred: Hold':[cf[0,0], cf[1,0]],
                          'Pred: Buy ':[cf[0,1], cf[1,1]]})
    cf_vis = render_mpl_table(cf_matrix, accuracy, mse)[0]
    
    # Loss value
    records     = pd.read_csv(folderpath+modelname +'.csv')
    records     = records.set_index('epoch')
    figR, axR = plt.subplots()
    records.plot(ax=axR)
    axR.set_title('Loss Value - Training-Testing')
    
    # model summary
    newlist = []
    model.summary(print_fn=lambda x: newlist.append(x))
    for i in range(len(newlist[:])):
        if newlist[i].startswith('='):
           newlist[i] = newlist[i][-37:]
    newlist.insert(0, '<< Model Summary >>')
    l = np.vstack(newlist)
    figMS, axMS = plt.subplots(figsize=(6,0.01))
    axMS.axis('off')
    axMS.table(cellText=l)
        
    with PdfPages('./rpt/LSTM.pdf') as pdf:
        pdf.savefig(sc, bbox_inches='tight', orientation='landscape')
        pdf.savefig(vis, bbox_inches='tight', orientation='landscape')
        pdf.savefig(cf_vis, bbox_inches='tight', orientation='landscape')
        pdf.savefig(figR, bbox_inches='tight', orientation='landscape')
        pdf.savefig(figMS, bbox_inches='tight', orientation='landscape')
    return
getRpt(df)

# developer check
print('@LSTM: ', feed)