import os
import socketserver
import sqlite3
import threading

# Načtení konfigurace z prostředí (nebo použití výchozích hodnot)
HOST = "0.0.0.0"
PORT = 9999
UNIVERSAL_SESSION_TOKEN = os.getenv("CHALLENGE_TOKEN", "defaultni_token_123")
FLAG = os.getenv("CHALLENGE_FLAG", "CTF{defaultni_vlajka}")

def init_db():
    # Vytvoření in-memory databáze
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    cursor.execute("CREATE TABLE flags (id INTEGER PRIMARY KEY, secret TEXT)")
    
    # Vložení dat do databáze
    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123')")
    cursor.execute("INSERT INTO flags (secret) VALUES (?)", (FLAG,))
    conn.commit()
    return conn

db_conn = init_db()
db_lock = threading.Lock()

class BlindSQLHandler(socketserver.BaseRequestHandler):
    def send_msg(self, msg):
        try:
            self.request.sendall((msg + "\n").encode('utf-8'))
        except Exception:
            pass

    def handle(self):
        self.send_msg("=== B-SQL Challenge Server ===")
        self.send_msg("Zadej session token:")
        
        try:
            token = self.request.recv(1024).strip().decode('utf-8')
            if token != UNIVERSAL_SESSION_TOKEN:
                self.send_msg("Nespravny token.")
                return
            
            self.send_msg("Token OK. Zadej SQL dotaz (napr. SELECT * FROM users).")
            
            while True:
                self.send_msg("SQL> ")
                data = self.request.recv(4096).strip()
                if not data: break
                
                query = data.decode('utf-8')
                if query.lower() in ['exit', 'quit']:
                    self.send_msg("Bye!")
                    break

                try:
                    with db_lock:
                        cursor = db_conn.cursor()
                        cursor.execute(query)
                        # Pokud dotaz vrátí alespoň jeden řádek, result nebude None
                        result = cursor.fetchone()
                        
                        if result is not None:
                            self.send_msg("Ano")
                        else:
                            self.send_msg("Ne")
                            
                except sqlite3.Error:
                    # Zamaskujeme SQL chybu, aby to bylo plně "blind"
                    self.send_msg("Ne (Chyba syntaxe)")
                    
        except Exception:
            pass

if __name__ == "__main__":
    print(f"Spoustim server na portu {PORT}...")
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer((HOST, PORT), BlindSQLHandler) as server:
        server.serve_forever()