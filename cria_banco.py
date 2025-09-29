import sqlite3

# Conecta ao banco de dados (se não existir, ele será criado)
conexao = sqlite3.connect('luthier.db')
cursor = conexao.cursor()
print("Conectado ao banco de dados.")

# Tabela de Clientes
cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cpf TEXT NOT NULL,
        nome TEXT NOT NULL,
        celular_whatsapp TEXT NOT NULL,
        telefone_recado TEXT,
        email TEXT
    )
''')
print("Tabela 'clientes' criada ou já existente.")

# Tabela de Equipamentos
cursor.execute('''
    CREATE TABLE IF NOT EXISTS equipamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        tipo TEXT NOT NULL,
        marca TEXT NOT NULL,
        modelo TEXT,
        numero_serie TEXT,
        FOREIGN KEY (cliente_id) REFERENCES clientes (id)
    )
''')
print("Tabela 'equipamentos' criada ou já existente.")

# Tabela de Ordens de Serviço
cursor.execute('''
    CREATE TABLE IF NOT EXISTS ordens_servico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipamento_id INTEGER NOT NULL,
        data_entrada TEXT NOT NULL,
        data_previsao_saida TEXT,
        descricao_problema TEXT NOT NULL,
        status TEXT NOT NULL
    )
''')
print("Tabela 'ordens_servico' criada ou já existente.")

conexao.commit()
conexao.close()
print("\nBanco de dados base configurado com sucesso!")