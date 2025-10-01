import webbrowser
from threading import Timer
from waitress import serve
from app import create_app


# Função para abrir o navegador após um pequeno atraso
def open_browser():
    """
    Abre o navegador padrão na URL da aplicação.
    """
    webbrowser.open_new("http://127.0.0.1:8000")


# Cria a aplicação usando a nossa fábrica de app/__init__.py
app = create_app()

if __name__ == "__main__":
    # Usa um temporizador para dar 1 segundo para o servidor iniciar
    # antes de tentar abrir o navegador.
    Timer(1, open_browser).start()

    # Inicia o servidor de produção 'waitress' na porta 8000.
    # Ele é mais estável e seguro que o servidor padrão do Flask.
    print("Iniciando o servidor em http://127.0.0.1:8000")
    print("O sistema será aberto no seu navegador em breve...")
    print("Para desligar o sistema, basta fechar esta janela do terminal.")
    serve(app, host="127.0.0.1", port=8000)

