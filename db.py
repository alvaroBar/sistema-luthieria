import sqlite3
from flask import current_app, g

def get_db():
    """
    Abre uma nova conexão com o banco de dados se não houver uma no contexto da requisição (g).
    Reutiliza a conexão existente se já houver uma.
    """
    if 'db' not in g:
        # Pega o caminho do banco de dados da configuração do app, que definimos no __init__.py
        db_path = current_app.config['DATABASE_PATH']
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """
    Fecha a conexão com o banco de dados, se ela existir no contexto da requisição.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    """
    Registra a função close_db para ser chamada automaticamente quando a requisição terminar.
    """
    app.teardown_appcontext(close_db)

# As funções abaixo permanecem quase iguais, mas agora usam get_db()
# e não fecham a conexão manualmente com conn.close()

def get_todos_clientes(termo_busca=None):
    conn = get_db()
    if termo_busca:
        query = 'SELECT * FROM clientes WHERE nome LIKE ? OR cpf LIKE ? ORDER BY nome'
        return conn.execute(query, (f'%{termo_busca}%', f'%{termo_busca}%')).fetchall()
    else:
        query = 'SELECT * FROM clientes ORDER BY nome'
        return conn.execute(query).fetchall()

def get_cliente_por_id(cliente_id):
    return get_db().execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,)).fetchone()

def get_todos_servicos():
    return get_db().execute('SELECT * FROM servicos ORDER BY nome').fetchall()

def get_servico_por_id(servico_id):
    return get_db().execute('SELECT * FROM servicos WHERE id = ?', (servico_id,)).fetchone()

def get_todas_os_com_detalhes():
    query = """
        SELECT os.*, eq.tipo as tipo_equipamento, eq.marca as marca_equipamento, cl.nome as nome_cliente
        FROM ordens_servico as os
        JOIN equipamentos as eq ON os.equipamento_id = eq.id
        JOIN clientes as cl ON eq.cliente_id = cl.id
        ORDER BY os.id DESC
    """
    return get_db().execute(query).fetchall()

def get_os_completa_por_id(os_id):
    query = """
        SELECT os.*, eq.tipo as tipo_equipamento, eq.marca as marca_equipamento, 
               cl.nome as nome_cliente, cl.id as cliente_id, cl.cpf, cl.celular_whatsapp,
               eq.id as equipamento_id, eq.modelo, eq.numero_serie
        FROM ordens_servico as os
        JOIN equipamentos as eq ON os.equipamento_id = eq.id
        JOIN clientes as cl ON eq.cliente_id = cl.id
        WHERE os.id = ?
    """
    return get_db().execute(query, (os_id,)).fetchone()

def get_itens_orcamento_por_os(os_id):
    return get_db().execute('SELECT * FROM orcamento_itens WHERE ordem_servico_id = ?', (os_id,)).fetchall()

def get_produtos_orcamento_por_os(os_id):
    query = """
        SELECT op.id, op.quantidade_usada, op.valor_cobrado_unidade, ei.nome 
        FROM orcamento_produtos as op
        JOIN estoque_itens as ei ON op.estoque_item_id = ei.id
        WHERE op.ordem_servico_id = ?
    """
    return get_db().execute(query, (os_id,)).fetchall()

def get_pagamentos_por_os(os_id):
    return get_db().execute('SELECT * FROM pagamentos WHERE ordem_servico_id = ? ORDER BY data_pagamento DESC', (os_id,)).fetchall()

def get_todos_itens_estoque():
    return get_db().execute('SELECT * FROM estoque_itens ORDER BY nome').fetchall()

def get_item_estoque_por_id(item_id):
    return get_db().execute('SELECT * FROM estoque_itens WHERE id = ?', (item_id,)).fetchone()

def get_estoque_disponivel():
    return get_db().execute('SELECT * FROM estoque_itens WHERE quantidade > 0 ORDER BY nome').fetchall()