from flask import Flask
import flask.ext.login as flask_login

app = Flask(__name__, static_url_path="")
app.secret_key = 'development'

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

SALT = 'development'

import soulvest.views
