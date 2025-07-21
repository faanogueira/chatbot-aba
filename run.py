# run.py

from app import create_app

# Cria a aplicação usando nossa factory
app = create_app()

# Este bloco só será executado se você rodar "python run.py"
# Não é usado pelo Gunicorn no Render
if __name__ == "__main__":
    app.run(debug=True)