# Data Source
# handles auto or manual data input
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import os
import cDB

# set parameter
tL = int(252/2)                                                                 # set test set to half year, test length
mS = 252                                                                        # set to 1 trading year, min size

# get parameter
current_par = cDB.queryDB()[0]
AM = current_par[0]                                                             # auto or manual data source
SS = current_par[1]                                                             # stock symbol
SP = current_par[2]                                                             # stock path
dR = current_par[3]                                                             # data rows
wL = current_par[4]                                                             # window length
gL = current_par[5]                                                             # window to future
wF = current_par[6]

if AM == 'auto':
    getStatus = 'ok'
    stock = yf.Ticker(SS)
    stock_history = stock.history(period='max')
    dseries = stock_history['Close']
    dfname = SS
    
elif AM == 'manual':
    if os.path.isfile(SP):        
        stock_history = pd.read_csv(SP)
    else:       
        stock_history = pd.DataFrame()
    
    if {'Date', 'Close'}.issubset(stock_history.columns):
        getStatus = 'ok'
        try:
            stock_history['Date'] = pd.to_datetime(stock_history['Date'], format='%d/%m/%Y')
        except:
            stock_history['Date'] = pd.to_datetime(stock_history['Date'], format='%Y-%m-%d')
        else:
            print('Date format is not dd/mm/yyyy')
        stock_history = stock_history.set_index('Date')
        dseries  = stock_history['Close']  
        dfname = SP[SP.rindex('/')+1:]
    else:
        getStatus = 'error'
        print('Incorrect data format. i.e. no "Date" or "Close" column')
    
def getChart():
    fig, ax = plt.subplots(figsize=(3.3,3.3))
    ax.set_title('<' + dfname + '> Max Historical Data')
    dseries.plot(kind='line', legend=True, ax=ax, color='b', marker=',', fontsize=5)
    ax.axhline(y=dseries.mean(), color='g', linestyle='--', lw=0.5)
    return fig
chart = getChart()

# developer check
print('@DataSource: ', [getStatus])
