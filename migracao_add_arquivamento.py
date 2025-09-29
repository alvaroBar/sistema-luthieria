import sqlite3

print("Iniciando migração para adicionar campo de arquivamento...")

try:
    # O arquivo db.py não é utilizável aqui, então conectamos diretamente
    # Garanta que este script esteja na pasta raiz do projeto
    conexao = sqlite3.connect('luthier.db')
    cursor = conexao.cursor()

    # Adiciona a coluna 'arquivada' à tabela de ordens de serviço.
    # INTEGER funciona como booleano no SQLite (0=falso, 1=verdadeiro).
    # O padrão 0 garante que todas as OS existentes não sejam arquivadas.
    cursor.execute("ALTER TABLE ordens_servico ADD COLUMN arquivada INTEGER DEFAULT 0 NOT NULL")

    conexao.commit()
    print("Coluna 'arquivada' adicionada à tabela 'ordens_servico' com sucesso!")

except sqlite3.OperationalError as e:
    # Este erro é esperado se você rodar o script mais de uma vez.
    if "duplicate column name" in str(e):
        print("A coluna 'arquivada' já existe. Nenhuma alteração necessária.")
    else:
        raise e
finally:
    if 'conexao' in locals() and conexao:
        conexao.close()
        print("Conexão com o banco de dados fechada.")
