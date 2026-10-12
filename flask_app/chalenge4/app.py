from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import random
import string
import os
import re
from config import CHALLENGE4_FLAG, FLASK_DEBUG, FLASK_PORT, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_DIR = os.path.join(BASE_DIR, 'user_dbs')

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

def get_db_path(username):
    """Vrátí cestu k databázi uživatele ve složce user_dbs."""
    safe_username = re.sub(r'[^a-zA-Z0-9_]', '', username)
    return os.path.join(DB_DIR, f"{safe_username}.db")

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def init_user_db(username, password):
    """Vytvoří izolovanou databázi pro konkrétního uživatele a naplní ji daty."""
    db_path = get_db_path(username)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('CREATE TABLE users (username TEXT, password TEXT, email TEXT)')
    c.execute('CREATE TABLE age (username TEXT, age INTEGER)')
    c.execute('CREATE TABLE messages (username TEXT, msg TEXT)')
    
    c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (username, password, ""))
    c.execute("INSERT INTO age (username, age) VALUES (?, ?)", (username, 15))
    
    dummy_messages = [
        ("Karlík", "Dneska to v nočním klubu žije! Vstup jen pro dospělé."),
        ("Anonymka99", "Ahoj, je tu někdo?"),
        ("Admin", "Nezapomeňte si v nastavení vyplnit e-mail pro upozornění.")
    ]
    for user, msg in dummy_messages:
        c.execute("INSERT INTO messages (username, msg) VALUES (?, ?)", (user, msg))
        
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dating'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        db_path = get_db_path(username)
    
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()
            conn.close()

            if user:
                session['username'] = username
                return redirect(url_for('dating'))
            else:
                error = "Neplatné heslo."
        else:
            error = "Uživatel neexistuje. Vygeneruj si účet."

    return render_template('login.html', error=error)

@app.route('/generate_user')
def generate_user():
    username = "user_" + generate_random_string(5)
    password = generate_random_string(8)

    init_user_db(username, password)
    
    flash(f"Tvé nové údaje:\nJméno: {username}\nHeslo: {password}")
    return redirect(url_for('login'))

@app.route('/dating', methods=['GET', 'POST'])
def dating():
    if 'username' not in session: return redirect(url_for('login'))
    
    username = session['username']
    try:
        db_path = get_db_path(username)
    except:
        session.pop('username', None)
        return redirect(url_for('login'))

    if not os.path.exists(db_path): 
        return redirect(url_for('logout'))

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    if request.method == 'POST':
        msg = request.form.get('message')
        if msg:
            c.execute("INSERT INTO messages (username, msg) VALUES (?, ?)", (username, msg))
            conn.commit()
            
    c.execute("SELECT username, msg FROM messages ORDER BY ROWID DESC LIMIT 20")
    messages = c.fetchall()
    
    try:
        c.execute("SELECT age FROM age WHERE username=?", (username,))
        age_row = c.fetchone()
        current_age = age_row[0] if age_row else 0
    except sqlite3.OperationalError:
        current_age = "Neznámý (tabulka smazána)"
        
    conn.close()

    return render_template('dating.html', messages=messages, age=current_age)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'username' not in session: return redirect(url_for('login'))
    
    username = session['username']
    try:
        db_path = get_db_path(username)
    except:
        session.pop('username', None)
        return redirect(url_for('login'))
    msg = None

    if request.method == 'POST':
        email = request.form.get('email')
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        vulnerable_query = f"UPDATE users SET email = '{email}' WHERE username = '{username}';"

        try:
            assert len(email) <= 26
            c.executescript(vulnerable_query)
            conn.commit()
            msg = "E-mail byl úspěšně aktualizován."    
        except AssertionError:
            msg = "Email je moc dlouhý!"
        except Exception as e:
            msg = f"SQL Error"
        finally:
            conn.close()

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute("SELECT email FROM users WHERE username=?", (username,))
        row = c.fetchone()
        current_email = row[0] if row else ""
    except sqlite3.OperationalError:
        current_email = "Chyba načítání (tabulka users možná neexistuje)"
    conn.close()

    return render_template('settings.html', email=current_email, msg=msg)

@app.route('/klub')
def klub():
    if 'username' not in session: return redirect(url_for('login'))
    
    username = session['username']
    try:
        db_path = get_db_path(username)
    except:
        session.pop('username', None)
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute("SELECT age FROM age WHERE username=?", (username,))
        row = c.fetchone()
        age = row[0] if row else 0
    except sqlite3.OperationalError:
        age = 0
    finally:
        conn.close()
    
    if isinstance(age, int) and age > 18:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("UPDATE age SET age=15")
        conn.commit()
        conn.close()
        return render_template('klub.html', success=True, flag=CHALLENGE4_FLAG)
    else:
        return render_template('klub.html', success=False, age=age)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=FLASK_DEBUG, port=FLASK_PORT)