# Investment Rdeep GUI

import tkinter as tk                                                            # for GUI
import tkinter.messagebox as msgbox
import pandas as pd                                                             # for data frms                                               # for Plots
import os                                                                     # for os commands
import cDB                                                                      # from *.py
import importlib as imp  

from datetime import date
from PIL import ImageTk, Image                                                  # for Images
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg                 # for Plots

#-- stage 0
try:
    import Speech
    Speech.Speak('hello')
except:
    print('Hello failed.')

root = tk.Tk()
root.title('Investment Rdeep v1.0')
root.iconbitmap('./img/Rdeep.ico')
root.geometry('1250x800+100+0')

def f(s):                                                                       # font
    font = ('Helvetica', s)
    return font

default_par = ['manual', 'AAPL', './csv/MSFT.csv', 504, 21, 'True', 10]         # Create default parameters .db if not found
if not os.path.isfile('./db/parameters_list.db'):
    print('Parameters_list.db not found, creating new...')
    cDB.newDB()
    cDB.insertDB(default_par[0], default_par[1], default_par[2],
                 default_par[3], default_par[4], default_par[5], default_par[6])
    current_par = cDB.queryDB()    
else:
    print('Parameters_list.db found...')
    current_par = cDB.queryDB()
 
guess = tk.StringVar()                                                          # FFT parameters
guess.set(current_par[0][5])
print(guess)
#-- end stage 0

#-- stage 1
# frmLogo: Logo & Intro text (0,0)
frmLogo = tk.LabelFrame(root, padx=5, pady=5, bd=10, width=450, height=230,
                        text='Invesment Rdeep v1.0 -- stock recommender app built using python')
frmLogo.grid(row=0, column=0)

logo_img = ImageTk.PhotoImage(Image.open('./img/Rdeep.jpg'))
logo_img_lbl = tk.Label(frmLogo, image=logo_img)
logo_img_lbl.place(x=5, y=5)

intro1 = tk.Label(frmLogo, text='Easy Steps:', font=('Helvetica', 18, 'bold', 'underline')) # intro texts
intro2 = tk.Label(frmLogo, text='i.   Choose Data Source', font=f(12))
intro3 = tk.Label(frmLogo, text='ii.  Browse Facts', font=f(12))
intro4 = tk.Label(frmLogo, text='iii. Run Recommendations', font=f(12))

intro1.place(x=200, y=5)
intro2.place(x=200, y=55)
intro3.place(x=200, y=105) 
intro4.place(x=200, y=155)

# frmMode: Mode of getting data (1,0)
frmMode = tk.LabelFrame(root, padx=5, pady=5, bd=10, width=450, height=170,
                        text='i. Data Source: Auto (python lib: yfiance) | Manual (csv)')           
frmMode.grid(row=1, column=0)

## frm 2.1: Auto
frmMode_1 = tk.LabelFrame(frmMode, text='Auto: Enter Stock Symbol', padx=5, pady=5)                         
frmMode_1.place(x=5, y=5)

stock_symbol_ipt = tk.Entry(frmMode_1, width=55, borderwidth=5)
stock_symbol_ipt.grid(row=0, column=0)
stock_symbol_ipt.insert(0, current_par[0][1])
    
def fetch(var):
    if var == 'auto':
        cDB.updateSS(stock_symbol_ipt.get())
    elif var == 'manual':
        response = msgbox.askyesno(title='File Path', message='Do you want to browse for a file?')
        if response == 1:
            filepath = tk.filedialog.askopenfilename(initialdir='./csv')
            stock_path_ipt.delete(0, 'end')
            stock_path_ipt.insert(0, filepath)
            cDB.updateSP(filepath)
        else:    
            cDB.updateSP(stock_path_ipt.get())
    
    imp.reload(cDB)
    guess = cDB.queryDB()[0][5]
    if guess == 'True':
        import FFT; imp.reload(FFT)
        cDB.updatewL(FFT.wLsug)
    deleteAllfrmII(); initialfrmScores()
    getSetting()
    getChart()
    getStats()    

fetch_auto_btn = tk.Button(frmMode_1, text='Auto', padx=8, command=lambda: fetch('auto'))
fetch_auto_btn.grid(row=0, column=1)

## frm 2.2: Manual
frmMode_2 = tk.LabelFrame(frmMode, text='Manual: Enter CSV Location', padx=5, pady=5)
frmMode_2.place(x=5, y=60)

stock_path_ipt = tk.Entry(frmMode_2, width=55, borderwidth=5)
stock_path_ipt.grid(row=0, column=0)
stock_path_ipt.insert(0, current_par[0][2])

