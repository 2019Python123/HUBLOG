from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask import Flask
from config import config
from flask_login import LoginManager
from flask_pagedown import PageDown
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()
db = SQLAlchemy()
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
pagedown = PageDown()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__,template_folder='templates',static_folder='static')
    app.config.from_object(config['config'])
    config['config'].init_app(app)
    db.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    pagedown.init_app(app)
    moment.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    from .auth import auth as  auth_bp
    app.register_blueprint(auth_bp,url_prefix='/auth')
    from .admin import admin as admin_bp
    app.register_blueprint(admin_bp,url_prefix='/admin')
    from .blog import blog as blog_bp
    app.register_blueprint(blog_bp,url_prefix='/blog')
    from .main import main as main_bp
    app.register_blueprint(main_bp)
    return app


