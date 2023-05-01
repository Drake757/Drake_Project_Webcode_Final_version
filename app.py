from flask import Flask, render_template, request,session,url_for,redirect
import pymysql
import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, ElasticNet
from sklearn.model_selection import train_test_split
from sklearn.svm import SVR

app = Flask(__name__)
app.secret_key = "123456"


@app.route('/', methods=['GET', 'POST'])
def mainpage():
    return render_template('test.html',x=0) # go to mainpage

@app.route('/returnback', methods=['GET', 'POST'])
def returnfuc():
    return render_template('test.html') #back to mainpage

@app.route('/signin',methods=['GET', 'POST'])
def signin():
    return render_template('signin.html') #go to sign in page

@app.route('/login',methods=['GET', 'POST'])
def login():
    return render_template('login.html') # go to log in page

@app.route('/registuser', methods=['GET', 'POST'])
def registuser():
    username = request.form.get('username') # get users' account information from web
    password = request.form.get('password')
    version1 = request.form.get('version1')
    version2 = request.form.get('version2')
    print(version1)
    conn = pymysql.connect(host='127.0.0.1', user='root', password='hushanxin.', db='RUNOOB', port=3306, charset='utf8')
    cur = conn.cursor()
    if version1=='1': # Store different account information into database
        sql = "INSERT INTO students_tbl (username,password,version)VALUES (%s,%s,%s)"
        try:
            cur.execute(sql, (username, password,version1))
            conn.commit()
            cur.close()
            return render_template('signin.html')
        except:
            conn.rollback()
    if version2=='2':
        sql = "INSERT INTO students_tbl (username,password,version)VALUES (%s,%s,%s)"
        try:
            cur.execute(sql, (username, password,version2))
            conn.commit()
            cur.close()
            return render_template('signin.html')
        except:
            conn.rollback()
    conn.close()

@app.route('/LOGIN', methods=['GET', 'POST'])
def check():
        username = request.form.get('username') # get users' account information from MySql databse
        password = request.form.get('password')
        session['username'] =username # store log in user name
        print(username)
        conn = pymysql.connect(host='127.0.0.1', user='root', password='hushanxin.', db='RUNOOB', port=3306,
                               charset='utf8')
        cur = conn.cursor()
        sql2 = "select * from students_tbl where username = %s and password = %s"
        try:
            cur.execute(sql2, (username, password))
            results = cur.fetchall()
            print(results)
            session['version'] = results[0][3]# store account's version
            print(session['version'])
            if len(results) >= 1 and session['version']==2: # version=2, log in student version
                return render_template('Studentpage.html',x=session['version'],name=results[0][1])
            if len(results) >= 1 and session['version'] == 1: # version=1, log in student version
                    return render_template('teacherpage.html')
            else:
                return 'The user name or password is incorrect'
            conn.commit()

        except:
            conn.rollback()
            return render_template('login.html')

        conn.close()

@app.route('/display', methods=['GET', 'POST'])
def display():
    conn = pymysql.connect(host='127.0.0.1', user='root', password='hushanxin.', db='RUNOOB', port=3306,
                           charset='utf8')
    cur = conn.cursor()
    sql3 = "select * from project where student_id = %s "
    sql4 = "select * from students_tbl where username = %s " # get students' information from database
    print(session['username'])
    try:
        cur.execute(sql4, (session['username']))
        name = cur.fetchall()
        print(name[0][0])
        cur.execute(sql3, (name[0][0]))
        id = cur.fetchall()
        if id[0][0]== name[0][0]: # Verify that the student is correct
            return render_template('display.html',x=id[0][11],y=id[0][12],z=id[0][13])
        else:
            return render_template('test.html',x=session['version'])
        conn.commit()

    except:
        conn.rollback()
        return render_template('Studentpage.html')

    conn.close()