fetch_manual_btn = tk.Button(frmMode_2, text='Manual', command=lambda: fetch('manual'))
fetch_manual_btn.grid(row=0, column=1)

# frmStats: Stock Fact Statistics (0-1,1)
frmStats = tk.LabelFrame(root, padx=5, pady=5, bd=10, width=400, height=400,
                         text='ii. Facts: Statistics')                       
frmStats.grid(row=0, column=1, rowspan=2)

def getPeriod(d):
    import DataSource; imp.reload(DataSource)
    df_period = DataSource.dseries.tail(d)
    tbl_content = df_period.describe().round(2)    
    tbl_content = pd.DataFrame(tbl_content) 
    return tbl_content
    
def getStats():
    for f in [frmStats_1, frmStats_2, frmStats_3, frmStats_4]:
        for l in f.place_slaves():
            l.destroy()
    global tbl1, tbl2, tbl3, tbl4
    tbl1 = tk.Label(frmStats_1, text=getPeriod(5), justify='r').place(x=45, y=10)
    tbl2 = tk.Label(frmStats_2, text=getPeriod(21), justify='r').place(x=45, y=10)
    tbl3 = tk.Label(frmStats_3, text=getPeriod(252), justify='r').place(x=45, y=10)
    tbl4 = tk.Label(frmStats_4, text=getPeriod(1260), justify='r').place(x=45, y=10)

frmStats_1 = tk.LabelFrame(frmStats, text='Week: recent 5 days',
                           padx=5, pady=5, width=180, height=180)
frmStats_2 = tk.LabelFrame(frmStats, text='Month: recent 21 days',
                           padx=5, pady=5, width=180, height=180)
frmStats_3 = tk.LabelFrame(frmStats, text='1 Year: recent 252 days',
                           padx=5, pady=5, width=180, height=180)
frmStats_4 = tk.LabelFrame(frmStats, text='5 Yrs: recent 1260 days',
                           padx=5, pady=5, width=180, height=180)

frmStats_1.place(x=5, y=5)
frmStats_2.place(x=185, y=5)
frmStats_3.place(x=5, y=185)
frmStats_4.place(x=185, y=185)

tbl1 = tk.Label(frmStats_1, text='--no data--').place(x=45, y=10)
tbl2 = tk.Label(frmStats_2, text='--no data--').place(x=45, y=10)
tbl3 = tk.Label(frmStats_3, text='--no data--').place(x=45, y=10)
tbl4 = tk.Label(frmStats_4, text='--no data--').place(x=45, y=10)

# frmChart: Stock Facts Chart (0-1,2)
frmChart = tk.LabelFrame(root, padx=5, pady=5, bd=10, width=400, height=400,
                         text='ii. Facts: Chart')                       
frmChart.grid(row=0, column=2, rowspan=2)

def getChart():
    import DataSource; imp.reload(DataSource)
    if DataSource.getStatus == 'error':
        msgbox.showerror(title='Manual Data Error', 
                         message='Invalid file path.' + '\n' + 
                         'Or cannot find "Date" or "Close" in data')
    fig = DataSource.chart
    fig_widget = FigureCanvasTkAgg(fig, frmChart)
    fig_widget.get_tk_widget().place(x=20, y=10)
##- end stage 1

##- start stage 2
# frmScores: Stock Recommendation Scores (2,1)
frmScores = tk.LabelFrame(root, padx=5, pady=5, bd=10, width=400, height=400,
                          text='iii. Recommendation: Buy | Hold')                       
frmScores.grid(row=2, column=1)
                       
frmRSI = tk.LabelFrame(frmScores, text='RSI', padx=5, pady=5, width=180, height=180)                         
frmETS = tk.LabelFrame(frmScores, text='ETS',  padx=5, pady=5, width=180, height=180)
frmLSTM = tk.LabelFrame(frmScores, text='LSTM', padx=5, pady=5, width=180, height=180)
frmHybrid = tk.LabelFrame(frmScores, text='Overall: LSTM + ETS + RSI',
                          padx=5, pady=5, width=180, height=180)

frmRSI.place(x=5, y=5)
frmETS.place(x=185, y=5)
frmLSTM.place(x=5, y=185)
frmHybrid.place(x=185, y=185)
             
