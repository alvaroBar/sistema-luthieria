import sqlite3
import os
import base64
from datetime import date
from flask import (Blueprint, render_template, request, url_for, redirect,
                   make_response, current_app, send_from_directory)
from weasyprint import HTML
import db

main_routes = Blueprint('main', __name__)


# --- FUNÇÃO DE AJUDA PARA O RECIBO ---
def gerar_e_salvar_recibo(os_id):
    conn = db.get_db_connection()
    query = "SELECT os.*, eq.*, cl.* FROM ordens_servico as os JOIN equipamentos as eq ON os.equipamento_id = eq.id JOIN clientes as cl ON eq.cliente_id = cl.id WHERE os.id = ?"
    dados_os = conn.execute(query, (os_id,)).fetchone()
    if not dados_os:
        conn.close()
        return None
    luthier_info = {
        "nome": current_app.config['LUTHIER_NOME'], "documento": current_app.config['LUTHIER_DOCUMENTO'],
        "telefone": current_app.config['LUTHIER_TELEFONE'], "endereco": current_app.config['LUTHIER_ENDERECO']
    }
    path_logo = os.path.join(current_app.root_path, 'static', 'logo_fundo_transparente.png')
    try:
        with open(path_logo, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        logo_data_uri = f'data:image/png;base64,{encoded_string}'
    except FileNotFoundError:
        logo_data_uri = None
    html_renderizado = render_template('recibo_entrega_pdf.html', os=dados_os, cliente=dados_os, equipamento=dados_os,
                                       luthier=luthier_info, data_entrega=date.today().strftime('%d/%m/%Y'),
                                       logo_data_uri=logo_data_uri)
    pdf = HTML(string=html_renderizado).write_pdf()
    nome_arquivo = f"recibo_os_{os_id}.pdf"
    caminho_completo = os.path.join(current_app.config['RECIBOS_FOLDER'], nome_arquivo)
    with open(caminho_completo, 'wb') as f:
        f.write(pdf)
    conn.execute('UPDATE ordens_servico SET caminho_recibo = ? WHERE id = ?', (nome_arquivo, os_id))
    conn.commit()
    conn.close()
    return nome_arquivo


# --- ROTAS PRINCIPAIS E DASHBOARD (ATUALIZADAS) ---
@main_routes.route('/')
def index():
    conn = db.get_db_connection()
    # ALTERAÇÃO AQUI: A query agora filtra para mostrar apenas as OS não arquivadas (arquivada = 0)
    query = """
        SELECT os.*, eq.tipo as tipo_equipamento, eq.marca as marca_equipamento, cl.nome as nome_cliente
        FROM ordens_servico as os
        JOIN equipamentos as eq ON os.equipamento_id = eq.id
        JOIN clientes as cl ON eq.cliente_id = cl.id
        WHERE os.arquivada = 0
        ORDER BY os.id DESC
    """
    ordens_servico = conn.execute(query).fetchall()
    conn.close()
    return render_template('index.html', ordens_servico=ordens_servico)


# --- NOVAS ROTAS DE ARQUIVAMENTO ---
@main_routes.route('/os/<int:os_id>/arquivar', methods=['POST'])
def arquivar_os(os_id):
    """Marca uma Ordem de Serviço como arquivada, SE o status permitir."""
    conn = db.get_db_connection()

    # Busca a OS para verificar o status antes de arquivar
    os = conn.execute('SELECT status FROM ordens_servico WHERE id = ?', (os_id,)).fetchone()

    # Apenas arquiva se a OS for encontrada e o status for 'Entregue' ou 'Cancelado'
    if os and (os['status'] == 'Entregue' or os['status'] == 'Cancelado'):
        conn.execute('UPDATE ordens_servico SET arquivada = 1 WHERE id = ?', (os_id,))
        conn.commit()

    conn.close()
    return redirect(url_for('main.index'))


@main_routes.route('/arquivadas')
def listar_arquivadas():
    """Mostra a página com todas as Ordens de Serviço arquivadas."""
    conn = db.get_db_connection()
    query = """
        SELECT os.*, eq.tipo as tipo_equipamento, eq.marca as marca_equipamento, cl.nome as nome_cliente
        FROM ordens_servico as os
        JOIN equipamentos as eq ON os.equipamento_id = eq.id
        JOIN clientes as cl ON eq.cliente_id = cl.id
        WHERE os.arquivada = 1
        ORDER BY os.id DESC
    """
    ordens_arquivadas = conn.execute(query).fetchall()
    conn.close()
    return render_template('arquivadas.html', ordens_servico=ordens_arquivadas)


@main_routes.route('/os/<int:os_id>/desarquivar', methods=['POST'])
def desarquivar_os(os_id):
    """Marca uma Ordem de Serviço como não arquivada, trazendo-a de volta para o feed."""
    conn = db.get_db_connection()
    conn.execute('UPDATE ordens_servico SET arquivada = 0 WHERE id = ?', (os_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('main.listar_arquivadas'))


# --- ROTAS DE GERENCIAMENTO DO CATÁLOGO DE SERVIÇOS ---
@main_routes.route('/servicos')
def listar_servicos():
    conn = db.get_db_connection()
    servicos = conn.execute('SELECT * FROM servicos ORDER BY nome').fetchall()
    conn.close()
    return render_template('servicos.html', servicos=servicos)


@main_routes.route('/servicos/novo', methods=['GET', 'POST'])
def novo_servico():
    if request.method == 'POST':
        nome = request.form['nome']
        preco_sugerido = request.form['preco_sugerido']

        conn = db.get_db_connection()
        conn.execute('INSERT INTO servicos (nome, preco_sugerido) VALUES (?, ?)', (nome, preco_sugerido))
        conn.commit()
        conn.close()

        # Verifica se o formulário foi enviado a partir de uma OS
        source_os_id = request.form.get('source_os_id')
        if source_os_id:
            return redirect(url_for('main.detalhe_os', os_id=source_os_id, _anchor='orcamento'))

        return redirect(url_for('main.listar_servicos'))
    return render_template('novo_servico.html')


@main_routes.route('/servicos/<int:servico_id>/editar', methods=['GET', 'POST'])
def editar_servico(servico_id):
    conn = db.get_db_connection()
    servico = conn.execute('SELECT * FROM servicos WHERE id = ?', (servico_id,)).fetchone()
    if request.method == 'POST':
        conn.execute('UPDATE servicos SET nome = ?, preco_sugerido = ? WHERE id = ?',
                     (request.form['nome'], request.form['preco_sugerido'], servico_id))
        conn.commit()
        conn.close()
        return redirect(url_for('main.listar_servicos'))
    conn.close()
    return render_template('editar_servico.html', servico=servico)


@main_routes.route('/servicos/<int:servico_id>/excluir', methods=['POST'])
def excluir_servico(servico_id):
    conn = db.get_db_connection()
    conn.execute('DELETE FROM servicos WHERE id = ?', (servico_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('main.listar_servicos'))


# --- ROTAS DE CLIENTES (COM ATUALIZAÇÃO) ---
@main_routes.route('/clientes')
def listar_clientes():
    termo_busca = request.args.get('busca')
    # Captura o novo parâmetro 'source' da URL
    source = request.args.get('source')

    conn = db.get_db_connection()
    if termo_busca:
        clientes = conn.execute('SELECT * FROM clientes WHERE nome LIKE ? OR cpf LIKE ? ORDER BY nome',
                                (f'%{termo_busca}%', f'%{termo_busca}%')).fetchall()
    else:
        clientes = conn.execute('SELECT * FROM clientes ORDER BY nome').fetchall()
    conn.close()

    # Passa o novo parâmetro 'source' para o template
    return render_template('clientes.html', clientes=clientes, termo_busca=termo_busca, source=source)


@main_routes.route('/clientes/novo', methods=['GET', 'POST'])
def novo_cliente():
    if request.method == 'POST':
        conn = db.get_db_connection()
        conn.execute(
            'INSERT INTO clientes (nome, cpf, celular_whatsapp, telefone_recado, email) VALUES (?, ?, ?, ?, ?)',
            (request.form['nome'], request.form['cpf'], request.form['celular_whatsapp'],
             request.form['telefone_recado'], request.form['email']))
        conn.commit()
        conn.close()
        return redirect(url_for('main.listar_clientes'))
    return render_template('novo_cliente.html')


@main_routes.route('/clientes/<int:cliente_id>/editar', methods=['GET', 'POST'])
def editar_cliente(cliente_id):
    conn = db.get_db_connection()
    cliente = conn.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,)).fetchone()
    if request.method == 'POST':
        conn.execute(
            'UPDATE clientes SET nome = ?, cpf = ?, celular_whatsapp = ?, telefone_recado = ?, email = ? WHERE id = ?',
            (request.form['nome'], request.form['cpf'], request.form['celular_whatsapp'],
             request.form['telefone_recado'], request.form['email'], cliente_id))
        conn.commit()
        conn.close()
        return redirect(url_for('main.listar_clientes'))
    conn.close()
    return render_template('editar_cliente.html', cliente=cliente)


@main_routes.route('/clientes/<int:cliente_id>/excluir', methods=['POST'])
def excluir_cliente(cliente_id):
    conn = db.get_db_connection()
    try:
        conn.execute('DELETE FROM clientes WHERE id = ?', (cliente_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()
    return redirect(url_for('main.listar_clientes'))


# --- ROTAS DE EQUIPAMENTOS (ATUALIZADAS) ---
@main_routes.route('/cliente/<int:cliente_id>/equipamentos')
def listar_equipamentos(cliente_id):
    conn = db.get_db_connection()
    cliente = conn.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,)).fetchone()
    equipamentos = conn.execute('SELECT * FROM equipamentos WHERE cliente_id = ? ORDER BY tipo', (cliente_id,)).fetchall()
    conn.close()
    return render_template('equipamentos.html', cliente=cliente, equipamentos=equipamentos)


@main_routes.route('/cliente/<int:cliente_id>/equipamentos/novo', methods=['GET', 'POST'])
def novo_equipamento(cliente_id):
    conn = db.get_db_connection()
    cliente = conn.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,)).fetchone()
    conn.close()

    if request.method == 'POST':
        tipo = request.form['tipo']
        # Se o tipo for "Outro", usa o valor do campo de texto, se não for vazio
        if tipo == 'Outro':
            tipo_outro = request.form.get('tipo_outro', '').strip()
            if tipo_outro:
                tipo = tipo_outro

        marca = request.form['marca']
        modelo = request.form['modelo']
        numero_serie = request.form['numero_serie']

        conn = db.get_db_connection()
        conn.execute('INSERT INTO equipamentos (cliente_id, tipo, marca, modelo, numero_serie) VALUES (?, ?, ?, ?, ?)',
                     (cliente_id, tipo, marca, modelo, numero_serie))
        conn.commit()
        conn.close()
        return redirect(url_for('main.listar_equipamentos', cliente_id=cliente_id))

    return render_template('novo_equipamento.html', cliente=cliente)


