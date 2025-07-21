# app/routes.py

from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse
from .models import db, Conversation
from .chatbot import get_gemini_response

# Um Blueprint é uma forma de organizar um grupo de rotas relacionadas.
main_bp = Blueprint('main', __name__)

@main_bp.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    """Recebe mensagens do WhatsApp via Twilio."""
    incoming_msg = request.values.get("Body", "").strip()
    sender_id = request.values.get("From", "")

    print(f"Mensagem de {sender_id}: {incoming_msg}")

    # Gera a resposta com o Gemini
    bot_reply_text = get_gemini_response(incoming_msg)

    # Armazena a conversa no banco de dados
    try:
        new_conversation = Conversation(
            sender_id=sender_id,
            user_message=incoming_msg,
            bot_response=bot_reply_text
        )
        db.session.add(new_conversation)
        db.session.commit()
    except Exception as e:
        print(f"Erro ao salvar no banco de dados: {e}")
        db.session.rollback() # Desfaz a transação em caso de erro

    # Prepara e envia a resposta de volta para o WhatsApp
    resp = MessagingResponse()
    resp.message(bot_reply_text)

    return str(resp)

@main_bp.route("/")
def index():
    return "Servidor do Chatbot Refatorado está no ar!"