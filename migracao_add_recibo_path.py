import sqlite3

print("Iniciando migração para adicionar campo de recibo...")

try:
    conexao = sqlite3.connect('luthier.db')
    cursor = conexao.cursor()

    # Comando para adicionar a nova coluna 'caminho_recibo'
    cursor.execute("ALTER TABLE ordens_servico ADD COLUMN caminho_recibo TEXT")

    conexao.commit()
    print("Coluna 'caminho_recibo' adicionada à tabela 'ordens_servico' com sucesso!")

except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("A coluna 'caminho_recibo' já existe. Nenhuma alteração necessária.")
    else:
        raise e
finally:
    if 'conexao' in locals() and conexao:
        conexao.close()
        print("Conexão com o banco de dados fechada.")