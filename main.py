import sqlite3
import datetime
from flask import Flask, request, redirect, url_for, render_template
from six.moves.urllib.request import urlopen
app = Flask(__name__)

def connect_db(db_name):
    conn = sqlite3.connect(db_name)
    print("database open")
    return conn

def update_value(conn,row,value,key):
    conn.execute("UPDATE MF_table set %s = %f where MF_ID = '%s';"%(row,value,key))
    conn.commit()
    print("Record Updated Successfully")

def read_value(conn,table_name):
    cursor = conn.execute("SELECT * from %s"%table_name)
    return cursor

@app.route('/login',methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      pswd = request.form['nm']
      if pswd == "qwe123R$":
          #user = 'Sumit Rastogi'
          return redirect(url_for('home'))
      else:
          return "<h1>Access Denied!!</h1><br><br><h2>ERROR: YOU HAVE ENTERED INCORRECT PASSWORD</h2>"

@app.route('/')
def index():
   return render_template('login.html')

@app.route('/home')
def home():
   return render_template('home.html')

@app.route('/update', methods = ['POST','GET'])
def update():
    if request.method == 'POST':
        conn = connect_db('MF.db')
        update_value(conn,"COST",22900.07,"MTE117")
        return "Database Updated"

@app.route('/showdb', methods = ['POST','GET'])
def show_db():
    save_nav_in_db(read_nav_from_internet())
    conn = connect_db('MF.db')
    return render_template('update.html', cursor = read_value(conn,'MF_table'))

@app.route('/report', methods = ['POST','GET'])
def report():
    NAV = read_nav_from_internet()
    save_nav_in_db(NAV)
    conn = connect_db('MF.db')
    value = []
    cost = []
    name = []
    unit = []
    data = []
    cursor_mf_table = read_value(conn,'MF_table')
    mf_data = cursor_mf_table.fetchall()
    for index in range(len(mf_data)):
        name.append(mf_data[index][0])
        unit.append(mf_data[index][2])
        value.append(mf_data[index][2]*NAV[index+1])
        cost.append(mf_data[index][3])
    for i in range(len(name)):
        data.append([name[i],NAV[i+1],unit[i],cost[i],value[i],value[i]-cost[i]])
    data.append(['','','',sum(cost),sum(value),sum(value)-sum(cost)])
    return render_template('report.html',mf_data=data)

def read_nav_from_internet():
    MF_NAV = [str(datetime.datetime.now())]
    MF_DICT = {
                 'MSB079': r'http://www.moneycontrol.com/mutual-funds/nav/sbi-blue-chip-fund/MSB079',
                 'MBS291': r'http://www.moneycontrol.com/mutual-funds/nav/birla-sun-life-tax-relief-96/MBS291',
                 'MTE117': r'http://www.moneycontrol.com/mutual-funds/nav/franklin-india-high-growth-companies-fund/MTE117', 
                 'MKP002' : r'http://www.moneycontrol.com/mutual-funds/nav/franklin-india-prima-fund/MKP002', 
                 'MPI1116' : r'http://www.moneycontrol.com/mutual-funds/nav/icici-prudential-value-discovery-fund-direct-plan/MPI1116', 
                 'MKM311' : r'http://www.moneycontrol.com/mutual-funds/nav/kotak-select-focus-fund-regular-plan/MKM311', 
                 'MMA100' : r'http://www.moneycontrol.com/mutual-funds/nav/mirae-asset-emerging-bluechip-fund-direct-plan/MMA100'}
    
    for MF in MF_DICT:
        try:
            response = urlopen(MF_DICT[MF])
            myfile = str(response.read())
            MF_NAV.append(float(myfile.split('[')[1].split(']')[0]))
        except:
            print("Please Rerun.. Values are not in correct order")
    return MF_NAV

def save_nav_in_db(NAV):
    conn = connect_db('MF.db')
    conn.execute("INSERT INTO MF_RECORD (DATE, MF1, MF2, MF3, MF4, MF5, MF6, MF7) VALUES(?,?,?,?,?,?,?,?)",tuple(NAV))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    app.debug = True
    app.run('192.168.1.100',80)