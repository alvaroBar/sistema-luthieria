import os
from flask import Flask

# Importa o Blueprint que criamos no arquivo de rotas
from app.routes import main_routes

# Cria a instância da aplicação Flask
app = Flask(__name__)

# Carrega as configurações do arquivo config.py
app.config.from_object('config')
app.config['SECRET_KEY'] = 'sua-chave-secreta-super-dificil-de-adivinhar'

# Define o caminho absoluto para a pasta de recibos
RECIBOS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'recibos')
app.config['RECIBOS_FOLDER'] = RECIBOS_FOLDER

# Registra o nosso conjunto de rotas na aplicação
app.register_blueprint(main_routes)

# Bloco para rodar o servidor
if __name__ == '__main__':
    app.run(debug=True)