@main_routes.route('/equipamento/<int:equipamento_id>/editar', methods=['GET', 'POST'])
def editar_equipamento(equipamento_id):
    conn = db.get_db_connection()
    # Pega os dados do equipamento e do cliente de uma vez só
    query = "SELECT eq.*, cl.nome as nome_cliente, cl.id as cliente_id FROM equipamentos as eq JOIN clientes as cl ON eq.cliente_id = cl.id WHERE eq.id = ?"
    equipamento = conn.execute(query, (equipamento_id,)).fetchone()
    conn.close()

    if request.method == 'POST':
        tipo = request.form['tipo']
        if tipo == 'Outro':
            tipo_outro = request.form.get('tipo_outro', '').strip()
            if tipo_outro:
                tipo = tipo_outro

        marca = request.form['marca']
        modelo = request.form['modelo']
        numero_serie = request.form['numero_serie']

        conn = db.get_db_connection()
        conn.execute('UPDATE equipamentos SET tipo = ?, marca = ?, modelo = ?, numero_serie = ? WHERE id = ?',
                     (tipo, marca, modelo, numero_serie, equipamento_id))
        conn.commit()
        conn.close()
        return redirect(url_for('main.listar_equipamentos', cliente_id=equipamento['cliente_id']))

    return render_template('editar_equipamento.html', equipamento=equipamento)


