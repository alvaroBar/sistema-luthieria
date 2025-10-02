import sqlite3
from werkzeug.security import generate_password_hash

print("Iniciando migração para adicionar tabela de usuários...")

try:
    conexao = sqlite3.connect('luthier.db')
    cursor = conexao.cursor()

    # Tabela para armazenar usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    ''')
    print("Tabela 'users' criada ou já existente.")

    # Verifica se o usuário 'admin' já existe
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if cursor.fetchone() is None:
        # Cria o usuário 'admin' com uma senha padrão 'admin'
        # Em um ambiente real, essa senha deve ser alterada ou definida de forma mais segura.
        senha_hash = generate_password_hash('admin')
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ('admin', senha_hash, 'admin'))
        print("Usuário 'admin' padrão criado com a senha 'admin'.")
    else:
        print("Usuário 'admin' já existe.")

    conexao.commit()
    print("\nMigração de usuários concluída com sucesso!")

except Exception as e:
    print(f"Ocorreu um erro durante a migração: {e}")
finally:
    if 'conexao' in locals() and conexao:
        conexao.close()
        print("Conexão com o banco de dados fechada.")
