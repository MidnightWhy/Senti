from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = "your_secret_key"

# SQLite Database Path
db_path = 'sentidb.db'


# Initialize database and create tables
def init_db():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                uid INTEGER PRIMARY KEY AUTOINCREMENT,
                fname TEXT,
                lname TEXT,
                email TEXT UNIQUE,
                pwd TEXT,
                gender TEXT,
                height REAL,
                weight REAL,
                dob TEXT,
                state TEXT,
                city TEXT
            );

            CREATE TABLE IF NOT EXISTS companies (
                cid INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT,
                email TEXT UNIQUE,
                pwd TEXT
            );

            CREATE TABLE IF NOT EXISTS products (
                pid INTEGER PRIMARY KEY AUTOINCREMENT,
                cid INTEGER,
                product TEXT,
                thumbnail TEXT,
                barcode TEXT,
                FOREIGN KEY (cid) REFERENCES companies(cid)
            );

            CREATE TABLE IF NOT EXISTS feedback (
                fid INTEGER PRIMARY KEY AUTOINCREMENT,
                uid INTEGER,
                pid INTEGER,
                feedback TEXT,
                sentiment TEXT,
                FOREIGN KEY (uid) REFERENCES users(uid),
                FOREIGN KEY (pid) REFERENCES products(pid)
            );
        """)
        conn.commit()
        conn.close()
    except sqlite3.Error as err:
        print(f"Database error: {err}")


init_db()


# Password hashing function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@app.route('/')
def index():
    return render_template('index.html')


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
        """, (fname, lname, email, pwd, gender, height, weight, dob, state,
              city))
        conn.commit()
        conn.close()
        return redirect(url_for('user_login'))
    return render_template('user_register.html')


@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        pwd = hash_password(request.form['pwd'])
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND pwd = ?",
                       (email, pwd))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['uid'] = user[0]
            return redirect(url_for('user_dashboard'))
        else:
            return "Invalid email or password"
    return render_template('user_login.html')


@app.route('/user/dashboard')
def user_dashboard():
    if 'uid' not in session:
        return redirect(url_for('user_login'))
    uid = session['uid']
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT feedback.fid, products.product, feedback.feedback, feedback.sentiment
        FROM feedback
        JOIN products ON feedback.pid = products.pid
        WHERE feedback.uid = ?
    """, (uid, ))
    feedbacks = cursor.fetchall()
    cursor.execute("SELECT pid, product FROM products")
    products = cursor.fetchall()
    conn.close()
    return render_template('user_dashboard.html',
                           feedbacks=feedbacks,
                           products=products)


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
        cursor.execute("SELECT * FROM companies WHERE email = ? AND pwd = ?",
                       (email, pwd))
        company = cursor.fetchone()
        conn.close()
        if company:
            session['cid'] = company[0]
            return redirect(url_for('index'))
        else:
            return "Invalid email or password"
    return render_template('company_login.html')


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'uid' not in session:
        return redirect(url_for('user_login'))
    if request.method == 'POST':
        uid = session['uid']
        pid = request.form['pid']
        feedback_text = request.form['feedback']
        sentiment = request.form['sentiment']

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO feedback (uid, pid, feedback, sentiment)
            VALUES (?, ?, ?, ?)
        """, (uid, pid, feedback_text, sentiment))
        conn.commit()
        conn.close()
        return redirect(url_for('user_dashboard'))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT pid, product FROM products")
    products = cursor.fetchall()
    conn.close()
    return render_template('feedback.html', products=products)


if __name__ == '__main__':
    app.run(debug=True)
