from app import create_app

# Cria a aplicação usando a nossa nova fábrica
app = create_app()

# Bloco para rodar o servidor de desenvolvimento
if __name__ == "__main__":
    app.run(debug=True)