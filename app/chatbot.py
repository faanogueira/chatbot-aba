# app/chatbot.py

import os
import google.generativeai as genai

def setup_gemini():
    """Configura a API do Gemini com a chave do ambiente."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("API Key do Gemini não encontrada. Defina a variável de ambiente GEMINI_API_KEY.")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model

# Inicializa o modelo quando este módulo é carregado
gemini_model = setup_gemini()

def get_gemini_response(prompt):
    """Função para obter a resposta do Gemini."""
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Erro ao chamar a API do Gemini: {e}")
        return "Desculpe, não consegui processar sua solicitação no momento. Tente novamente."