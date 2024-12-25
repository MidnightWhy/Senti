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
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                uid TEXT PRIMARY KEY,
                fname TEXT,
                lname TEXT,
                email TEXT,
                pwd TEXT,
                gender TEXT,
                height REAL,
                weight REAL,
                dob TEXT,
                state TEXT,
                city TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                cid TEXT PRIMARY KEY,
                company TEXT,
                email TEXT,
                pwd TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                pid TEXT PRIMARY KEY,
                cid TEXT,
                product TEXT,
                thumbnail TEXT,
                barcode TEXT,
                FOREIGN KEY (cid) REFERENCES companies(cid)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                fid TEXT PRIMARY KEY,
                uid TEXT,
                pid TEXT,
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


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user/register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        uid = request.form['uid']
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

        # Insert data into the users table
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        query = """
            INSERT INTO users (uid, fname, lname, email, pwd, gender, height, weight, dob, state, city)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        values = (uid, fname, lname, email, pwd, gender, height, weight, dob,
                  state, city)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()

        # Redirect to login page
        return redirect(url_for('user_login'))
    return render_template('user_register.html')


@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        pwd = hash_password(request.form['pwd'])
        # Query the database for the user
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE email = ? AND pwd = ?"
        values = (email, pwd)
        cursor.execute(query, values)
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            # Store user id in session
            session['uid'] = user[0]
            return redirect(url_for('index'))
        else:
            # Invalid credentials
            return "Invalid email or password"
    return render_template('user_login.html')


@app.route('/company/register', methods=['GET', 'POST'])
def company_register():
    if request.method == 'POST':
        cid = request.form['cid']
        company = request.form['company']
        email = request.form['email']
        pwd = hash_password(request.form['pwd'])

        # Insert data into the companies table
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        query = """
            INSERT INTO companies (cid, company, email, pwd)
            VALUES (?, ?, ?, ?)
        """
        values = (cid, company, email, pwd)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()

        # Redirect to login page
        return redirect(url_for('company_login'))
    return render_template('company_register.html')


@app.route('/company/login', methods=['GET', 'POST'])
def company_login():
    if request.method == 'POST':
        email = request.form['email']
        pwd = hash_password(request.form['pwd'])
        # Query the database for the company
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        query = "SELECT * FROM companies WHERE email = ? AND pwd = ?"
        values = (email, pwd)
        cursor.execute(query, values)
        company = cursor.fetchone()
        cursor.close()
        conn.close()
        if company:
            # Store company id in session
            session['cid'] = company[0]
            return redirect(url_for('index'))
        else:
            # Invalid credentials
            return "Invalid email or password"
    return render_template('company_login.html')


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'uid' not in session:
        return redirect(url_for('user_login'))
    if request.method == 'POST':
        fid = request.form['fid']
        uid = session['uid']
        pid = request.form['pid']
        feedback_text = request.form['feedback']
        sentiment = request.form['sentiment']

        # Insert data into the feedback table
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        query = """
            INSERT INTO feedback (fid, uid, pid, feedback, sentiment)
            VALUES (?, ?, ?, ?, ?)
        """
        values = (fid, uid, pid, feedback_text, sentiment)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()

        # Redirect to index page
        return redirect(url_for('index'))
    return render_template('feedback.html')


if __name__ == '__main__':
    app.run(debug=True)
