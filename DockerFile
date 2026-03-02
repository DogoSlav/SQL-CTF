# 1. Použijeme oficiální a odlehčený obraz Pythonu
FROM python:3.11-slim

# 2. Nastavíme pracovní adresář uvnitř kontejneru
WORKDIR /app

# 3. Zkopírujeme soubor s knihovnami do kontejneru
COPY requirements.txt .

# 4. Nainstalujeme všechny knihovny z tvého seznamu
RUN pip install --no-cache-dir -r requirements.txt

# 5. Zkopírujeme zbytek tvého kódu (složky site1, site2, wsgi.py atd.) do kontejneru
COPY . .

# 6. Řekneme Dockeru, že aplikace poběží na portu 8000
EXPOSE 8000

# 7. Příkaz pro spuštění produkčního serveru Gunicorn
# -w 4 znamená 4 workery (pro těch cca 80 lidí)
# -b 0.0.0.0:8000 znamená, že to bude poslouchat všechny příchozí dotazy uvnitř kontejneru
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "wsgi:application"]