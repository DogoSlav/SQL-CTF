# Použijeme lehký oficiální Python image
FROM python:3.11-slim

# Nastavení pracovního adresáře v kontejneru
WORKDIR /app

# Zkopírování našeho skriptu do kontejneru
COPY . .

# Otevření portu 9999 pro komunikaci
EXPOSE 9999

# Příkaz, který se spustí při startu kontejneru
CMD ["python", "-u", "tcp_blind_sql.py"]
