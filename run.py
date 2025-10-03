import webbrowser
from threading import Timer
import sys
import ctypes

from waitress import serve
from app import create_app

# --- Bloco de Instância Única (Mutex) ---
# Importações necessárias para o Mutex funcionar no Windows
try:
    from win32event import CreateMutex
    from win32api import GetLastError
    from winerror import ERROR_ALREADY_EXISTS
except ImportError:
    # Se não estiver no Windows, cria classes "falsas" para não dar erro.
    # Isso permite que o código ainda rode em outros sistemas para desenvolvimento.
    class SingleInstance:
        def __init__(self): pass

        def already_running(self): return False
else:
    class SingleInstance:
        """
        Classe para garantir que apenas uma instância da aplicação seja executada.
        Usa um Mutex do Windows.
        """

        def __init__(self):
            # Nome único e global para o nosso Mutex
            self.mutexname = "SistemaLuthier-Mutex-App-v1.0-9E7D8C4B"  # Adicionado um GUID para ser mais único
            self.mutex = CreateMutex(None, False, self.mutexname)
            self.lasterror = GetLastError()

        def already_running(self):
            """Retorna True se outra instância já estiver rodando, False caso contrário."""
            return self.lasterror == ERROR_ALREADY_EXISTS

        def __del__(self):
            """Garante que o Mutex seja liberado ao fechar o programa."""
            if self.mutex:
                try:
                    self.mutex.close()
                except Exception:
                    pass


# --- Fim do Bloco de Instância Única ---


def main():
    """
    Função principal que inicia o servidor e a aplicação.
    Só é chamada se for a primeira instância do programa.
    """

    # Função para abrir o navegador após um pequeno atraso
    def open_browser():
        print("Abrindo a interface no navegador padrão...")
        webbrowser.open_new("http://127.0.0.1:8000")

    # Cria a aplicação usando a fábrica em app/__init__.py
    app = create_app()

    # Usa um temporizador para dar 1 segundo para o servidor iniciar
    # antes de tentar abrir o navegador.
    Timer(1, open_browser).start()

    print("Iniciando o servidor em http://127.0.0.1:8000")
    print("O sistema será aberto no seu navegador em breve...")
    print("Para desligar o sistema, use o botão 'Desligar Servidor' na interface do programa.")
    serve(app, host="127.0.0.1", port=8000)


# --- Bloco Principal de Execução ---
# Este é o ponto de entrada quando o SistemaLuthier.exe é executado.
if __name__ == "__main__":

    # Cria o verificador de instância única
    instance_checker = SingleInstance()

    if instance_checker.already_running():
        # Se o programa JÁ ESTÁ RODANDO:
        # 1. Avisa no console (se houver um).
        print("Aplicação já está em execução. Abrindo uma nova aba no navegador.")
        # 2. Abre uma nova aba no navegador apontando para o servidor ativo.
        webbrowser.open_new("http://127.0.0.1:8000")
        # 3. Encerra esta segunda instância imediatamente.
        sys.exit(0)

    # Se o programa NÃO ESTÁ RODANDO:
    # 1. Chama a função principal para iniciar o servidor.
    main()