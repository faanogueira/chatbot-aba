# app/chatbot.py (VERSÃO MODIFICADA)

import os
import google.generativeai as genai
import chromadb

def setup_gemini():
    # ... (esta função continua igual)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("API Key do Gemini não encontrada.")
    genai.configure(api_key=api_key)
    generation_model = genai.GenerativeModel('gemini-1.5-flash')
    embedding_model = "models/embedding-001"
    return generation_model, embedding_model

def setup_chroma():
    """Configura e retorna a coleção do ChromaDB."""
    client = chromadb.Client()
    collection = client.get_collection(name="chatbot_docs")
    return collection

# Inicializa os modelos e o DB quando o módulo é carregado
generation_model, embedding_model = setup_gemini()
chroma_collection = setup_chroma()

def get_main_menu():
    return """Olá! 👋 Como posso te ajudar hoje?

Digite o número da opção desejada:

*1.* ⛪ Igrejas
*2.* 🎉 Eventos
*3.* 📢 Avisos
*4.* 📝 Cadastro
*5.* 🤖 Outros (Falar com a IA)
"""

def handle_menu_choice(choice):
    if choice == '1':
        # Aqui você pode buscar informações de igrejas do BD ou retornar um texto fixo
        return "Nossas igrejas são: Paróquia A, Capela B, Santuário C. Deseja mais detalhes sobre alguma delas?"
    elif choice == '2':
        return "Os próximos eventos são: Festa do Padroeiro (25/07), Chá Beneficente (10/08). Visite nosso site para mais informações."
    elif choice == '3':
        return "Avisos da semana: A secretaria paroquial estará fechada na sexta-feira. A missa de sábado será às 18h."
    elif choice == '4':
        return "Para realizar seu cadastro, por favor, acesse nosso site: [link do seu site de cadastro aqui]"
    else:
        return "Opção inválida. Por favor, escolha um número de 1 a 5."

def get_gemini_response(prompt):
    """
    Função modificada para usar RAG. Busca no ChromaDB e gera resposta com contexto.
    """
    try:
        # 1. Buscar por chunks relevantes no ChromaDB
        response = genai.embed_content(model=embedding_model, content=prompt)
        query_embedding = response['embedding']
        
        results = chroma_collection.query(
            query_embeddings=[query_embedding],
            n_results=3  # Pega os 3 chunks mais relevantes
        )
        
        retrieved_docs = results['documents'][0]
        context = "\n\n".join(retrieved_docs)

        # 2. Montar o prompt aumentado
        augmented_prompt = f"""
        Você é um assistente especialista. Use APENAS o contexto fornecido abaixo para responder à pergunta do usuário.
        Se a resposta não estiver no contexto, diga claramente: "Não encontrei essa informação nos meus documentos."

        Contexto:
        ---
        {context}
        ---

        Pergunta do Usuário:
        {prompt}

        Resposta:
        """

        # 3. Gerar a resposta final com o Gemini
        final_response = generation_model.generate_content(augmented_prompt)
        return final_response.text

    except Exception as e:
        print(f"Erro no processo de RAG: {e}")
        # Retorna uma resposta genérica se o RAG falhar
        return "Desculpe, tive um problema ao consultar meus documentos. Poderia tentar novamente?"