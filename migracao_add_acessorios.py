import sqlite3

print("Iniciando migração do banco de dados...")

try:
    conexao = sqlite3.connect('luthier.db')
    cursor = conexao.cursor()

    # Comando para adicionar a nova coluna 'acessorios_entrada'
    cursor.execute("ALTER TABLE ordens_servico ADD COLUMN acessorios_entrada TEXT")

    conexao.commit()
    print("Coluna 'acessorios_entrada' adicionada à tabela 'ordens_servico' com sucesso!")

except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("A coluna 'acessorios_entrada' já existe. Nenhuma alteração necessária.")
    else:
        raise e
finally:
    if 'conexao' in locals() and conexao:
        conexao.close()
        print("Conexão com o banco de dados fechada.")