def runModel(frm):
    imp.reload(cDB)
    guess = cDB.queryDB()[0][5]
    if guess == 'True':
        import FFT; imp.reload(FFT)
        cDB.updatewL(FFT.wLsug)        
    getSetting()
    getChart()
    getStats()
    for i in frm.place_slaves():
        i.destroy()
    if frm == frmRSI:             
        import RSI; imp.reload(RSI)
        global r
        r = RSI.feed
        frmScoreContents(frmRSI, r[0], r[1], r[2])
        showVis(RSI.vis)
    elif frm == frmETS:     
        import ETS; imp.reload(ETS)
        global e  
        e = ETS.feed
        frmScoreContents(frmETS, e[0], e[1], e[2])
        showVis(ETS.vis)   
    elif frm == frmLSTM:
        import LSTM; imp.reload(LSTM)
        global l
        l = LSTM.feed
        frmScoreContents(frmLSTM, l[0], l[1], l[2])
        showVis(LSTM.vis) 
    elif frm == frmHybrid:               
        try:
            global h0, h1, h2, hyb_score 
            hyb_score = (r[3] * r[4]
                        + e[3] * e[4]
                        + l[3] * l[4])/3
            if round(hyb_score,2) >= 0.5:
                h0 = 'Buy'
            else:
                h0 = 'Hold'
            h1 = str(round(hyb_score*100,1)) + '%'
            h1 = str(int(l[3] + r[3] + e[3])) + ' / 3 votes'
            h2 = str(date.today()) + ' <- ran'
        except:
            h0 = '--'; h1 = '--'; h2 = 'Other models req.'
        frmScoreContents(frmHybrid, h0, h1, h2)
        for i in [r[3], r[4], e[3], e[4], l[3], l[4]]:
            print(round(i,3), type(i))       
        

def finalRec():
    try:
        ln1 = '          (  ' + str(r[3]) + '  x  ' + str(round(r[4],3)) + '  +  ' + '\n'
        ln2 = '             ' + str(e[3]) + '  x  ' + str(round(e[4],3)) + '  +  ' + '\n'
        ln3 = '             ' + str(l[3]) + '  x  ' + str(round(l[4],3)) + '  )  /  3  ' + '\n'
        ln4 = '\n'
        ln5 = '          =  ' + str(round(hyb_score,2)) + '\n'
        ln6 = '\n'
        ln7 = '          {  >=0.5 "Buy"  ;  <0.5 "Hold"  }'
        frec =  ln1 + ln2 + ln3 + ln4 + ln5 + ln6 + ln7
        import Speech; imp.reload(Speech)
        Speech.Speak(h0)
        msgbox.showinfo(title='Final Recommendation', message=frec)
    except:
        msgbox.showinfo(title='Final Recommendation', 
                        message='No recommendation yet,\nplease run other models first!')

def rpt(frm):                                                            
    getSetting()
    getChart()
    getStats()
    if frm == frmRSI:
        os.startfile('rpt\\RSI.pdf')
    elif frm == frmETS:
        os.startfile('rpt\\ETS.pdf')
    elif frm == frmLSTM:
        os.startfile('rpt\\LSTM.pdf')
    elif frm == frmHybrid:
        finalRec()
        
def deleteAllfrmII():
    for f in [frmHybrid, frmLSTM, frmRSI, frmETS, frmVisTrend]:
        for l in f.place_slaves():
            l.destroy()
 
def frmScoreContents(frm, T0, T1, tdate):
    global recommend, txdate, model_lbl, tmodel_acc, view_btn, run_btn    
    recommend = tk.Label(frm, text=T0, font=('Helvetica', 16, 'bold')).place(x=5)
    txdate = tk.Label(frm, text=tdate, font=('Helvetica', 12, 'bold')).place(x=5, y=30)
    model_lbl = tk.Label(frm, text='Forecast support:', 
                         font=f(8)).place(x=5, y=70)
    tmodel_acc = tk.Label(frm, text=T1, font=f(8)).place(x=110, y=70)
    view_btn = tk.Button(frm, text='Latest Rpt', font=f(12), width = 10,
                         command=lambda: rpt(frm)).place(x=5, y=110)
    run_btn = tk.Button(frm, text='Run', font=f(12), width = 4,
                        command=lambda: runModel(frm)).place(x=110, y=110)

def initialfrmScores():
    for f in [frmHybrid, frmLSTM, frmRSI, frmETS]:
        frmScoreContents(f, '-', '-', '-')

initialfrmScores()

# frmVisTrend: Stock Recommendation Trend (2,0)
frmVisTrend = tk.LabelFrame(root, padx=5, pady=5, bd=10, width=450, height=400,
                       text='iii. Recommendation: Visual Trend')                       
frmVisTrend.grid(row=2, column=0)

