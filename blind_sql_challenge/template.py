import socket
import sys

class BlindSQLClient:
    def __init__(self, host, port, token):
        self.host = host
        self.port = port
        self.token = token
    
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        self._connect_and_authenticate()

    def _read_until(self, expected_text):
        data = ""
        while expected_text not in data:
            chunk = self.sock.recv(1024).decode('utf-8')
            if not chunk:
                raise ConnectionError("Spojení bylo neočekávaně ukončeno serverem. Napiš do diskuze v KSI.")
            data += chunk
        return data

    def _connect_and_authenticate(self):
        try:
            self.sock.connect((self.host, self.port))
        except ConnectionRefusedError:
            print("[-] Nelze se připojit. Běží server? Stáhni si znova kostru, pokud i to nefunguje, napiš do diskuze na KSI.")
            sys.exit(1)

        self.sock.sendall((self.token + "\n").encode('utf-8'))

        uvod = self._read_until("SQL> ")
        if "Nespravny token" in uvod:
            print("[-] Chyba: Nesprávný session token! Stáhni si znova kostru, pokud i to nefunguje, napiš do diskuze na KSI.")
            sys.exit(1)
            
        print("[+] Session úspěšně navázána!\n")

    def ask_database(self, query):
        self.sock.sendall((query + "\n").encode('utf-8'))
        
        odpoved = self._read_until("SQL> ")

        if "Yes" in odpoved:
            return True
        elif "No" in odpoved:
            return False
        else:
            print(odpoved.split("\n", 1)[0])

        return False


if __name__ == "__main__":
    HOST = "89.221.215.195"
    PORT = 9999
    TOKEN = "KSI_ctf_session_2026"

    client = BlindSQLClient(HOST, PORT, TOKEN)

    # ==========================================
    #           NÍŽE PIŠTE SVŮJ KÓD 
    # ==========================================

    # Příklad
    dotaz = "SELECT * FROM messages"

    vysledek = client.ask_database(dotaz) # Proměnná vysledek bude bool (True/False)

    if vysledek:
        print("Pravda")
    else:
        print("Nepravda")
