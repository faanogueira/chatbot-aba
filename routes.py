# app/routes.py

from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse
from .models import db, User, Conversation
from .chatbot import get_gemini_response, get_main_menu, handle_menu_choice

main_bp = Blueprint('main', __name__)

@main_bp.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "").strip()
    sender_id = request.values.get("From", "")

    # 1. ENCONTRAR OU CRIAR O USUÁRIO
    user = User.query.get(sender_id)
    if not user:
        user = User(id=sender_id, state='initial')
        db.session.add(user)
        # Commit inicial para garantir que o usuário exista na sessão
        db.session.commit()

    bot_reply_text = ""

    # 2. LÓGICA DE ESTADO (STATE MACHINE)
    if user.state == 'awaiting_menu_choice':
        # Se o usuário escolheu a opção 5, vai para o Gemini
        if incoming_msg == '5':
            bot_reply_text = "Entendido. Você quer falar com a inteligência artificial. Qual é a sua pergunta?"
            user.state = 'talking_to_ai' # Novo estado para conversa livre
        else:
            # Processa a escolha do menu (1-4)
            bot_reply_text = handle_menu_choice(incoming_msg)
            # Após responder, retorna o usuário para o estado inicial
            user.state = 'initial' 
    
    elif user.state == 'talking_to_ai':
        # Se o usuário digitar 'menu' ou 'voltar', retorna ao menu principal
        if incoming_msg.lower() in ['menu', 'voltar', 'sair']:
             bot_reply_text = get_main_menu()
             user.state = 'awaiting_menu_choice'
        else:
            # Envia a mensagem para o Gemini (RAG que criamos)
            bot_reply_text = get_gemini_response(incoming_msg)
            # Mantém o estado, permitindo uma conversa contínua com a IA
            user.state = 'talking_to_ai' 

    # O estado 'initial' e qualquer outro estado não tratado mostrarão o menu
    else: # Isso pega o estado 'initial'
        bot_reply_text = get_main_menu()
        user.state = 'awaiting_menu_choice' # Atualiza o estado para esperar a resposta

    # 3. SALVAR E ENVIAR
    try:
        # Salva a conversa
        convo = Conversation(user_id=user.id, user_message=incoming_msg, bot_response=bot_reply_text)
        db.session.add(convo)
        # Salva as alterações de estado e a nova conversa
        db.session.commit()
    except Exception as e:
        print(f"Erro ao salvar no banco de dados: {e}")
        db.session.rollback()

    resp = MessagingResponse()
    resp.message(bot_reply_text)
    return str(resp)


@main_bp.route("/")
def index():
    return "Servidor do Chatbot Refatorado está no ar!"