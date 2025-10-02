import os
from flask import Flask
from flask_login import LoginManager


def create_app():
    """
    Cria e configura uma instância da aplicação Flask.
    Este é o padrão Application Factory.
    """
    app = Flask(__name__, instance_relative_config=True)

    # Carrega as configurações do config.py que está na pasta raiz
    app.config.from_pyfile(os.path.join(os.path.dirname(__file__), '..', 'config.py'))
    app.config['SECRET_KEY'] = 'sua-chave-secreta-super-dificil-de-adivinhar'

    # Define o caminho absoluto para a pasta de recibos
    RECIBOS_FOLDER = os.path.join(app.root_path, '..', 'recibos')
    app.config['RECIBOS_FOLDER'] = RECIBOS_FOLDER

    # Garante que a pasta de recibos exista
    if not os.path.exists(app.config['RECIBOS_FOLDER']):
        os.makedirs(app.config['RECIBOS_FOLDER'])

    # --- INICIALIZAÇÃO DO SISTEMA DE LOGIN ---
    login_manager = LoginManager()
    login_manager.init_app(app)
    # Define a rota para onde usuários não logados são redirecionados
    login_manager.login_view = 'auth.login'

    # CORREÇÃO AQUI: Importa a classe User de .models (que está dentro da pasta 'app')
    from .models import User
    import db

    # Define como o Flask-Login deve carregar um usuário a partir do ID
    @login_manager.user_loader
    def load_user(user_id):
        conn = db.get_db_connection()
        user_data = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        if user_data:
            return User(id=user_data['id'], username=user_data['username'], role=user_data['role'])
        return None

    # --- FIM DA INICIALIZAÇÃO DO LOGIN ---

    # Com a aplicação já criada e configurada, importa e registra os blueprints
    from . import routes
    app.register_blueprint(routes.main_routes)

    # CORREÇÃO AQUI: Importa o blueprint de .auth (que está dentro da pasta 'app')
    from . import auth
    app.register_blueprint(auth.auth_bp)

    # Retorna a aplicação pronta para ser executada pelo run.py
    return app