@app.route('/comparison', methods=['GET', 'POST'])
def comparison():
    conn = pymysql.connect(host='127.0.0.1', user='root', password='hushanxin.', db='RUNOOB', port=3306,
                           charset='utf8')
    cur = conn.cursor()
    sql5 = "select G1 from project "
    sql6 = "select G2 from project "
    sql7 = "select G3 from project "
    sql8 = "select * from students_tbl where username = %s "
    sql9 = "select * from project where student_id = %s " # get students' information from database
    try:
        cur.execute(sql5)
        G1 = cur.fetchall()
        G1total=0
        G2total=0
        G3total=0
        for i in range(0, 395):
            G1total= G1total+G1[i][0]
        G1average=G1total/395 # get G1 average
        cur.execute(sql6)
        G2 = cur.fetchall()
        for i in range(0, 395):
            G2total = G2total + G2[i][0]
        G2average=G2total/395 # get G2 average
        cur.execute(sql7)
        G3 = cur.fetchall()
        for i in range(0, 395):
            G3total = G3total + G3[i][0]
        G3average = G3total / 395 # get G3 average
        print(session['username'])
        cur.execute(sql8, (session['username']))
        name = cur.fetchall()
        print(name[0][0])
        cur.execute(sql9, (name[0][0]))
        id = cur.fetchall()
        print(id[0][0])
        if id[0][0] == name[0][0]:
            return render_template('comparison.html',G1average=G1average,G2average=G2average,G3average=G3average,x=id[0][11],y=id[0][12],z=id[0][13])
            conn.commit()

    except:
        conn.rollback()
        return render_template('Studentpage.html')

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    f = open('LR_Model with 5 features include G1 and G2', 'rb') # use prediction model
    s = f.read()
    model = pickle.loads(s)
    conn = pymysql.connect(host='127.0.0.1', user='root', password='hushanxin.', db='RUNOOB', port=3306,
                           charset='utf8')
    cur = conn.cursor()
    sql10 = "select failures,Medu,G1,pass,G2  from project_tbl "
    sql11 = "select * from students_tbl where username = %s "
    sql12 = "select * from project where student_id = %s " # get information form database
    try:
        cur.execute(sql10)
        features = cur.fetchall()
        print(features)
        df = pd.DataFrame(features, dtype=int) # transfer data into dataframe
        print(df)
        predictions = model.predict(df)
        print(predictions)
        cur.execute(sql11, (session['username']))
        name = cur.fetchall()
        cur.execute(sql12, (name[0][0]))
        id = cur.fetchall()
        x=id[0][0]
        print(x)
        if id[0][0] == name[0][0]: # Verify that the student is correct
            return render_template('prediction.html',score=predictions[x-1],name=session['username'])
            conn.commit()
    except:
        conn.rollback()
        return render_template('test.html',x=session['version'])

