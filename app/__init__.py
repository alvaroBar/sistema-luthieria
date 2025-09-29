import os
from flask import Flask


def create_app():
    """
    Cria e configura uma instância da aplicação Flask.
    Este é o padrão Application Factory.
    """
    # O Flask agora procura as pastas 'static' e 'templates' a partir daqui (de dentro da pasta 'app')
    app = Flask(__name__, instance_relative_config=True)

    # Carrega as configurações do config.py que está na pasta raiz do projeto
    # Acessa a pasta pai (../) a partir da localização deste arquivo (__file__)
    app.config.from_pyfile(os.path.join(os.path.dirname(__file__), '..', 'config.py'))

    # Define uma chave secreta, necessária para algumas funcionalidades do Flask
    app.config['SECRET_KEY'] = 'sua-chave-secreta-super-dificil-de-adivinhar'

    # Define o caminho absoluto para a pasta de recibos, que está na raiz do projeto
    RECIBOS_FOLDER = os.path.join(app.root_path, '..', 'recibos')
    app.config['RECIBOS_FOLDER'] = RECIBOS_FOLDER

    # Garante que a pasta de recibos exista; se não, cria a pasta
    if not os.path.exists(app.config['RECIBOS_FOLDER']):
        os.makedirs(app.config['RECIBOS_FOLDER'])

    # Com a aplicação já criada e configurada, importa e registra o blueprint de rotas
    from . import routes
    app.register_blueprint(routes.main_routes)

    # Retorna a aplicação pronta para ser executada pelo run.py
    return app

