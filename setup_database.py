# setup_database.py

import os
import fitz  # PyMuPDF
import chromadb
import google.generativeai as genai
from dotenv import load_dotenv

print("Iniciando o processo de indexação de documentos...")

# Carregar variáveis de ambiente
load_dotenv()

# Configurar a API do Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("API Key do Gemini não encontrada.")
genai.configure(api_key=api_key)

# 1. FUNÇÃO PARA EXTRAIR E DIVIDIR O TEXTO
def extract_and_chunk_pdfs(folder_path):
    print(f"Lendo PDFs da pasta: {folder_path}")
    text_chunks = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)
            try:
                with fitz.open(file_path) as doc:
                    full_text = ""
                    for page in doc:
                        full_text += page.get_text()
                    
                    # Dividindo o texto em pedaços de ~500 caracteres, respeitando parágrafos
                    # Esta é uma estratégia de chunking simples. Pode ser melhorada.
                    paragraphs = full_text.split('\n\n')
                    chunk = ""
                    for p in paragraphs:
                        if len(chunk) + len(p) + 2 > 500:
                            text_chunks.append(chunk)
                            chunk = ""
                        chunk += p + "\n\n"
                    if chunk:
                        text_chunks.append(chunk)
                print(f"  - Processado: {filename}")
            except Exception as e:
                print(f"  - Erro ao processar {filename}: {e}")
    return text_chunks

# 2. FUNÇÃO PARA CRIAR E POPULAR O BANCO DE DADOS DE VETORES
def create_vector_database(chunks):
    print("Configurando o banco de dados de vetores (ChromaDB)...")
    client = chromadb.PersistentClient(path="chroma")

    # Tenta obter a coleção. Se não existir, cria uma nova.
    collection_name = "chatbot_docs"
    if collection_name in [c.name for c in client.list_collections()]:
        print(f"Coleção '{collection_name}' já existe. Apagando para recriar.")
        client.delete_collection(name=collection_name)

    collection = client.create_collection(name=collection_name)
    print("Coleção criada. Iniciando a criação de embeddings...")

    # Gerar embeddings e adicionar ao ChromaDB
    # O modelo de embedding é diferente do modelo de geração de texto.
    embedding_model = "models/embedding-001"
    count = 0
    for i, chunk in enumerate(chunks):
        try:
            response = genai.embed_content(model=embedding_model, content=chunk)
            embedding = response['embedding']
            collection.add(
                ids=[f"chunk_{i}"],
                embeddings=[embedding],
                documents=[chunk]
            )
            count += 1
            if count % 10 == 0:
                print(f"  - {count}/{len(chunks)} chunks processados...")
        except Exception as e:
            print(f"  - Erro ao gerar embedding para o chunk {i}: {e}")

    print(f"Indexação concluída! {count} chunks adicionados à coleção '{collection_name}'.")

# --- EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    pdf_folder = "documentos"
    if not os.path.exists(pdf_folder):
        print(f"Erro: A pasta '{pdf_folder}' não foi encontrada. Crie-a e adicione seus PDFs.")
    else:
        text_chunks = extract_and_chunk_pdfs(pdf_folder)
        if text_chunks:
            create_vector_database(text_chunks)
        else:
            print("Nenhum texto foi extraído dos PDFs.")