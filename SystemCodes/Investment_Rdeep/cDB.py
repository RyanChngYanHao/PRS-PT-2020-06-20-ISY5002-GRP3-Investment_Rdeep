# sqlite related help functions
import sqlite3

def newDB():
    conn = sqlite3.connect('db/parameters_list.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE parameters(
        p_auto_manual text,
        p_stock_symbol text,
        p_stock_path text,
        p_data_rows integer,
        p_win_length integer,
        p_guess_length text,
        p_win_future integer)''')
    conn.commit()
    conn.close

def insertDB(AM, SS, SP, dR, wL, gL, wF):
    conn = sqlite3.connect('db/parameters_list.db')
    cursor = conn.cursor() 
    cursor.execute('''INSERT INTO parameters VALUES 
                   (:p_auto_manual, 
                   :p_stock_symbol, 
                   :p_stock_path,
                   :p_data_rows,
                   :p_win_length,
                   :p_guess_length,
                   :p_win_future)''',
                        {
                        'p_auto_manual': AM,
                        'p_stock_symbol': SS,
                        'p_stock_path': SP,
                        'p_data_rows': dR,
                        'p_win_length': wL,
                        'p_guess_length':gL,
                        'p_win_future': wF
                        })    
    
    conn.commit()
    conn.close
    
def updateSS(SS):
    conn = sqlite3.connect('db/parameters_list.db')
    cursor = conn.cursor() 
    cursor.execute('''UPDATE parameters SET
                   p_auto_manual = :AM,
                   p_stock_symbol = :SS
                   WHERE oid = :oid''' ,
                        {
                        'AM': 'auto',
                        'SS': SS,
                        'oid': 1
                        })
    conn.commit()
    conn.close
    
def updateSP(SP):
    conn = sqlite3.connect('db/parameters_list.db')
    cursor = conn.cursor() 
    cursor.execute('''UPDATE parameters SET
                   p_auto_manual = :AM,
                   p_stock_path = :SP

                   WHERE oid = :oid''' ,
                        {
                        'AM': 'manual',
                        'SP': SP,
                        'oid': 1
                        })
    conn.commit()
    conn.close

def updatedR(dR):
    conn = sqlite3.connect('db/parameters_list.db')
    cursor = conn.cursor() 
    cursor.execute('''UPDATE parameters SET
                   p_data_rows = :dR
    
                   WHERE oid = :oid''' ,
                        {
                        'dR': dR,
                        'oid': 1
                        })
    conn.commit()
    conn.close

def updatewL(wL):
    conn = sqlite3.connect('db/parameters_list.db')
    cursor = conn.cursor() 
    cursor.execute('''UPDATE parameters SET
                   p_win_length = :wL
                   
                   WHERE oid = :oid''' ,
                        {
                        'wL': wL,
                        'oid': 1
                        })
    conn.commit()
    conn.close

def updategL(gL):
    conn = sqlite3.connect('db/parameters_list.db')
    cursor = conn.cursor() 
    cursor.execute('''UPDATE parameters SET
                   p_guess_length = :gL
                   
                   WHERE oid = :oid''' ,
                        {
                        'gL': gL,
                        'oid': 1
                        })
    conn.commit()
    conn.close
    
def updatewF(wF):
    conn = sqlite3.connect('db/parameters_list.db')
    cursor = conn.cursor() 
    cursor.execute('''UPDATE parameters SET
                   p_win_future = :wF
    
                   WHERE oid = :oid''' ,
                        {
                        'wF': wF,
                        'oid': 1
                        })
    conn.commit()
    conn.close
    
def updateDB(AM, SS, SP, dR, wL, gL, wF):
    conn = sqlite3.connect('db/parameters_list.db')
    cursor = conn.cursor() 
    cursor.execute('''UPDATE parameters SET
                   p_auto_manual = :AM,
                   p_stock_symbol = :SS,
                   p_stock_path = :SP,
                   p_data_rows = :dR,
                   p_win_length = :wL,
                   p_guess_length = :gL,
                   p_win_future = :wF
    
                   WHERE oid = :oid''' ,
                        {
                        'AM': AM,
                        'SS': SS,
                        'SP': SP,
                        'dR': dR,
                        'wL': wL,
                        'gL': gL,
                        'wF': wF,
                        'oid': 1
                        })
    conn.commit()
    conn.close

def queryDB():
    conn = sqlite3.connect('db/parameters_list.db')
    cursor = conn.cursor()
    cursor.execute('SELECT *, oid FROM parameters')
    # with fetchone, fetchmany options
    oid_1 = cursor.fetchall()     
    conn.commit()
    conn.close    
    return oid_1
