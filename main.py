from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = "your_secret_key"

# SQLite Database Path
db_path = 'sentidb.db'

# Password hashing function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    next_page = request.args.get('next', '/')
    if request.method == 'POST':
        email = request.form['email']
        pwd = hash_password(request.form['pwd'])
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT uid FROM users WHERE email = ? AND pwd = ?", (email, pwd))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['uid'] = user[0]
            return redirect(next_page)
        else:
            return "Invalid email or password"
    return render_template('login.html', next=next_page)

@app.route('/user/register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        pwd = hash_password(request.form['pwd'])
        gender = request.form['gender']
        height = float(request.form['height'])
        weight = float(request.form['weight'])
        dob = request.form['dob']
        state = request.form['state']
        city = request.form['city']

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (fname, lname, email, pwd, gender, height, weight, dob, state, city)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (fname, lname, email, pwd, gender, height, weight, dob, state, city))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('user_register.html')

@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    return redirect(url_for('login'))

@app.route('/user/dashboard')
def user_dashboard():
    if 'uid' not in session:
        return redirect(url_for('login', next=request.url))
    uid = session['uid']
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT feedback.fid, products.product, feedback.feedback, feedback.sentiment
        FROM feedback
        JOIN products ON feedback.pid = products.pid
        WHERE feedback.uid = ?
    """, (uid,))
    feedbacks = cursor.fetchall()
    conn.close()
    return render_template('user_dashboard.html', feedbacks=feedbacks)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        if 'uid' in session:
            uid = session['uid']
            pid = request.form['pid']
            feedback_text = request.form['feedback']
            sentiment = 'neutral'  # Default sentiment

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO feedback (uid, pid, feedback, sentiment)
                VALUES (?, ?, ?, ?)
            """, (uid, pid, feedback_text, sentiment))
            conn.commit()
            conn.close()
            return redirect(url_for('feedback'))
        else:
            return redirect(url_for('login', next=request.url))
    if 'uid' in session:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT pid, product FROM products")
        products = cursor.fetchall()
        conn.close()
        return render_template('feedback.html', products=products)
    else:
        return redirect(url_for('login', next=request.url))

@app.route('/company/register', methods=['GET', 'POST'])
def company_register():
    if request.method == 'POST':
        company = request.form['company']
        email = request.form['email']
        pwd = hash_password(request.form['pwd'])

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO companies (company, email, pwd)
            VALUES (?, ?, ?)
        """, (company, email, pwd))
        conn.commit()
        conn.close()
        return redirect(url_for('company_login'))
    return render_template('company_register.html')

@app.route('/company/login', methods=['GET', 'POST'])
def company_login():
    if request.method == 'POST':
        email = request.form['email']
        pwd = hash_password(request.form['pwd'])
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT cid FROM companies WHERE email = ? AND pwd = ?", (email, pwd))
        company = cursor.fetchone()
        conn.close()
        if company:
            session['cid'] = company[0]
            return redirect(url_for('index'))
        else:
            return "Invalid email or password"
    return render_template('company_login.html')

if __name__ == '__main__':
    app.run(debug=True)