def showVis(vis):
    fig = vis
    fig_widget = FigureCanvasTkAgg(fig, frmVisTrend)
    fig_widget.get_tk_widget().place(x=10, y=5)

# frmSetting: Setting (2,3) 
frmSetting = tk.LabelFrame(root, text='<<Settings>>',
                           padx=5, pady=5, bd=10, width=400, height=400)
frmSetting.grid(row=2, column=2)

current_setting = tk.LabelFrame(frmSetting, text='Current Settings',
                                padx=5, pady=5, width=360, height=300)
current_setting.place(x=5, y=5)

def getSetting():
    import cDB; imp.reload(cDB)
    current_par = cDB.queryDB()
    stock_symbol_ipt.delete(0, 'end')
    stock_symbol_ipt.insert(0, current_par[0][1])
    stock_path_ipt.delete(0, 'end')
    stock_path_ipt.insert(0, current_par[0][2])
    
    for p in current_setting.place_slaves(): 
        p.destroy()
        
    parInitial()
    global par0, par1, par2, par3, par4, par5, par6
    par0 = tk.Label(current_setting, text=current_par[0][0]).place(x=180, y=10)
    par1 = tk.Label(current_setting, text=current_par[0][1]).place(x=180, y=40)
    par2 = tk.Label(current_setting, text=current_par[0][2].rsplit('/',1)[1]).place(x=180, y=70)
    par3 = tk.Label(current_setting, text=current_par[0][3]).place(x=180, y=100)
    par4 = tk.Label(current_setting, text=current_par[0][4]).place(x=180, y=130) 
    par5 = tk.Label(current_setting, text=current_par[0][5]).place(x=180, y=160)
    par6 = tk.Label(current_setting, text=current_par[0][6]).place(x=180, y=190)
    

def parInitial():
    global par0_lbl, par1_lbl, par2_lbl, par3_lbl, par4_lbl, par5_lbl, par6_lbl
    par0_lbl = tk.Label(current_setting, text='Data Mode\t\t:').place(x=10, y=10)
    par1_lbl = tk.Label(current_setting, text='Stock Symbol (Auto)\t:').place(x=10, y=40)
    par2_lbl = tk.Label(current_setting, text='Stock Path (Manual)\t:').place(x=10, y=70)
    par3_lbl = tk.Label(current_setting, text='Data Rows\t\t:').place(x=10, y=100)
    par4_lbl = tk.Label(current_setting, text='Window Length\t\t:').place(x=10, y=130)
    par5_lbl = tk.Label(current_setting, text='Guess Window Length\t:').place(x=10, y=160)
    par6_lbl = tk.Label(current_setting, text='Window Future\t\t:').place(x=10, y=190)

parInitial()
##- end stage 2

