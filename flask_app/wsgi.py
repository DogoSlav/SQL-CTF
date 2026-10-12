from werkzeug.middleware.dispatcher import DispatcherMiddleware
from flask import Flask

from chalenge1.app import app as site1_app
from chalenge2.app import app as site2_app
from chalenge3.app import app as site3_app
from chalenge4.app import app as site4_app
from config import FLASK_DEBUG, FLASK_HOST, FLASK_PORT

main_app = Flask(__name__)

application = DispatcherMiddleware(main_app, {
    '/nuioghabyiaw/site1': site1_app,
    '/nuioghabyiaw/site2': site2_app,
    '/nuioghabyiaw/site3': site3_app,
    '/nuioghabyiaw/site4': site4_app
})

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple(
        FLASK_HOST,
        FLASK_PORT,
        application,
        use_reloader=FLASK_DEBUG,
        use_debugger=FLASK_DEBUG,
    )