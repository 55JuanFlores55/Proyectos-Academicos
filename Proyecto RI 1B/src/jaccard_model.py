def jaccard_similarity(query_tokens, doc_tokens):
    """Calcula el coeficiente de Jaccard sobre vectores binarios lógicos."""
    query_set = set(query_tokens)
    doc_set = set(doc_tokens)

    intersection = len(query_set.intersection(doc_set))
    union = len(query_set.union(doc_set))

    if union == 0:
        return 0

    return intersection / union

def search_jaccard(query, documents, clean_text, top_k=5):
    """Ejecuta consultas de texto libre ordenando resultados por el score binario."""
    query_tokens = clean_text(query)
    results = []

    for doc in documents:
        score = jaccard_similarity(query_tokens, doc['tokens'])
        if score > 0:
            results.append({
                'id': doc['id'],
                'title': doc['title'],
                'score': score
            })

    # Ordenar de forma estrictamente descendente
    results = sorted(results, key=lambda x: x['score'], reverse=True)
    return results[:top_k]