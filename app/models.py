# app/models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Criamos a instância do SQLAlchemy aqui, sem app, para evitar importações circulares.
db = SQLAlchemy()

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.String(50), nullable=False)
    user_message = db.Column(db.String(1000), nullable=False) # Aumentei o tamanho para mensagens mais longas
    bot_response = db.Column(db.String(1000), nullable=False) # Aumentei o tamanho para respostas mais longas
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Conversation {self.id}>'