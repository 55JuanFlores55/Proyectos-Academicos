from tabulate import tabulate
from colorama import Fore, Style, init

init(autoreset=True)

def show_menu():
    print(Fore.CYAN + "\n" + "=" * 65)
    print(Fore.CYAN + " 📊 SISTEMA MULTI-CORPUS DE RECUPERACIÓN DE INFORMACIÓN ")
    print(Fore.CYAN + "=" * 65)
    print(Fore.YELLOW + "\nSeleccione una opción de la rúbrica:\n")
    print("1. Buscar con Jaccard (Vectores Binarios)")
    print("2. Buscar con TF-IDF (Similitud Coseno)")
    print("3. Buscar con BM25 (Okapi Probabilístico)")
    print("4. Buscar con Recuperación Semántica (Embeddings Transformers + FAISS)")
    print("5. Consultar término en Índice Invertido Propio (Req. A)")
    print("6. Comparar rankings de todos los modelos lado a lado (Req. F)")
    print("7. Ejecutar Suite de Evaluación Completa (Precision, Recall, MAP - Req. E)")
    print("8. Salir de la terminal")

def print_results(results, model_name):
    if not results:
        print(Fore.RED + "\n❌ No se encontraron documentos relevantes para esta consulta.\n")
        return
    table = []
    for i, result in enumerate(results, start=1):
        table.append([i, result['id'], result['title'][:55], round(result['score'], 4)])
    print(Fore.GREEN + f"\n📌 RANKING DE RELEVANCIA ORDENADO - MOTOR {model_name}\n")
    print(tabulate(table, headers=["#", "Doc ID", "Título del Artículo", "Score de Relevancia"], tablefmt="fancy_grid"))

def print_inverted_index_term(term, postings):
    if not postings:
        print(Fore.RED + f"\n❌ El término '{term}' no existe dentro del índice invertido propio.\n")
        return
    table = [[doc_id, freq] for doc_id, freq in list(postings.items())[:20]]
    print(Fore.GREEN + f"\n📖 LISTA DE POSTEO INTERNA - Palabra Clave: '{term}' (Muestra de los primeros 20 docs)\n")
    print(tabulate(table, headers=["Doc ID (Posting List)", "Frecuencia Local (TF)"], tablefmt="fancy_grid"))

def print_comparison(jaccard, tfidf, bm25, semantic):
    max_len = max(len(jaccard), len(tfidf), len(bm25), len(semantic))
    table = []
    for i in range(max_len):
        row = [i + 1]
        row.append(f"{jaccard[i]['id']} ({round(jaccard[i]['score'], 2)})" if i < len(jaccard) else "-")
        row.append(f"{tfidf[i]['id']} ({round(tfidf[i]['score'], 2)})" if i < len(tfidf) else "-")
        row.append(f"{bm25[i]['id']} ({round(bm25[i]['score'], 2)})" if i < len(bm25) else "-")
        row.append(f"{semantic[i]['id']} ({round(semantic[i]['score'], 2)})" if i < len(semantic) else "-")
        table.append(row)
    print(Fore.MAGENTA + "\n📊 MATRIZ COMPARATIVA DE RANKINGS CRUZADOS [Doc ID (Score original)]\n")
    print(tabulate(table, headers=["Rank", "Jaccard (Binario)", "TF-IDF (Coseno)", "BM25 (Okapi)", "Semántico (FAISS)"], tablefmt="fancy_grid"))

def print_evaluation_table(metrics_summary):
    table = []
    for model, data in metrics_summary.items():
        table.append([model, round(data['precision'], 4), round(data['recall'], 4), round(data['map'], 4)])
    print(Fore.BLUE + "\n📈 REPORTE CUANTITATIVO GLOBAL DE RENDIMIENTO DEL SISTEMA\n")
    print(tabulate(table, headers=["Modelo / Algoritmo", "Media Precision@5", "Media Recall@5", "MAP (Mean Average Precision)"], tablefmt="fancy_grid"))