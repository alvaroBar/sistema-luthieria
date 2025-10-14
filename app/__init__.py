# app/__init__.py

import os
import sys
import shutil
from datetime import timedelta, datetime
from flask import Flask, session, render_template
from flask_login import LoginManager


# --- FUNÇÃO DO FILTRO DE DATA ---
def format_date_br(value, format='%d/%m/%Y'):
    """Formata uma string de data YYYY-MM-DD para DD/MM/YYYY."""
    try:
        return datetime.strptime(value, '%Y-%m-%d').strftime(format)
    except (ValueError, TypeError):
        return value


def create_app():
    """
    Cria e configura uma instância da aplicação Flask.
    """
    app = Flask(__name__, instance_relative_config=True)

    # Garante que a pasta 'instance' exista para uploads
    try:
        if not os.path.exists(app.instance_path):
            os.makedirs(app.instance_path)
    except OSError:
        pass

    # Adiciona o filtro de data ao ambiente Jinja
    app.jinja_env.filters['datebr'] = format_date_br

    # --- LÓGICA DE CAMINHOS CORRIGIDA ---
    if getattr(sys, 'frozen', False):
        # MODO PRODUÇÃO (APP COMPILADO)
        # Usa a pasta %LOCALAPPDATA% para os dados
        program_base_dir = os.path.dirname(sys.executable)
        app_data_path = os.path.join(os.environ.get('LOCALAPPDATA'), 'SistemaLuthier')

        if not os.path.exists(app_data_path):
            os.makedirs(app_data_path)

        # Define o caminho do banco de dados de destino
        db_path = os.path.join(app_data_path, 'luthier.db')

        # Se o banco de dados não existir no destino, copia o original da instalação
        db_source_path = os.path.join(program_base_dir, 'luthier.db')
        if not os.path.exists(db_path):
            shutil.copy2(db_source_path, db_path)
    else:
        # MODO DESENVOLVIMENTO
        # Usa o banco de dados diretamente da pasta do projeto
        program_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        app_data_path = program_base_dir  # A pasta de dados é a própria pasta do projeto
        db_path = os.path.join(program_base_dir, 'luthier.db')

    # Salva o caminho do banco de dados ATIVO na configuração do app
    app.config['DATABASE_PATH'] = db_path

    # Carrega as configurações do arquivo config.py
    config_path = os.path.join(program_base_dir, 'config.py')
    app.config.from_pyfile(config_path)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'sua-chave-secreta-super-dificil-de-adivinhar'

    # ... (o resto da sua função create_app continua igual a partir daqui) ...
    # Configuração de timeout da sessão, recibos, LoginManager, etc.

    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)

    @app.before_request
    def make_session_permanent():
        session.permanent = True

    recibos_folder = os.path.join(app_data_path, 'recibos')
    app.config['RECIBOS_FOLDER'] = recibos_folder
    if not os.path.exists(app.config['RECIBOS_FOLDER']):
        os.makedirs(app.config['RECIBOS_FOLDER'])

    # --- ADICIONE O BLOCO ABAIXO ---
    # Configuração da pasta de uploads para fotos dos equipamentos
    uploads_folder = os.path.join(app_data_path, 'uploads', 'equipamentos')
    app.config['UPLOADS_FOLDER'] = uploads_folder
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
    if not os.path.exists(app.config['UPLOADS_FOLDER']):
        os.makedirs(app.config['UPLOADS_FOLDER'])
    # --- FIM DO NOVO BLOCO ---

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    import db
    db.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        conn = db.get_db()
        user_data = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if user_data:
            return User(id=user_data['id'], username=user_data['username'], role=user_data['role'])
        return None

    from . import routes
    app.register_blueprint(routes.main_routes)
    from . import auth
    app.register_blueprint(auth.auth_bp)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app