@main_routes.route('/equipamento/<int:equipamento_id>/excluir', methods=['POST'])
def excluir_equipamento(equipamento_id):
    conn = db.get_db_connection()
    # Primeiro, descobre a qual cliente o equipamento pertence para poder redirecionar de volta
    equipamento = conn.execute('SELECT cliente_id FROM equipamentos WHERE id = ?', (equipamento_id,)).fetchone()
    cliente_id = equipamento['cliente_id'] if equipamento else None

    try:
        # Tenta excluir. O DB irá barrar se houver OS associada.
        conn.execute('DELETE FROM equipamentos WHERE id = ?', (equipamento_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        # Falha silenciosamente para proteger os dados.
        # Em um sistema real, adicionaríamos uma flash message de erro.
        pass
    finally:
        conn.close()

    if cliente_id:
        return redirect(url_for('main.listar_equipamentos', cliente_id=cliente_id))
    return redirect(url_for('main.index'))  # Fallback


# --- ROTAS DE ORDEM DE SERVIÇO ---
@main_routes.route('/equipamento/<int:equipamento_id>/os/novo', methods=['GET', 'POST'])
def nova_os(equipamento_id):
    conn = db.get_db_connection()
    dados_completos = conn.execute(
        "SELECT eq.*, cl.nome as nome_cliente, cl.id as id_cliente FROM equipamentos as eq JOIN clientes as cl ON eq.cliente_id = cl.id WHERE eq.id = ?",
        (equipamento_id,)).fetchone()
    cliente = {'id': dados_completos['id_cliente'], 'nome': dados_completos['nome_cliente']}
    equipamento = dict(dados_completos)
    conn.close()

    if request.method == 'POST':
        data_entrada = date.today().strftime('%Y-%m-%d')
        data_previsao_saida = request.form['data_previsao_saida']
        descricao_problema = request.form['descricao_problema']
        status = "Aguardando Orçamento"

        # Lógica para combinar os acessórios
        acessorios_radio = request.form['acessorios_entrada']
        acessorios_obs = request.form.get('acessorios_obs', '').strip()

        acessorios_finais = acessorios_radio
        if acessorios_obs:
            acessorios_finais += f" (Obs: {acessorios_obs})"

        conn = db.get_db_connection()
        conn.execute(
            'INSERT INTO ordens_servico (equipamento_id, data_entrada, data_previsao_saida, descricao_problema, status, acessorios_entrada) VALUES (?, ?, ?, ?, ?, ?)',
            (equipamento_id, data_entrada, data_previsao_saida, descricao_problema, status, acessorios_finais))
        conn.commit()
        conn.close()
        return redirect(url_for('main.index'))

    return render_template('nova_os.html', cliente=cliente, equipamento=equipamento)


@main_routes.route('/os/<int:os_id>')
def detalhe_os(os_id):
    conn = db.get_db_connection()
    query_os = "SELECT os.*, eq.tipo as tipo_equipamento, eq.marca as marca_equipamento, cl.nome as nome_cliente FROM ordens_servico as os JOIN equipamentos as eq ON os.equipamento_id = eq.id JOIN clientes as cl ON eq.cliente_id = cl.id WHERE os.id = ? "
    os_data = conn.execute(query_os, (os_id,)).fetchone()
    itens_orcamento = conn.execute('SELECT * FROM orcamento_itens WHERE ordem_servico_id = ?', (os_id,)).fetchall()
    catalogo_servicos = conn.execute('SELECT * FROM servicos ORDER BY nome').fetchall()
    pagamentos = conn.execute('SELECT * FROM pagamentos WHERE ordem_servico_id = ? ORDER BY data_pagamento DESC',
                              (os_id,)).fetchall()
    produtos_orcamento = conn.execute(
        "SELECT op.id, op.quantidade_usada, op.valor_cobrado_unidade, ei.nome FROM orcamento_produtos as op JOIN estoque_itens as ei ON op.estoque_item_id = ei.id WHERE op.ordem_servico_id = ?",
        (os_id,)).fetchall()
    estoque_disponivel = conn.execute('SELECT * FROM estoque_itens WHERE quantidade > 0 ORDER BY nome').fetchall()
    conn.close()

    total_servicos = sum(item['valor_cobrado'] for item in itens_orcamento)
    total_produtos = sum(prod['valor_cobrado_unidade'] * prod['quantidade_usada'] for prod in produtos_orcamento)
    total_orcamento = total_servicos + total_produtos
    total_pago = sum(pg['valor_pago'] for pg in pagamentos)

    return render_template('detalhe_os.html',
                           os=os_data,
                           itens_orcamento=itens_orcamento,
                           produtos_orcamento=produtos_orcamento,
                           catalogo_servicos=catalogo_servicos,
                           estoque_disponivel=estoque_disponivel,
                           total_orcamento=total_orcamento,
                           pagamentos=pagamentos,
                           total_pago=total_pago)


# --- ROTAS DO ORÇAMENTO (ATUALIZADAS) ---

@main_routes.route('/os/<int:os_id>/add_servico', methods=['POST'])
def add_servico(os_id):
    conn = db.get_db_connection()
    servico_id = request.form['servico_id']
    valor_cobrado_str = request.form['valor_cobrado']
    servico_catalogo = conn.execute('SELECT * FROM servicos WHERE id = ?', (servico_id,)).fetchone()
    descricao = servico_catalogo['nome']
    valor = float(valor_cobrado_str) if valor_cobrado_str else servico_catalogo['preco_sugerido']
    conn.execute('INSERT INTO orcamento_itens (ordem_servico_id, servico_descricao, valor_cobrado) VALUES (?, ?, ?)', (os_id, descricao, valor))
    conn.commit()
    conn.close()
    # CORREÇÃO: Adiciona a âncora para manter a posição na página
    return redirect(url_for('main.detalhe_os', os_id=os_id, _anchor='orcamento'))


@main_routes.route('/orcamento/item/<int:item_id>/excluir', methods=['POST'])
def excluir_item_orcamento(item_id):
    conn = db.get_db_connection()
    item = conn.execute('SELECT ordem_servico_id FROM orcamento_itens WHERE id = ?', (item_id,)).fetchone()
    os_id = item['ordem_servico_id']
    conn.execute('DELETE FROM orcamento_itens WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    # CORREÇÃO: Adiciona a âncora
    return redirect(url_for('main.detalhe_os', os_id=os_id, _anchor='orcamento'))


@main_routes.route('/os/<int:os_id>/add_produto', methods=['POST'])
def add_produto_orcamento(os_id):
    estoque_item_id = request.form['estoque_item_id']
    quantidade_usada = int(request.form.get('quantidade_usada', 1))
    conn = db.get_db_connection()
    item_estoque = conn.execute('SELECT * FROM estoque_itens WHERE id = ?', (estoque_item_id,)).fetchone()
    if item_estoque and quantidade_usada > 0 and item_estoque['quantidade'] >= quantidade_usada:
        conn.execute('INSERT INTO orcamento_produtos (ordem_servico_id, estoque_item_id, quantidade_usada, valor_cobrado_unidade) VALUES (?, ?, ?, ?)',
                     (os_id, estoque_item_id, quantidade_usada, item_estoque['preco_venda']))
        nova_quantidade = item_estoque['quantidade'] - quantidade_usada
        conn.execute('UPDATE estoque_itens SET quantidade = ? WHERE id = ?', (nova_quantidade, estoque_item_id))
        conn.commit()
    conn.close()
    # CORREÇÃO: Adiciona a âncora
    return redirect(url_for('main.detalhe_os', os_id=os_id, _anchor='orcamento'))


@main_routes.route('/orcamento/produto/<int:item_id>/excluir', methods=['POST'])
def excluir_produto_orcamento(item_id):
    conn = db.get_db_connection()
    item_orcamento = conn.execute('SELECT * FROM orcamento_produtos WHERE id = ?', (item_id,)).fetchone()
    if item_orcamento:
        os_id = item_orcamento['ordem_servico_id']
        estoque_item_id = item_orcamento['estoque_item_id']
        quantidade_devolvida = item_orcamento['quantidade_usada']
        conn.execute('UPDATE estoque_itens SET quantidade = quantidade + ? WHERE id = ?', (quantidade_devolvida, estoque_item_id))
        conn.execute('DELETE FROM orcamento_produtos WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()
        # CORREÇÃO: Adiciona a âncora
        return redirect(url_for('main.detalhe_os', os_id=os_id, _anchor='orcamento'))
    conn.close()
    return redirect(url_for('main.index'))


@main_routes.route('/os/<int:os_id>/add_pagamento', methods=['POST'])
def add_pagamento(os_id):
    valor_pago = request.form['valor_pago']
    forma_pagamento = request.form['forma_pagamento']
    data_pagamento = date.today().strftime('%Y-%m-%d')
    conn = db.get_db_connection()
    conn.execute(
        'INSERT INTO pagamentos (ordem_servico_id, data_pagamento, valor_pago, forma_pagamento) VALUES (?, ?, ?, ?)',
        (os_id, data_pagamento, valor_pago, forma_pagamento))
    conn.commit()
    conn.close()
    return redirect(url_for('main.detalhe_os', os_id=os_id))


@main_routes.route('/os/<int:os_id>/pdf')
def gerar_os_pdf(os_id):
    conn = db.get_db_connection()
    query_os = "SELECT os.*, eq.id as equipamento_id, eq.tipo as tipo_equipamento, eq.marca as marca_equipamento, cl.id as cliente_id, cl.nome as nome_cliente FROM ordens_servico as os JOIN equipamentos as eq ON os.equipamento_id = eq.id JOIN clientes as cl ON eq.cliente_id = cl.id WHERE os.id = ? "
    os_data = conn.execute(query_os, (os_id,)).fetchone()
    cliente_info = conn.execute('SELECT * FROM clientes WHERE id = ?', (os_data['cliente_id'],)).fetchone()
    equipamento_info = conn.execute('SELECT * FROM equipamentos WHERE id = ?', (os_data['equipamento_id'],)).fetchone()
    itens_orcamento = conn.execute('SELECT * FROM orcamento_itens WHERE ordem_servico_id = ?', (os_id,)).fetchall()

    # Busca os produtos do orçamento (esta linha já existia, mas agora vamos usá-la)
    produtos_orcamento = conn.execute(
        "SELECT op.id, op.quantidade_usada, op.valor_cobrado_unidade, ei.nome FROM orcamento_produtos as op JOIN estoque_itens as ei ON op.estoque_item_id = ei.id WHERE op.ordem_servico_id = ?",
        (os_id,)).fetchall()
    conn.close()

    # Recalcula o total para garantir que está correto
    total_servicos = sum(item['valor_cobrado'] for item in itens_orcamento)
    total_produtos = sum(prod['valor_cobrado_unidade'] * prod['quantidade_usada'] for prod in produtos_orcamento)
    total_orcamento = total_servicos + total_produtos

    data_hoje = date.today().strftime('%d/%m/%Y')
    path_logo = os.path.join(current_app.root_path, 'static', 'logo_fundo_transparente.png')
    try:
        with open(path_logo, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        logo_data_uri = f'data:image/png;base64,{encoded_string}'
    except FileNotFoundError:
        logo_data_uri = None

    # CORREÇÃO AQUI: Adicionamos 'produtos_orcamento' para ser enviado ao template
    html_renderizado = render_template('os_pdf_template.html',
                                       os=os_data,
                                       cliente_info=cliente_info,
                                       equipamento_info=equipamento_info,
                                       itens_orcamento=itens_orcamento,
                                       produtos_orcamento=produtos_orcamento,  # <-- LINHA ADICIONADA
                                       total_orcamento=total_orcamento,
                                       data_hoje=data_hoje,
                                       logo_data_uri=logo_data_uri)

    pdf = HTML(string=html_renderizado).write_pdf()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=OS_{os_id}.pdf'
    return response


@main_routes.route('/os/<int:os_id>/atualizar_status', methods=['POST'])
def atualizar_status(os_id):
    novo_status = request.form['status']
    conn = db.get_db_connection()
    conn.execute('UPDATE ordens_servico SET status = ? WHERE id = ?', (novo_status, os_id))
    conn.commit()
    conn.close()
    if novo_status == 'Entregue':
        nome_arquivo = gerar_e_salvar_recibo(os_id)
        return redirect(url_for('main.detalhe_os', os_id=os_id, recibo_gerado=nome_arquivo))
    return redirect(url_for('main.detalhe_os', os_id=os_id))


@main_routes.route('/recibos/<path:filename>')
def servir_recibo(filename):
    return send_from_directory(current_app.config['RECIBOS_FOLDER'], filename, as_attachment=False)


@main_routes.route('/estoque')
def listar_estoque():
    conn = db.get_db_connection()
    itens = conn.execute('SELECT * FROM estoque_itens ORDER BY nome').fetchall()
    conn.close()
    return render_template('estoque.html', itens=itens)


@main_routes.route('/estoque/novo', methods=['GET', 'POST'])
def novo_item_estoque():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        quantidade = request.form['quantidade']
        preco_venda = request.form['preco_venda']

        conn = db.get_db_connection()
        conn.execute('INSERT INTO estoque_itens (nome, descricao, quantidade, preco_venda) VALUES (?, ?, ?, ?)',
                     (nome, descricao, quantidade, preco_venda))
        conn.commit()
        conn.close()

        # Verifica se o formulário foi enviado a partir de uma OS
        source_os_id = request.form.get('source_os_id')
        if source_os_id:
            return redirect(url_for('main.detalhe_os', os_id=source_os_id, _anchor='orcamento'))

        return redirect(url_for('main.listar_estoque'))
    return render_template('novo_item_estoque.html')


@main_routes.route('/estoque/<int:item_id>/editar', methods=['GET', 'POST'])
def editar_item_estoque(item_id):
    conn = db.get_db_connection()
    item = conn.execute('SELECT * FROM estoque_itens WHERE id = ?', (item_id,)).fetchone()
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        quantidade = request.form['quantidade']
        preco_venda = request.form['preco_venda']
        conn.execute('UPDATE estoque_itens SET nome = ?, descricao = ?, quantidade = ?, preco_venda = ? WHERE id = ?',
                     (nome, descricao, quantidade, preco_venda, item_id))
        conn.commit()
        conn.close()
        return redirect(url_for('main.listar_estoque'))
    conn.close()
    return render_template('editar_item_estoque.html', item=item)


@main_routes.route('/estoque/<int:item_id>/excluir', methods=['POST'])
def excluir_item_estoque(item_id):
    conn = db.get_db_connection()
    try:
        conn.execute('DELETE FROM estoque_itens WHERE id = ?', (item_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()
    return redirect(url_for('main.listar_estoque'))


# --- NOVA ROTA PARA ADICIONAR QUANTIDADE AO ESTOQUE ---
@main_routes.route('/estoque/<int:item_id>/add_quantidade', methods=['POST'])
def add_quantidade_estoque(item_id):
    """Adiciona uma quantidade especificada a um item do estoque."""
    if request.method == 'POST':
        try:
            # Garante que o valor é um número inteiro positivo
            quantidade_adicionada = int(request.form['quantidade_adicionada'])
            if quantidade_adicionada > 0:
                conn = db.get_db_connection()
                conn.execute('UPDATE estoque_itens SET quantidade = quantidade + ? WHERE id = ?',
                             (quantidade_adicionada, item_id))
                conn.commit()
                conn.close()
        except (ValueError, TypeError):
            # Ignora se o valor não for um número válido
            pass

    return redirect(url_for('main.listar_estoque'))


# --- NOVA ROTA PARA EDITAR INFORMAÇÕES DA OS ---
@main_routes.route('/os/<int:os_id>/editar_info', methods=['POST'])
def editar_info_os(os_id):
    """Atualiza as informações de acessórios e problema de uma OS."""
    if request.method == 'POST':
        acessorios = request.form['acessorios_entrada']
        problema = request.form['descricao_problema']

        conn = db.get_db_connection()
        conn.execute('UPDATE ordens_servico SET acessorios_entrada = ?, descricao_problema = ? WHERE id = ?',
                     (acessorios, problema, os_id))
        conn.commit()
        conn.close()

    return redirect(url_for('main.detalhe_os', os_id=os_id))

