import sqlite3
import os

# Importa a variável do caminho de AppData que definimos no __init__.py
from app import APP_DATA_PATH

def get_db_connection():
    """Cria uma conexão com o banco de dados localizado na pasta AppData."""
    db_path = os.path.join(APP_DATA_PATH, 'luthier.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# --- FUNÇÕES DE CLIENTES ---

def get_todos_clientes(termo_busca=None):
    """Busca todos os clientes ou filtra por nome/CPF."""
    conn = get_db_connection()
    if termo_busca:
        query = 'SELECT * FROM clientes WHERE nome LIKE ? OR cpf LIKE ? ORDER BY nome'
        clientes = conn.execute(query, (f'%{termo_busca}%', f'%{termo_busca}%')).fetchall()
    else:
        query = 'SELECT * FROM clientes ORDER BY nome'
        clientes = conn.execute(query).fetchall()
    conn.close()
    return clientes

def get_cliente_por_id(cliente_id):
    """Busca um único cliente pelo seu ID."""
    conn = get_db_connection()
    cliente = conn.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,)).fetchone()
    conn.close()
    return cliente

# --- FUNÇÕES DE SERVIÇOS (CATÁLOGO) ---

def get_todos_servicos():
    """Busca todos os serviços do catálogo."""
    conn = get_db_connection()
    servicos = conn.execute('SELECT * FROM servicos ORDER BY nome').fetchall()
    conn.close()
    return servicos

def get_servico_por_id(servico_id):
    """Busca um único serviço do catálogo pelo seu ID."""
    conn = get_db_connection()
    servico = conn.execute('SELECT * FROM servicos WHERE id = ?', (servico_id,)).fetchone()
    conn.close()
    return servico

# --- FUNÇÕES DE ORDEM DE SERVIÇO (OS) ---

def get_todas_os_com_detalhes():
    """Busca todas as OS com informações do cliente e equipamento para o dashboard."""
    conn = get_db_connection()
    query = """
        SELECT os.*, 
               eq.tipo as tipo_equipamento, 
               eq.marca as marca_equipamento, 
               cl.nome as nome_cliente
        FROM ordens_servico as os
        JOIN equipamentos as eq ON os.equipamento_id = eq.id
        JOIN clientes as cl ON eq.cliente_id = cl.id
        ORDER BY os.id DESC
    """
    ordens_servico = conn.execute(query).fetchall()
    conn.close()
    return ordens_servico

def get_os_completa_por_id(os_id):
    """Busca todos os dados de uma OS específica, incluindo cliente e equipamento."""
    conn = get_db_connection()
    query = """
        SELECT os.*, eq.tipo as tipo_equipamento, eq.marca as marca_equipamento, 
               cl.nome as nome_cliente, cl.id as cliente_id, cl.cpf, cl.celular_whatsapp,
               eq.id as equipamento_id, eq.modelo, eq.numero_serie
        FROM ordens_servico as os
        JOIN equipamentos as eq ON os.equipamento_id = eq.id
        JOIN clientes as cl ON eq.cliente_id = cl.id
        WHERE os.id = ?
    """
    os_data = conn.execute(query, (os_id,)).fetchone()
    conn.close()
    return os_data

# --- FUNÇÕES DE ORÇAMENTO E PAGAMENTOS ---

def get_itens_orcamento_por_os(os_id):
    """Busca todos os serviços do orçamento de uma OS."""
    conn = get_db_connection()
    itens = conn.execute('SELECT * FROM orcamento_itens WHERE ordem_servico_id = ?', (os_id,)).fetchall()
    conn.close()
    return itens

def get_produtos_orcamento_por_os(os_id):
    """Busca todos os produtos do orçamento de uma OS."""
    conn = get_db_connection()
    query = """
        SELECT op.id, op.quantidade_usada, op.valor_cobrado_unidade, ei.nome 
        FROM orcamento_produtos as op
        JOIN estoque_itens as ei ON op.estoque_item_id = ei.id
        WHERE op.ordem_servico_id = ?
    """
    produtos = conn.execute(query, (os_id,)).fetchall()
    conn.close()
    return produtos

def get_pagamentos_por_os(os_id):
    """Busca todos os pagamentos de uma OS específica."""
    conn = get_db_connection()
    pagamentos = conn.execute('SELECT * FROM pagamentos WHERE ordem_servico_id = ? ORDER BY data_pagamento DESC', (os_id,)).fetchall()
    conn.close()
    return pagamentos

# --- FUNÇÕES DE ESTOQUE ---

def get_todos_itens_estoque():
    """Busca todos os itens do catálogo de estoque."""
    conn = get_db_connection()
    itens = conn.execute('SELECT * FROM estoque_itens ORDER BY nome').fetchall()
    conn.close()
    return itens

def get_item_estoque_por_id(item_id):
    """Busca um único item do estoque pelo seu ID."""
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM estoque_itens WHERE id = ?', (item_id,)).fetchone()
    conn.close()
    return item

def get_estoque_disponivel():
    """Busca apenas os itens de estoque com quantidade maior que zero."""
    conn = get_db_connection()
    itens = conn.execute('SELECT * FROM estoque_itens WHERE quantidade > 0 ORDER BY nome').fetchall()
    conn.close()
    return itens

