from werkzeug.middleware.dispatcher import DispatcherMiddleware
from flask import Flask

# Import tvých aplikací
from chalenge1.app import app as site1_app
from chalenge2.app import app as site2_app
from chalenge3.app import app as site3_app
from chalenge4.app import app as site3_app

# Hlavní (root) aplikace - co se stane, když někdo přijde na tvou hlavní doménu '/'
main_app = Flask(__name__)

@main_app.route('/')
def index():
    return "Vítejte na hlavním portálu! Zkuste /site1 nebo /site2."

# Zde se děje kouzlo - namapování cest
application = DispatcherMiddleware(main_app, {
    '/site1': site1_app,
    '/site2': site2_app,
    '/site3': site3_app
})

# Pro lokální testování (spustíš pomocí: python wsgi.py)
if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 5000, application, use_reloader=True, use_debugger=True)