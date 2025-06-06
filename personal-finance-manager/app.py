from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = 'secret123'

# Database Setup
def init_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, category TEXT, amount REAL, date TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Authentication Decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_id' in session:
            return f(*args, **kwargs)
        else:
            flash("Login First", "danger")
            return redirect(url_for('login'))
    return wrap

# Routes
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        flash("Registered Successfully!", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid Credentials!", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        category = request.form['category']
        amount = float(request.form['amount'])
        date = request.form['date']
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        c.execute("INSERT INTO expenses (user_id, category, amount, date) VALUES (?, ?, ?, ?)",
                  (session['user_id'], category, amount, date))
        conn.commit()
        conn.close()
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("SELECT category, amount, date FROM expenses WHERE user_id=?", (session['user_id'],))
    expenses = c.fetchall()
    conn.close()
    return render_template('dashboard.html', expenses=expenses)

@app.route('/reports')
@login_required
def reports():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("SELECT category, SUM(amount) FROM expenses WHERE user_id=? GROUP BY category", (session['user_id'],))
    data = c.fetchall()
    conn.close()
    labels = [row[0] for row in data]
    values = [row[1] for row in data]
    return render_template('reports.html', labels=labels, values=values)

if __name__ == '__main__':
    app.run(debug=True)

