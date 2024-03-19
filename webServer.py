from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key='SECRET_KEY'


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
        
    else : 
        userid = request.form['uid']
        userpw = request.form['upw']
        userinput = (userid, userpw)

        if(userid=='' or userpw==''):
            return 'write your user ID and Password'
        else:
            conn = sqlite3.connect('test_info.db', check_same_thread=False)
            cur=conn.cursor()
            cur.execute(f'SELECT uid, upw FROM USER_INFO;')
            db_value = cur.fetchall()

            if userinput in db_value:
                session['login_user']=userid
                conn.close()
                return redirect(url_for('list'))
            else:
                conn.close()
                return 'try again'


@app.route('/logout')
def logout():
    session.pop('login_user',None)
    return render_template("login.html")
    

@app.route('/register', methods=['POST','GET'] )
def register():
    if request.method == 'GET':
        return render_template('register.html')

    else : 
        userid = request.form['uid']
        userpw = request.form['upw']
        if(userid=='' or userpw==''):
            return 'write your user ID and Password'
        else:
            conn = sqlite3.connect('test_info.db', check_same_thread=False)
            cur=conn.cursor()

            cur.execute(f'SELECT uid FROM USER_INFO;')
            user_id_db=cur.fetchall()

            if (userid, ) in user_id_db:
                conn.close()
                return 'already exist.'         
            else: 
                cur.execute(f'INSERT INTO USER_INFO(uid, upw) VALUES(?, ?);',(userid, userpw))
                conn.commit()
                conn.close()
                return redirect(url_for('login'))


@app.route('/list')
def list():
    
    conn = sqlite3.connect('test_info.db', check_same_thread=False)
    cur=conn.cursor()
    cur.execute(f'CREATE TABLE IF NOT EXISTS CONTENT_INFO(uid TEXT, title TEXT, content TEXT, file BLOB);')
    conn.commit()

    if 'login_user' in session:
        conn=sqlite3.connect('test_info.db', check_same_thread=False)
        cur=conn.cursor()

        cur.execute("SELECT rowid, * FROM CONTENT_INFO;")
        rows=cur.fetchall()
        conn.close()

        return render_template("list.html",rows=rows)
    
    else:
        return redirect(url_for('login'))


@app.route('/write',methods=['POST','GET'])
def write():
    if request.method=='GET':
        return render_template("write.html",login_user=session['login_user'])

    else :
        userid=session['login_user']
        n_title=request.form['title']
        n_content=request.form['content']
        n_file=request.form['file']
        
        conn=sqlite3.connect('test_info.db', check_same_thread=False)
        cur=conn.cursor()
        cur.execute(f'CREATE TABLE IF NOT EXISTS CONTENT_INFO(uid TEXT, title TEXT, content TEXT, file BLOB);')
        conn.commit()

        cur.execute(f'INSERT INTO CONTENT_INFO(uid, title, content, file) VALUES(?, ?, ?, ?);',(userid, n_title, n_content, n_file))
        conn.commit()
        conn.close()
        return redirect(url_for('list'))


@app.route('/detail',methods=['POST'])
def detail():
    contentid=request.form['rowid']
    print(contentid)
    return render_template('modify.html',login_user=session['login_user'],rowid=contentid)


@app.route('/modify',methods=['POST', 'GET'])
def modify():
    if 'login_user' in session:
        title=request.form['title']
        content=request.form['content']
        contentid=request.form['row_id']
        userid=session['login_user']
        # print(contentid)

        conn = sqlite3.connect('test_info.db', check_same_thread=False)
        cur=conn.cursor()

        cur.execute(f'SELECT uid FROM CONTENT_INFO WHERE rowid=?;', (contentid))
        write_user=cur.fetchone()
        # print(write_user)

        if userid in write_user :
            cur.execute(f'UPDATE CONTENT_INFO SET uid=?, title=?, content=?  WHERE rowid=?;', (userid, title, content, contentid))
            conn.commit()
            conn.close()
            return redirect(url_for('list'))
        else:
            conn.close()
            return "Cannot be modified"
    else : 
        return 'error'


@app.route('/delete', methods=['POST'])
def delete():
    contentid=request.form['row_id']
    userid=session['login_user']

    conn = sqlite3.connect('test_info.db', check_same_thread=False)
    cur=conn.cursor()

    cur.execute(f'SELECT uid FROM CONTENT_INFO WHERE rowid=?;', (contentid))
    write_user=cur.fetchone()

    if userid in write_user:
        cur.execute(f'DELETE FROM CONTENT_INFO WHERE rowid=?;', (contentid))
        conn.commit()
        conn.close()
        return redirect(url_for('list'))
    else : 
        conn.close()
        return "Cannot delete"



if __name__=="__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)