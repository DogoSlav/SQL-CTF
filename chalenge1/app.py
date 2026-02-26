from flask import Flask, request, render_template
import sqlite3
import os

app = Flask(__name__)

# Tato funkce potřebuje práva k zápisu, aby mohla DB vytvořit
def init_db():
    conn = sqlite3.connect('ctf.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS users')
    c.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    c.execute("INSERT INTO users (username, password) VALUES ('admin', 'super_tajne_heslo_123_ktere_nikdo_neuhodne')")
    conn.commit()
    conn.close()

if not os.path.exists('ctf.db'):
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
            conn = sqlite3.connect('file:ctf.db?mode=ro', uri=True)
            c = conn.cursor()

            # Zranitelný dotaz zůstává
            query = f'SELECT * FROM users WHERE username = "{username}" AND password = "{password}"'
            error = f"query: {query}\n\n"
            # Při ladění můžeš nechat vypsat
            print(f"Spouštím dotaz: {query}") 
            
            # Pokud útočník pošle DROP TABLE nebo UPDATE, SQLite vyhodí výjimku, 
            # protože spojení je pouze pro čtení. Úloha tak zůstane funkční pro ostatní.
            
            # Abychom zabránili pádu aplikace při více příkazech oddělených středníkem 
            # (např. "admin'; DROP TABLE users; --"), použijeme executescript() nebo ošetříme chybu.
            # Metoda execute() ve sqlite3 standardně zpracuje jen první dotaz, což nás také částečně chrání.
            c.execute(query)
            user = c.fetchone()

            if user:
                return render_template('flag.html')
            else:
                error += "Neplatné přihlašovací údaje."

        except sqlite3.OperationalError as e:
            # Zachytíme chyby. Pokud se někdo pokusí o zápis do RO databáze, hodí to chybu.
            error += f"{e}"
        except Exception as e:
             error += "Nastala nečekaná chyba, napiš do diskuze na KSI"
        finally:

            if 'conn' in locals():
                conn.close()

    return render_template('login.html', error=error)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)