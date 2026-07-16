import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import streamlit as st
from dotenv import load_dotenv

# =====================================================================
# 1. CONFIGURACIÓN DE PÁGINA (Debe ir al inicio)
# =====================================================================
st.set_page_config(
    page_title="arXiv RAG Explorer",
    page_icon="🔬",
    layout="centered"
)

# Cargar variables de entorno locales (.env)
load_dotenv()

# Renderizado rápido del título para evitar pantallas en negro
st.title("🔬 arXiv Semantic Search & RAG")
st.markdown(
    "Bienvenido al buscador semántico de papers científicos. Este sistema recupera "
    "artículos relevantes de arXiv y genera respuestas basadas de manera estricta en la evidencia."
)

# =====================================================================
# 2. CARGA DE RECURSOS CON CACHÉ (Hugging Face Local)
# =====================================================================
@st.cache_resource
def inicializar_recursos():
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    # Validar API KEY de Gemini para la generación
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key and "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        os.environ["GOOGLE_API_KEY"] = api_key
        
    if not os.environ.get("GOOGLE_API_KEY"):
        return "error_api_key", None, None

    # 1. Cargar embeddings locales (exactamente igual que en tu Notebook)
    embeddings_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # 2. Cargar base vectorial FAISS
    if not os.path.exists("faiss_index"):
        return "error_faiss_no_existe", None, None
        
    db = FAISS.load_local(
        "faiss_index", 
        embeddings_model, 
        allow_dangerous_deserialization=True
    )
    
    # 3. Inicializar Gemini 2.5 Flash para responder
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.0
    )
    
    return "ok", db, llm

# Mostrar indicador de carga mientras lee el modelo desde el disco
with st.spinner("⏳ Cargando base de datos y modelos... (Esto tomará solo unos segundos porque ya están descargados)"):
    estado, db_vectorial, llm = inicializar_recursos()

# Manejo de errores visuales
if estado == "error_api_key":
    st.error("❌ No se encontró la 'GOOGLE_API_KEY'.")
    st.stop()
elif estado == "error_faiss_no_existe":
    st.error("❌ No se encontró la carpeta 'faiss_index'.")
    st.info("Asegúrate de ejecutar la celda `db_vectorial.save_local('faiss_index')` en tu Notebook para generarla.")
    st.stop()

# =====================================================================
# 3. LÓGICA DE BÚSQUEDA Y PROMPT RAG (Requerimientos D y E)
# =====================================================================
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def recuperar_evidencias(query: str, vector_store, top_k: int = 3, similarity_threshold: float = 0.40):
    # En local, similarity_search_with_relevance_scores puede variar de escala según la distancia L2
    resultados = vector_store.similarity_search_with_relevance_scores(query, k=top_k)
    evidencias_filtradas = []
    for doc, score in resultados:
        if score >= similarity_threshold:
            evidencias_filtradas.append((doc, score))
    return evidencias_filtradas

prompt_template = ChatPromptTemplate.from_messages([
    ("system", (
        "Eres un asistente de investigación científica altamente confiable especializado en artículos de arXiv.\n\n"
        "INSTRUCCIONES DE RESPUESTA:\n"
        "1. Responde a la pregunta del usuario utilizando ÚNICAMENTE el contexto provisto abajo.\n"
        "2. Si el contexto provisto está vacío, es irrelevante, o no contiene información suficiente para responder con certeza completa, "
        "debes responder EXACTAMENTE con la siguiente frase, sin añadir nada más:\n"
        "'Lo siento, pero el corpus de arXiv cargado no contiene suficiente información para responder a tu consulta.'\n"
        "3. No inventes datos, no alucines, ni uses conocimientos externos fuera de los documentos proporcionados.\n"
        "4. Redacta tu respuesta de manera profesional, estructurada y en español.\n\n"
        "CONTEXTO RECUPERADO DE ARXIV:\n"
        "{context}"
    )),
    ("human", "{question}")
])

# =====================================================================
# 4. SISTEMA DE CHAT INTERACTIVO
# =====================================================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Historial del chat
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "evidencias" in message and message["evidencias"]:
            with st.expander("📖 Ver evidencias científicas utilizadas"):
                for idx, (doc, score) in enumerate(message["evidencias"], 1):
                    st.markdown(f"**[{idx}] {doc.metadata.get('title', 'Título N/A')}**")
                    st.markdown(f"*Score de Similitud: {score:.4f}*")
                    st.caption(doc.metadata.get("abstract", "Abstract N/A"))
                    st.markdown("---")

# Captura de preguntas
if prompt := st.chat_input("Escribe tu consulta sobre IA, Machine Learning o Ciencias de la Computación..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Buscando evidencias y redactando respuesta..."):
            evidencias = recuperar_evidencias(
                query=prompt, 
                vector_store=db_vectorial, 
                top_k=3, 
                similarity_threshold=0.40
            )
            
            if not evidencias:
                respuesta = "Lo siento, pero el corpus de arXiv cargado no contiene suficiente información para responder a tu consulta."
                st.markdown(respuesta)
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": respuesta, 
                    "evidencias": []
                })
            else:
                contexto_formateado = ""
                for i, (doc, score) in enumerate(evidencias):
                    contexto_formateado += f"\n--- Documento {i+1} (Similitud: {score:.4f}) ---\n"
                    contexto_formateado += doc.page_content + "\n"
                
                chain = prompt_template | llm | StrOutputParser()
                respuesta = chain.invoke({
                    "context": contexto_formateado,
                    "question": prompt
                })
                
                st.markdown(respuesta)
                
                with st.expander("📖 Ver evidencias científicas utilizadas"):
                    for idx, (doc, score) in enumerate(evidencias, 1):
                        st.markdown(f"**[{idx}] {doc.metadata.get('title', 'Título N/A')}**")
                        st.markdown(f"*Score de Similitud: {score:.4f}*")
                        st.caption(doc.metadata.get("abstract", "Abstract N/A"))
                        st.markdown("---")
                
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": respuesta, 
                    "evidencias": evidencias
                })