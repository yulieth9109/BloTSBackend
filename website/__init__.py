from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager
from flask_mail import Mail
from .dbManager import dbManager
from flask_cors import CORS
import website.parameters as parameters


dbManagerC = dbManager()
CORS_ALLOW_ORIGIN="*,*"
CORS_EXPOSE_HEADERS="*,*"
CORS_ALLOW_HEADERS="content-type,*"
app = Flask(__name__,template_folder='templates')
cors = CORS(app, origins=CORS_ALLOW_ORIGIN.split(","), allow_headers=CORS_ALLOW_HEADERS.split(",") , expose_headers= CORS_EXPOSE_HEADERS.split(","),   supports_credentials = True)
mail = Mail(app)

def create_app():
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SECURITY_PASSWORD_SALT'] = 'my_precious_two'
    app.config['MAIL_USERNAME'] = parameters.emailU
    app.config['MAIL_PASSWORD'] = parameters.emailP
    app.config['MAIL_DEFAULT_SENDER'] = parameters.emailU
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    # mail settings
    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] =  465
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    login_manager = LoginManager(app)
    login_manager.session_protection = None
    login_manager.init_app(app)
    

    from .routes import routes

    app.register_blueprint(routes, url_prefix='/')
    
    mail = Mail(app)

    @login_manager.user_loader
    def load_user(email):
        return dbManagerC.getUserInfo(email)

    return app