@app.route('/overall', methods=['GET', 'POST'])
def overall():
    conn = pymysql.connect(host='127.0.0.1', user='root', password='hushanxin.', db='RUNOOB', port=3306,
                           charset='utf8')
    cur = conn.cursor()
    sql5 = "select G1 from project "
    sql6 = "select G2 from project "
    sql7 = "select G3 from project " # get information form database
    try:
        cur.execute(sql5)
        G1 = cur.fetchall()
        G1_0_3=0
        G1_4_7=0
        G1_8_11=0
        G1_12_15=0
        G1_16_20=0
        G2_0_3 = 0
        G2_4_7 = 0
        G2_8_11 = 0
        G2_12_15 = 0
        G2_16_20 = 0
        G3_0_3 = 0
        G3_4_7 = 0
        G3_8_11 = 0
        G3_12_15 = 0
        G3_16_20 = 0 # Record the number of people in each section
        for i in range(0, 395):
            if(0<=G1[i][0]<=3):
                G1_0_3=G1_0_3+1
            if (4<= G1[i][0] <= 7):
                G1_4_7 = G1_4_7 + 1
            if (8 <= G1[i][0] <= 11):
                G1_8_11 = G1_8_11 + 1
            if (12 <= G1[i][0] <= 15):
                G1_12_15 = G1_12_15 + 1
            if (16 <= G1[i][0] <= 20):
                G1_16_20 = G1_16_20 + 1

        cur.execute(sql6)
        G2 = cur.fetchall()
        for i in range(0, 395):
            if (0 <= G2[i][0] <= 3):
                G2_0_3 = G2_0_3 + 1
            if (4 <= G2[i][0] <= 7):
                G2_4_7 = G2_4_7 + 1
            if (8 <= G2[i][0] <= 11):
                G2_8_11 = G2_8_11 + 1
            if (12 <= G2[i][0] <= 15):
                G2_12_15 = G2_12_15 + 1
            if (16 <= G2[i][0] <= 20):
                G2_16_20 = G2_16_20 + 1
        cur.execute(sql7)
        G3 = cur.fetchall()
        for i in range(0, 395):
            if (0 <= G3[i][0] <= 3):
                G3_0_3 = G3_0_3 + 1
            if (4 <= G3[i][0] <= 7):
                G3_4_7 = G3_4_7 + 1
            if (8 <= G3[i][0] <= 11):
                G3_8_11 = G3_8_11 + 1
            if (12 <= G3[i][0] <= 15):
                G3_12_15 = G3_12_15 + 1
            if (16 <= G3[i][0] <= 20):
                G3_16_20 = G3_16_20 + 1
        print(G1_0_3,G1_4_7)
        return render_template('overall.html', G1_0_3=G1_0_3,G1_4_7=G1_4_7,G1_8_11=G1_8_11,G1_12_15=G1_12_15,G1_16_20=G1_16_20
                               ,G2_0_3=G2_0_3,G2_4_7=G2_4_7,G2_8_11=G2_8_11,G2_12_15=G2_12_15,G2_16_20=G2_16_20,
                               G3_0_3=G3_0_3,G3_4_7=G3_4_7,G3_8_11=G3_8_11,G3_12_15=G3_12_15,G3_16_20=G3_16_20)
        conn.commit()
    except:
        conn.rollback()
        return render_template('Studentpage.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    return render_template('search.html',x=1) # go to search page

@app.route('/Search', methods=['GET', 'POST'])
def Search():
    conn = pymysql.connect(host='127.0.0.1', user='root', password='hushanxin.', db='RUNOOB', port=3306,
                           charset='utf8')
    cur = conn.cursor()
    student_name = request.form.get('search')
    sql2 = "select student_id from students_tbl where username = %s "
    sql3 = "select * from project where student_id = %s " # get student information form database
    print(student_name)
    student_datalist=[]
    try:
        cur.execute(sql2, (student_name))
        student_id = cur.fetchall()
        print(student_id)
        cur.execute(sql3, (student_id[0][0]))
        student_data = cur.fetchall()
        print(student_data)
        for i in range(0,14):
            student_datalist.append(student_data[0][i])
        return render_template('search.html',student_data=student_datalist,x=2)
    except:
        conn.rollback()
        return render_template('teacherpage.html')

    conn.close()

@app.route('/Chat', methods=['GET', 'POST'])
def Chat():
    conn = pymysql.connect(host='127.0.0.1', user='root', password='hushanxin.', db='RUNOOB', port=3306,
                           charset='utf8')
    cur = conn.cursor()


    sql = "select student_id from project"
    cur.execute(sql)
    student_id = cur.fetchall()
    return render_template('chat.html',student_id=student_id)


@app.route('/studentinfo', methods=['GET', 'POST'])
def studentinfo():
    student = request.form.get('content') # get search content from web
    session['student'] =student
    print(student)
    conn = pymysql.connect(host='127.0.0.1', user='root', password='hushanxin.', db='RUNOOB', port=3306,
                           charset='utf8')
    cur = conn.cursor()

    sql = "select * from project where student_id = %s"
    try:
        cur.execute(sql, student)
        student_info = cur.fetchall()
        print(student_info)
        return render_template('student_info.html', student_info=student_info)
    except:
        conn.rollback()
        return render_template('teacherpage.html')

@app.route('/reply', methods=['GET', 'POST'])
def reply():
    content = request.form.get('reply') # get reply form web
    print(content)
    print(session['username'])
    conn = pymysql.connect(host='127.0.0.1', user='root', password='hushanxin.', db='RUNOOB', port=3306, charset='utf8')
    cur = conn.cursor()
    sql = "INSERT INTO reply_tbl (user_id,content,reply_user)VALUES (%s,%s,%s)" # store reply into database
    try:
        cur.execute(sql,(session['username'],content,session['student']))
        conn.commit()
        return render_template('teacherpage.html',x=1)

    except:

        conn.rollback()
        return render_template('teacherpage.html')

    conn.close()

@app.route('/Checkreply', methods=['GET', 'POST'])
def Checkreply():
    conn = pymysql.connect(host='127.0.0.1', user='root', password='hushanxin.', db='RUNOOB', port=3306, charset='utf8')
    cur = conn.cursor()
    sql = "select student_id from students_tbl where username = %s"
    sql2 = "select user_id,content,createtime,claim from reply_tbl where reply_user = %s" # get reply form database
    try:
        cur.execute(sql,(session['username']))
        student_id = cur.fetchall()
        print("student_id")
        print(student_id[0][0])
        cur.execute(sql2, (session['username']))
        replies = cur.fetchall()
        print("replies")
        print(replies)
        conn.commit()
        return render_template('replypage.html',x=1,replies=replies)

    except:

        conn.rollback()
        return render_template('test.html')

    conn.close()

@app.route('/goClaim', methods=['GET', 'POST'])
def goClaim():
    conn = pymysql.connect(host='127.0.0.1', user='root', password='hushanxin.', db='RUNOOB', port=3306, charset='utf8')
    cur = conn.cursor()
    sql = "select user_id,title,createtime from claim_tbl" # get claim list form databse
    try:
        cur.execute(sql)
        claims = cur.fetchall()
        print(claims)

        return render_template('Claim.html',claims=claims)
    except:

        conn.rollback()
        return render_template('test.html')

    conn.close()


@app.route('/postClaim', methods=['GET', 'POST'])
def postClaim():

        return render_template('postClaim.html')

@app.route('/Claim', methods=['GET', 'POST'])
def Claim():
    title = request.form.get('title')
    content = request.form.get('content') # get claim form web
    print(content)
    print(title)
    print(session['username'])
    conn = pymysql.connect(host='127.0.0.1', user='root', password='hushanxin.', db='RUNOOB', port=3306, charset='utf8')
    cur = conn.cursor()
    sql = "INSERT INTO claim_tbl (user_id,title,content)VALUES (%s,%s,%s)" # store claim into databse

    try:
        cur.execute(sql, (session['username'], title,content))
        conn.commit()

        return render_template('Claim.html')

    except:

        conn.rollback()
        return render_template('test.html')

    conn.close()

@app.route('/claimpage', methods=['GET', 'POST'])
def claimpage():
    title = request.form.get('title')
    session['title']=title
    print(title)
    conn = pymysql.connect(host='127.0.0.1', user='root', password='hushanxin.', db='RUNOOB', port=3306, charset='utf8')
    cur = conn.cursor()
    sql = "select title,content from claim_tbl where title = %s"
    sql2 = "select user_id,createtime,content from reply_tbl where claim = %s" # get claim form databse

    try:
        cur.execute(sql, (title))
        content = cur.fetchall()
        print(content)
        cur.execute(sql2, (title))
        reply=cur.fetchall()
        print(reply)

        return render_template('claimpage.html',content=content,reply=reply)

    except:

        conn.rollback()
        return render_template('test.html')

    conn.close()



@app.route('/Claimreply', methods=['GET', 'POST'])
def Claimreply():
    reply = request.form.get('reply') # get reply form web
    print(reply)
    print('s'+session['title'])
    conn = pymysql.connect(host='127.0.0.1', user='root', password='hushanxin.', db='RUNOOB', port=3306, charset='utf8')
    cur = conn.cursor()
    sql = "INSERT INTO reply_tbl (user_id,content,reply_user,claim)VALUES (%s,%s,%s,%s)" # store claim reply into database
    sql2 = "select user_id from claim_tbl where title = %s  "
    try:
        cur.execute(sql2,(session['title']))
        title = cur.fetchall()
        title2 = title[0][0]
        print('s'+title2)
        cur.execute(sql,(session['username'],reply,title2,session['title']))
        conn.commit()
        return render_template('mainpage.html',x=1)

    except:

        conn.rollback()
        return render_template('index.html')

    conn.close()

@app.route('/returnteacher', methods=['GET', 'POST'])
def returnteacher():
    return render_template('teacherpage.html')

@app.route('/returnstudent', methods=['GET', 'POST'])
def returnstudent():
    return render_template('Studentpage.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    return render_template('text.html')

if __name__ == '__main__':
    app.run()
