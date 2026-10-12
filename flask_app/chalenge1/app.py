from flask import Flask, request, render_template
import sqlite3
import os
from config import (
    CHALLENGE1_ADMIN_PASSWORD,
    CHALLENGE1_FLAG,
    FLASK_DEBUG,
    FLASK_HOST,
    FLASK_PORT,
)

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_DIR = os.path.join(BASE_DIR, 'ctf.db')

def init_db():
    conn = sqlite3.connect(DB_DIR)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS users')
    c.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', CHALLENGE1_ADMIN_PASSWORD))
    conn.commit()
    conn.close()

if not os.path.exists(DB_DIR):
    init_db()
else:
    init_db() 

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        try:
            conn = sqlite3.connect(f'file:{DB_DIR}?mode=ro', uri=True)
            c = conn.cursor()

            query = f'SELECT * FROM users WHERE username = "{username}" AND password = "{password}"'
            error = f"query: {query}\n\n"

            c.execute(query)
            user = c.fetchone()

            if user:
                return render_template('flag.html', flag=CHALLENGE1_FLAG)
            else:
                error += "Neplatné přihlašovací údaje."

        except sqlite3.OperationalError as e:
            error += f"{e}"
        except Exception as e:
             error += "Nastala nečekaná chyba, napiš do diskuze na KSI"
        finally:

            if 'conn' in locals():
                conn.close()

    return render_template('login.html', error=error)

if __name__ == '__main__':
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT)