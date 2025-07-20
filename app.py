import os
from dotenv import load_dotenv
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai
from datetime import datetime

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# --- Configuração Inicial ---
app = Flask(__name__)

# Configuração do Banco de Dados
db_url = os.environ.get("DATABASE_URL")
if db_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://", 1)
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conversations.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configuração da API do Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash') # Usando o modelo mais recente e rápido

# --- Modelo do Banco de Dados ---
class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.String(50), nullable=False)
    user_message = db.Column(db.String(500), nullable=False)
    bot_response = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Conversation {self.id}>'

# --- Funções Auxiliares ---
def get_gemini_response(prompt):
    """Função para obter a resposta do Gemini."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Erro ao chamar a API do Gemini: {e}")
        return "Desculpe, não consegui processar sua solicitação no momento."

# --- Rota Principal (Webhook) ---
@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    """Recebe mensagens do WhatsApp via Twilio."""
    # Extrai a mensagem do usuário e o número de telefone
    incoming_msg = request.values.get("Body", "").strip()
    sender_id = request.values.get("From", "")

    print(f"Mensagem de {sender_id}: {incoming_msg}")

    # Gera a resposta com o Gemini
    bot_reply_text = get_gemini_response(incoming_msg)

    # Armazena a conversa no banco de dados
    new_conversation = Conversation(
        sender_id=sender_id,
        user_message=incoming_msg,
        bot_response=bot_reply_text
    )
    db.session.add(new_conversation)
    db.session.commit()

    # Prepara e envia a resposta de volta para o WhatsApp
    resp = MessagingResponse()
    resp.message(bot_reply_text)

    return str(resp)

# Rota de teste para verificar se o servidor está no ar
@app.route("/")
def index():
    return "Servidor do Chatbot está no ar!"

# # --- Inicialização ---
# if __name__ == "__main__":
#     with app.app_context():
#         # Cria as tabelas do banco de dados se não existirem
#         db.create_all()
#     # Inicia o servidor Flask
#     app.run(debug=True, port=5000)