from flask import Flask, request, render_template
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_DIR = os.path.join(BASE_DIR, 'ctf.db')

# Tato funkce potřebuje práva k zápisu, aby mohla DB vytvořit
def init_db():
    conn = sqlite3.connect(DB_DIR)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS users')
    c.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    c.execute("INSERT INTO users (username, password) VALUES ('Karlik', 'Karlikovo_tajne_heslo_15311563')")
    c.execute("INSERT INTO users (username, password) VALUES ('admin', 'super_tajne_heslo_123_ktere_nikdo_neuhodne_1564186165')")
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

        # 🛡️ OCHRANA PROTI ROZBITÍ DB: Připojení v Read-Only režimu
        # Použijeme URI formát a přidáme parametr ?mode=ro
        try:
            conn = sqlite3.connect(f'file:{DB_DIR}?mode=ro', uri=True)
            c = conn.cursor()

            # Zranitelný dotaz zůstává
            first_password_query = c.execute("SELECT password FROM users WHERE username=?", (username,))
            print("lol")
            query_output = first_password_query.fetchone()
            print("lol2")
            if query_output is None:
                error = "Neplatné přihlašovací údaje."
                return render_template('login.html', error=error)

            user_password, = query_output
            print(user_password)

            second_password_query = f'SELECT password FROM users WHERE username = "{username}" AND password = "{password}"'
            print("lol3")
            c.execute(second_password_query)

            query_output = c.fetchone()

            if query_output is None:
                error = "Neplatné přihlašovací údaje."
                return render_template('login.html', error=error)

            control_user_password, = query_output

            if username == 'admin' and user_password == control_user_password:
                return render_template('flag.html')
            else:
                error = "Neplatné přihlašovací údaje."

        except sqlite3.OperationalError as e:
            # Zachytíme chyby. Pokud se někdo pokusí o zápis do RO databáze, hodí to chybu.
            error = f"{e}"
        except Exception as e:
             error = f"Nastala nečekaná chyba, napiš do diskuze na KSI {e}"
        finally:

            if 'conn' in locals():
                conn.close()

    return render_template('login.html', error=error)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)