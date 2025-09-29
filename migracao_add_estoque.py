import sqlite3

print("Iniciando migração para adicionar tabelas de Controle de Estoque...")

try:
    conexao = sqlite3.connect('luthier.db')
    cursor = conexao.cursor()

    # Tabela 1: O catálogo principal do inventário
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estoque_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            descricao TEXT,
            quantidade INTEGER NOT NULL DEFAULT 0,
            preco_venda REAL NOT NULL
        )
    ''')
    print("Tabela 'estoque_itens' criada ou já existente.")

    # Tabela 2: Tabela de ligação entre a OS e os produtos do estoque utilizados
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orcamento_produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ordem_servico_id INTEGER NOT NULL,
            estoque_item_id INTEGER NOT NULL,
            quantidade_usada INTEGER NOT NULL DEFAULT 1,
            valor_cobrado_unidade REAL NOT NULL,
            FOREIGN KEY (ordem_servico_id) REFERENCES ordens_servico (id),
            FOREIGN KEY (estoque_item_id) REFERENCES estoque_itens (id)
        )
    ''')
    print("Tabela 'orcamento_produtos' criada ou já existente.")

    conexao.commit()
    print("\nMigração do Controle de Estoque concluída com sucesso!")
    print("O banco de dados está pronto para as próximas funcionalidades.")

except Exception as e:
    print(f"Ocorreu um erro durante a migração: {e}")
finally:
    if 'conexao' in locals() and conexao:
        conexao.close()
        print("Conexão com o banco de dados fechada.")