##- stage 3
# Pop Up Window
def adv_set():
   try:
       import Speech; imp.reload(Speech)
       Speech.Speak('adv')
   except:
       print('inform adv failed')
   deleteAllfrmII(); initialfrmScores()
   
   AW = tk.Toplevel()
   AW.title('Advance Setting')
   AW.iconbitmap('./img/Rdeep.ico')
   AW.geometry('400x450+300+200')
   
   frmAW = tk.LabelFrame(AW, text='Advance Setting', padx=5, pady=5, width=390, height=390)
   

   def updatePar5(guess): 
    if guess == 'False':
        cDB.updategL('False')
        getSetting()
    else:
        cDB.updategL('True')
        getSetting()        
    

   frmAW.place(x=5, y=5)
   def updatePar3():
    p = int(par3_ipt.get())
    if p in range(504, 1260+1):
        cDB.updatedR(p)
        getSetting()
    else:
        msgbox.showwarning(title='Warning!', message='Value out of range!')
        par3_ipt.insert(0, current_par[3])
    

   def updatePar4():
    p = int(par4_ipt.get())
    if p in range(15, 63+1):
        cDB.updatewL(p)
        getSetting()
    else:
        msgbox.showwarning(title='Warning!', message='Value out of range!')
        par3_ipt.insert(0, current_par[4])
    

   def updatePar6():
        p = int(par6_ipt.get())
        if p in range(5, 21+1):
            cDB.updatewF(p)
            getSetting()
        else:
            msgbox.showwarning(title='Warning!', message='Value out of range!')
            par6_ipt.insert(0, current_par[6])
        
    
   def insertCurrent():
       p = cDB.queryDB()
       par3_ipt.insert(0, p[0][3])
       par4_ipt.insert(0, p[0][4])
       par6_ipt.insert(0, p[0][6])         
       guess.set(p[0][5])
       
   
   def deleteCurrent():
       par3_ipt.delete(0, 'end')
       par4_ipt.delete(0, 'end')
       par6_ipt.delete(0, 'end')
       
   
   def openReadme():
    os.startfile('db\\readme.txt')
    
   def clearCache():
    # clear python cache
    response = msgbox.askyesno(title='Clear Cache', 
                               message='Clearing cache allow application to run normally.\nDo you want to clear them now?')
    if response == 1:
        if os.path.isdir('./__pycache__'):
            for root, dirs, files in os.walk('./__pycache__'):
                for file in files:
                    os.remove(os.path.join(root, file)) 
        for file in ['hello.mp3', 'hold.mp3', 'buy.mp3', 'adv.mp3',
                     './db/lstm.csv', './db/lstm.hdf5',
                     './rpt/RSI.pdf', './rpt/ETS.pdf', './rpt/LSTM.pdf',]:
            if os.path.isfile(file):
                os.remove(file)
            else:
                print('File not found: ', file) 

   def updateDefault():
    cDB.updateDB(default_par[0], default_par[1], default_par[2],
                 default_par[3], default_par[4], default_par[5], default_par[6])
    deleteCurrent()
    getSetting()
    insertCurrent()
    
    stock_symbol_ipt.delete(0, 'end')
    stock_symbol_ipt.insert(0, current_par[0][1])
    stock_path_ipt.delete(0, 'end')
    stock_path_ipt.insert(0, current_par[0][2])
    
   
   par3_l1 = tk.Label(frmAW, text='# of rows used, from last record.', font=f(12))
   par3_l2 = tk.Label(frmAW, text='\t504 <= dR <= 1260', font=f(12))
   par4_l1 = tk.Label(frmAW, text='Window length considered, aka "look back".', font=f(12))
   par4_l2 = tk.Label(frmAW, text='\t 15 <= wL <= 63', font=f(12))
   par5_l3 = tk.Label(frmAW, text='* returns previous if <15 or >63', font=f(9))
   par6_l1 = tk.Label(frmAW, text='Days to the future. wF <= wL', font=f(12))
   par6_l2 = tk.Label(frmAW, text='\t  5 <= wF <= 21', font=f(12))

   par3_ipt = tk.Entry(frmAW, width=10, font=f(12), borderwidth=5, justify='r')
   par3_btn = tk.Button(frmAW, text='<< cfm change', command=updatePar3, font=f(12))
   par4_ipt = tk.Entry(frmAW, width=10, font=f(12), borderwidth=5, justify='r')
   par4_btn = tk.Button(frmAW, text='<< cfm change', command=updatePar4, font=f(12))
   par5_rdo1 = tk.Radiobutton(frmAW, text='Guess on', variable=guess, value='True',
                              font=f(12), command=lambda: updatePar5('True'))
   par5_rdo2 = tk.Radiobutton(frmAW, text='Guess off', variable=guess, value='False',
                              font=f(12), command=lambda: updatePar5('False'))
   par6_ipt = tk.Entry(frmAW, width=10, font=f(12), borderwidth=5, justify='r')
   par6_btn = tk.Button(frmAW, text='<< cfm change', command=updatePar6, font=f(12))
   
   insertCurrent()
   
   par3_btn.place(x=250, y=67)
   par4_btn.place(x=250, y=167)   
   par6_btn.place(x=250, y=317)   
   
   par3_l1.place(x=10, y=10)
   par3_l2.place(x=10, y=40)
   par3_ipt.place(x=150, y=70)
   par4_l1.place(x=10, y=110)
   par4_l2.place(x=10, y=140)
   par4_ipt.place(x=150, y=170)
   par5_rdo1.place(x=150, y=200)
   par5_rdo2.place(x=250, y=200)
   par5_l3.place(x=150, y=230)
   par6_l1.place(x=10, y=260)
   par6_l2.place(x=10, y=290)
   par6_ipt.place(x=150, y=320)   
         
   readme_btn = tk.Button(AW, text='readme', command=openReadme, font=f(12))
   readme_btn.place(x=10, y=407)
   
   reset_btn = tk.Button(AW, text='default', command=updateDefault, font=f(12))
   reset_btn.place(x=155, y=407)
   
   readme_btn = tk.Button(AW, text='clear cache', command=clearCache, font=f(12))
   readme_btn.place(x=300, y=407)
   return

## adv button
adv_btn = tk.Button(frmSetting, text='<Refresh / AdvSet>', command=adv_set, font=f(12))
adv_btn.place(x=200, y=320)
##- end stage 3

root.mainloop()
