from src.preprocessing import load_all_corpora, clean_text
from src.inverted_index import build_inverted_index
from src.jaccard_model import search_jaccard
from src.tfidf_model import TFIDFSearch
from src.bm25_model import BM25Search
from src.semantic_model import SemanticSearch
from src.evaluation import evaluate_all_models
from src.cli import (
    show_menu,
    print_results,
    print_comparison,
    print_evaluation_table,
    print_inverted_index_term
)

# Ruta base de la carpeta contenedora de todos los CSVs
CORPUS_DIR = "corpus"

print("\n🚀 Iniciando Framework Global de Recuperación de Información...")
print("Escaneando y unificando colecciones estructuradas (Carga Masiva Reuters)...")
documents = load_all_corpora(CORPUS_DIR)
print(f"\n✅ Base de datos unificada con éxito. Total global indexado: {len(documents)} documentos.")

print("\n🏗️  Construyendo Índice Invertido Propio bajo demanda (Requerimiento A)...")
custom_inverted_index = build_inverted_index(documents)
print(f"✅ Índice estructurado con {len(custom_inverted_index)} tokens únicos en las listas de posteo.")

print("\n🧠 Indexando y compilando matrices lógicas y bases vectoriales...")
tfidf_search = TFIDFSearch(documents)
bm25_search = BM25Search(documents)
semantic_search = SemanticSearch(documents)
print("🎯 ¡Todos los motores de búsqueda inicializados y en línea!\n")

while True:
    show_menu()
    option = input("\nSeleccione una opción (1-8): ").strip()

    if option == "8":
        print("\nCerrando de forma segura. ¡Éxito total en tu sustentación!\n")
        break

    if option == "5":
        term = input("\nIngrese la palabra exacta que desea rastrear en el índice propio: ").strip().lower()
        postings = custom_inverted_index.get(term, {})
        print_inverted_index_term(term, postings)
        continue

    if option == "7":
        print("\n⏳ Computando simulaciones analíticas contra qrels...")
        metrics = evaluate_all_models(documents, search_jaccard, tfidf_search, bm25_search, semantic_search, clean_text, k=5)
        print_evaluation_table(metrics)
        continue

    if option not in ["1", "2", "3", "4", "6"]:
        print("\n❌ Entrada inválida. Intente de nuevo.")
        continue

    query = input("\nIngrese su consulta de texto libre: ").strip()
    if not query:
        print("⚠ La consulta ingresada no es válida.")
        continue

    # Ejecuciones simultáneas en tiempo real para poblar los visualizadores
    jaccard_res = search_jaccard(query, documents, clean_text, top_k=5)
    tfidf_res = tfidf_search.search(query, clean_text, top_k=5)
    bm25_res = bm25_search.search(query, clean_text, top_k=5)
    semantic_res = semantic_search.search(query, top_k=5)

    if option == "1":
        print_results(jaccard_res, "JACCARD BINARIO")
    elif option == "2":
        print_results(tfidf_res, "TF-IDF + COSENO")
    elif option == "3":
        print_results(bm25_res, "OKAPI BM25")
    elif option == "4":
        print_results(semantic_res, "EMBEDDINGS + BASE VECTORIAL FAISS")
    elif option == "6":
        print_comparison(jaccard_res, tfidf_res, bm25_res, semantic_res)