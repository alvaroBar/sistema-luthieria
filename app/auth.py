from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
import db
from .models import User # Importa a classe User do models.py que está na mesma pasta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Se o usuário já estiver logado, redireciona para o dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = db.get_db_connection()
        user_data = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        # Verifica se o usuário existe e se a senha está correta
        if not user_data or not check_password_hash(user_data['password'], password):
            flash('Usuário ou senha inválida. Por favor, tente novamente.')
            return redirect(url_for('auth.login'))

        # Cria o objeto User e faz o login
        user = User(id=user_data['id'], username=user_data['username'], role=user_data['role'])
        login_user(user, remember=True) # 'remember=True' mantém o usuário logado
        return redirect(url_for('main.index'))

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

