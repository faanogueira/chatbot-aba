# app/models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# NOVA TABELA PARA ARMAZENAR O ESTADO DE CADA USUÁRIO
class User(db.Model):
    id = db.Column(db.String(50), primary_key=True)  # Usaremos o sender_id do WhatsApp como ID
    state = db.Column(db.String(50), default='initial') # Estado atual do usuário
    
    # Relacionamento com as conversas
    conversations = db.relationship('Conversation', backref='user', lazy=True)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Chave estrangeira para ligar a conversa ao usuário
    user_id = db.Column(db.String(50), db.ForeignKey('user.id'), nullable=False)
    
    # Vamos manter as colunas de mensagem para ter um log completo
    user_message = db.Column(db.String(1000), nullable=False)
    bot_response = db.Column(db.String(1000), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Conversation {self.id}>'