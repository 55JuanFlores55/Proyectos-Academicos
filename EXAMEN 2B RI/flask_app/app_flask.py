"""
Alternativa a app.py (Streamlit) usando Flask puro.
Misma lógica de RAG (FAISS + Gemini), interfaz de chat vía HTTP normal
(fetch/POST), sin WebSocket. Útil si Streamlit se ve bloqueado localmente
por firewall/antivirus, y también funciona igual en la nube.

Ejecutar localmente:
    python app_flask.py
Luego abrir: http://localhost:5000  (o el puerto que elijas)
"""

import os

# FIX Windows: evita el choque de OpenMP entre torch y faiss (mismo problema
# que en la versión Streamlit). Debe ir ANTES de cualquier import pesado.
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

app = Flask(__name__)

# --------------------------------------------------------------------------
# Carga de recursos (una sola vez, al arrancar el servidor)
# --------------------------------------------------------------------------
print("Cargando modelo de embeddings y base vectorial (puede tardar unos segundos)...")

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError(
        "No se encontró GOOGLE_API_KEY. Defínela en tu archivo .env o como "
        "variable de entorno antes de arrancar el servidor."
    )

embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

if not os.path.exists("faiss_index"):
    raise RuntimeError(
        "No se encontró la carpeta 'faiss_index'. Cópiala junto a este archivo "
        "(la genera tu notebook con db_vectorial.save_local('faiss_index'))."
    )

db_vectorial = FAISS.load_local(
    "faiss_index", embeddings_model, allow_dangerous_deserialization=True
)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0)

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "Eres un asistente de investigación científica altamente confiable "
                "especializado en artículos de arXiv.\n\n"
                "INSTRUCCIONES DE RESPUESTA:\n"
                "1. Responde a la pregunta del usuario utilizando ÚNICAMENTE el "
                "contexto provisto abajo.\n"
                "2. Si el contexto provisto está vacío, es irrelevante, o no "
                "contiene información suficiente para responder con certeza "
                "completa, debes responder EXACTAMENTE con la siguiente frase, "
                "sin añadir nada más:\n"
                "'Lo siento, pero el corpus de arXiv cargado no contiene "
                "suficiente información para responder a tu consulta.'\n"
                "3. No inventes datos, no alucines, ni uses conocimientos "
                "externos fuera de los documentos proporcionados.\n"
                "4. Redacta tu respuesta de manera profesional, estructurada y "
                "en español.\n\n"
                "CONTEXTO RECUPERADO DE ARXIV:\n{context}"
            ),
        ),
        ("human", "{question}"),
    ]
)
chain = prompt_template | llm | StrOutputParser()

print("✅ Listo. Servidor Flask preparado.")


# --------------------------------------------------------------------------
# Lógica RAG (idéntica a la de app.py / notebook, secciones D y E)
# --------------------------------------------------------------------------
def recuperar_evidencias(query: str, top_k: int = 3, similarity_threshold: float = 0.40):
    resultados = db_vectorial.similarity_search_with_relevance_scores(query, k=top_k)
    return [(doc, score) for doc, score in resultados if score >= similarity_threshold]


def responder(query: str):
    evidencias = recuperar_evidencias(query)

    if not evidencias:
        return {
            "answer": (
                "Lo siento, pero el corpus de arXiv cargado no contiene "
                "suficiente información para responder a tu consulta."
            ),
            "evidence": [],
        }

    contexto = ""
    for i, (doc, score) in enumerate(evidencias):
        contexto += f"\n--- Documento {i + 1} (Similitud: {score:.4f}) ---\n"
        contexto += doc.page_content + "\n"

    respuesta = chain.invoke({"context": contexto, "question": query})

    evidence_payload = [
        {
            "title": doc.metadata.get("title", "Título N/A"),
            "abstract": doc.metadata.get("abstract", "")[:300],
            "score": round(float(score), 4),
        }
        for doc, score in evidencias
    ]
    return {"answer": respuesta, "evidence": evidence_payload}


# --------------------------------------------------------------------------
# Rutas web (requisito G: interfaz de chat)
# --------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("chat.html")


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(force=True)
    query = (data.get("query") or "").strip()
    if not query:
        return jsonify({"error": "Consulta vacía"}), 400
    try:
        result = responder(query)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # host="0.0.0.0" para que también sea accesible desde otras máquinas de tu red si hace falta
    app.run(host="0.0.0.0", port=5000, debug=False)
