import os
import socketserver
import sqlite3
import socket  # Importujeme socket pro zachycení výjimky socket.timeout
import json

# Konfigurace
HOST = "0.0.0.0"
PORT = 9999
UNIVERSAL_SESSION_TOKEN = os.getenv("CHALLENGE_TOKEN", "moje_ctf_session_2026")
FLAG = os.getenv("CHALLENGE_FLAG", "KSI{error}")
TIMEOUT_SECONDS = 60 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, 'ctf.db')
# Cesta k souboru databáze
DB_PATH = DB_DIR

def setup_readonly_db():
    print("[*] Generuji databázi...")
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, message TEXT NOT NULL)")
    cursor.execute("CREATE TABLE parek917 (first TEXT, second)")
    cursor.execute("CREATE TABLE maintenance (id INTEGER PRIMARY KEY AUTOINCREMENT, flag TEXT NOT NULL, number NOT NULL)")

    first_messages = [
        ("Karlík", "Ahoj, parku"),
        ("parek917", "Ahoj, co potrebujes?"),
        ("Deep", "Nekdo lolko?"),
        ("Karlík", "Potreboval bych zase... ty vis co...")
        ("parek917", "Jasne, najdes to v tabulce, ktera ma nazev jako muj username. Dale je to uloze ve dvou sloupcich s nazvem first a last"),
        ("heppsak", "Hledam holku co se neboji rychlych aut.")
        ("Karlík", "Díky, mas to u me.")
    ]

    first_flag_database = [
        (FLAG[:16], "Druha cast vlajky se presunula z technickych duvodu do tabulky maintenance. Obsahuje sloupce flag a number. V tabulce maintenance se nachazi vice vlajek. Vase vlajka je v tabulce zde ulozena nekolikrat. Vase vlajka ma celkovy soucet u sloupce number 67.")
    ]

    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    maintenance_data = [
        [(row["string"], row["cislo"]) for row in data]
    ]

    cursor.executemany("INSERT INTO maintenance VALUES (?, ?)", maintenance_data)

    for frst, scnd in first_flag_database:
        cursor.execute("INSERT INTO parek917 (first, second) VALUES (?, ?)", (frst, scnd))

    cursor.executemany("INSERT INTO messages (username, password) VALUES (?, ?)", first_messages)
    
    conn.commit()
    conn.close()
    print("[+] Databáze připravena.")

class BlindSQLHandler(socketserver.BaseRequestHandler):
    def send_msg(self, msg):
        try:
            self.request.sendall((msg + "\n").encode('utf-8'))
        except Exception:
            pass

    def handle(self):
        # 1. NASTAVENÍ TIMEOUTU:
        # Pokud klient nepošle žádná data po dobu 900 vteřin,
        # funkce self.request.recv() vyhodí výjimku socket.timeout
        self.request.settimeout(TIMEOUT_SECONDS)
        
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        cursor = conn.cursor()

        try:
            
            token = self.request.recv(1024).strip().decode('utf-8')
            if token != UNIVERSAL_SESSION_TOKEN:
                return
            
            while True:
                self.send_msg("SQL> ")
                # Zde server čeká na data. Pokud uběhne 15 minut, skočí to do except socket.timeout
                data = self.request.recv(4096).strip()
                if not data: 
                    break # Klient ukončil spojení standardně
                
                query = data.decode('utf-8')
                if query.lower() in ['exit', 'quit']:
                    self.send_msg("Bye!")
                    break

                try:
                    cursor.execute(query)
                    result = cursor.fetchone()
                    
                    if result is not None:
                        self.send_msg("Yes")
                    else:
                        self.send_msg("No")
                        
                except sqlite3.OperationalError:
                    self.send_msg("Ne (Nepovolená operace - databáze je read-only)")
                except sqlite3.Error:
                    self.send_msg("Ne (Chyba syntaxe)")

        except socket.timeout:
            # 2. ZACHYCENÍ TIMEOUTU
            # Dáme uživateli vědět, proč ho odpojujeme (dobrá praxe u CTF)
            self.send_msg("\nTimeout")
            print(f"[*] Klient {self.client_address} byl odpojen z důvodu timeoutu.")
            
        except ConnectionResetError:
            # Uživatel násilně zavřel terminál
            pass
        except Exception as e:
            pass
        finally:
            # Bez ohledu na to, zda došlo k timeoutu, chybě nebo normálnímu konci, 
            # musíme zavřít spojení do DB.
            conn.close()

if __name__ == "__main__":
    setup_readonly_db()
    
    print(f"[*] Spoustim server na portu {PORT} s timeoutem {TIMEOUT_SECONDS}s...")
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer((HOST, PORT), BlindSQLHandler) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nUkončuji server...")