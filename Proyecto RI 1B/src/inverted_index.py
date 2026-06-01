from collections import defaultdict

def build_inverted_index(documents):
    """
    Construye de forma nativa un índice invertido que mapea cada término único
    a los IDs de los documentos en los que aparece junto con su frecuencia local (TF).
    """
    inverted_index = defaultdict(dict)

    for doc in documents:
        doc_id = doc['id']
        tokens = doc['tokens']

        # Calcular frecuencias locales del documento actual
        term_freq = {}
        for token in tokens:
            term_freq[token] = term_freq.get(token, 0) + 1

        # Agregar datos estructurados al índice global
        for term, freq in term_freq.items():
            inverted_index[term][doc_id] = freq

    return inverted_index