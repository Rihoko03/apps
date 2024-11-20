from pathlib import Path
from flask import Flask, request, session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from apps.config import config
from flask_login import LoginManager

csrf = CSRFProtect()
db = SQLAlchemy()
login_manager = LoginManager()

login_manager.login_message = "ログインしてください"

def create_app(config_key):
    app = Flask(__name__)
    app.config.from_object(config[config_key])

    csrf.init_app(app)
    db.init_app(app)
    Migrate(app, db)
    login_manager.init_app(app)

    @app.before_request
    def set_login_view():
        # リクエストのエンドポイントに応じてログインビューを設定
        if request.endpoint and 'teacher' in request.endpoint:
            login_manager.login_view = 'teacher.login'
            session['user_type'] = 'teacher'
        elif request.endpoint and 'student' in request.endpoint:
            login_manager.login_view = 'student.login'
            session['user_type'] = 'student'

    # ビューのインポート
    from apps.teacher import views as teacher_views
    from apps.student import views as student_views

    app.register_blueprint(teacher_views.teacher, url_prefix="/teacher")
    app.register_blueprint(student_views.student, url_prefix="/student")

    return app