import sqlite3
from datetime import date

print("Iniciando migração para adicionar tabela de pagamentos...")

try:
    conexao = sqlite3.connect('luthier.db')
    cursor = conexao.cursor()

    # Tabela para registrar os pagamentos de cada OS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ordem_servico_id INTEGER NOT NULL,
            data_pagamento TEXT NOT NULL,
            valor_pago REAL NOT NULL,
            forma_pagamento TEXT NOT NULL,
            FOREIGN KEY (ordem_servico_id) REFERENCES ordens_servico (id)
        )
    ''')
    print("Tabela 'pagamentos' criada ou já existente.")

    conexao.commit()
    print("Migração dos pagamentos concluída com sucesso!")

except Exception as e:
    print(f"Ocorreu um erro durante a migração: {e}")
finally:
    if 'conexao' in locals() and conexao:
        conexao.close()
        print("Conexão com o banco de dados fechada.")