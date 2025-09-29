import sqlite3

print("Iniciando migração para adicionar tabelas de orçamento...")

try:
    conexao = sqlite3.connect('luthier.db')
    cursor = conexao.cursor()

    # Tabela 1: Catálogo de Serviços
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            preco_sugerido REAL NOT NULL
        )
    ''')
    print("Tabela 'servicos' criada ou já existente.")

    # Tabela 2: Itens do Orçamento de cada OS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orcamento_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ordem_servico_id INTEGER NOT NULL,
            servico_descricao TEXT NOT NULL,
            valor_cobrado REAL NOT NULL,
            FOREIGN KEY (ordem_servico_id) REFERENCES ordens_servico (id)
        )
    ''')
    print("Tabela 'orcamento_itens' criada ou já existente.")

    # Inserindo alguns serviços padrão para começar (apenas se a tabela estiver vazia)
    cursor.execute("SELECT count(id) FROM servicos")
    if cursor.fetchone()[0] == 0:
        servicos_padrao = [
            ('Regulagem Simples', 150.00),
            ('Troca de Cordas', 50.00),
            ('Troca de Trastes (Completa)', 800.00),
            ('Revisão Elétrica', 120.00),
            ('Colagem de Headstock', 450.00)
        ]
        cursor.executemany('INSERT INTO servicos (nome, preco_sugerido) VALUES (?, ?)', servicos_padrao)
        print(f"{len(servicos_padrao)} serviços padrão inseridos no catálogo.")

    conexao.commit()
    print("Migração do orçamento concluída com sucesso!")

except Exception as e:
    print(f"Ocorreu um erro durante a migração: {e}")
finally:
    if 'conexao' in locals() and conexao:
        conexao.close()
        print("Conexão com o banco de dados fechada.")