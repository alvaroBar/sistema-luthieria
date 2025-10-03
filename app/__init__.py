# app/__init__.py

import os
import sys
import shutil
from datetime import timedelta  # <-- Importação necessária
from flask import Flask, session  # <-- 'session' adicionado aqui
from flask_login import LoginManager

# Variável global para o caminho dos dados do aplicativo
APP_DATA_PATH = ''


def create_app():
    """
    Cria e configura uma instância da aplicação Flask.
    Este é o padrão Application Factory.
    """
    global APP_DATA_PATH

    app = Flask(__name__, instance_relative_config=True)

    # --- LÓGICA DE CAMINHOS PARA PROGRAM FILES E APPDATA ---
    if getattr(sys, 'frozen', False):
        program_base_dir = os.path.dirname(sys.executable)
        app_data_root = os.environ.get('LOCALAPPDATA')
        APP_DATA_PATH = os.path.join(app_data_root, 'SistemaLuthier')
    else:
        program_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        APP_DATA_PATH = program_base_dir

    if not os.path.exists(APP_DATA_PATH):
        os.makedirs(APP_DATA_PATH)

    db_source_path = os.path.join(program_base_dir, 'luthier.db')
    db_dest_path = os.path.join(APP_DATA_PATH, 'luthier.db')

    if not os.path.exists(db_dest_path):
        shutil.copy2(db_source_path, db_dest_path)

    config_path = os.path.join(program_base_dir, 'config.py')
    app.config.from_pyfile(config_path)

    app.config['SECRET_KEY'] = 'sua-chave-secreta-super-dificil-de-adivinhar'

    # --- NOVO: CONFIGURAÇÃO DE TIMEOUT DA SESSÃO ---
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)

    @app.before_request
    def make_session_permanent():
        session.permanent = True

    # --- FIM DA CONFIGURAÇÃO DE TIMEOUT ---

    RECIBOS_FOLDER = os.path.join(APP_DATA_PATH, 'recibos')
    app.config['RECIBOS_FOLDER'] = RECIBOS_FOLDER

    if not os.path.exists(app.config['RECIBOS_FOLDER']):
        os.makedirs(app.config['RECIBOS_FOLDER'])

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .models import User
    import db

    @login_manager.user_loader
    def load_user(user_id):
        conn = db.get_db_connection()
        user_data = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        if user_data:
            return User(id=user_data['id'], username=user_data['username'], role=user_data['role'])
        return None

    from . import routes
    app.register_blueprint(routes.main_routes)
    from . import auth
    app.register_blueprint(auth.auth_bp)

    return app