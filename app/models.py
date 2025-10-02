from flask_login import UserMixin

class User(UserMixin):
    """
    Classe que representa um usuário no sistema.
    Herda de UserMixin para obter as propriedades padrão do Flask-Login
    (is_authenticated, is_active, is_anonymous, get_id()).
    """
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role