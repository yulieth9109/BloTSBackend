from flask import Flask
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager
from flask_mail import Mail
from .dbManager import dbManager
from flask_cors import CORS


dbManagerC = dbManager()
app = Flask(__name__,template_folder='templates')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
mail = Mail(app)

def create_app():
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SECURITY_PASSWORD_SALT'] = 'my_precious_two'
    app.config['MAIL_USERNAME'] = 'blots.contact@gmail.com'
    app.config['MAIL_PASSWORD'] = 'shjnkmhgijiidcaf'
    app.config['MAIL_DEFAULT_SENDER'] = 'blots.contact@gmail.com'
    # mail settings
    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] =  465
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    login_manager = LoginManager(app)
    login_manager.init_app(app)

    from .routes import routes

    app.register_blueprint(routes, url_prefix='/')
    
    mail = Mail(app)

    @login_manager.user_loader
    def load_user(email):
        return dbManagerC.getUserInfo(email)

    return app

