import numpy as np

def calculate_query_metrics(retrieved_ids, relevant_ids, k=5):
    """Calcula las métricas exactas basadas en los documentos recuperados en la ventana K."""
    retrieved_at_k = retrieved_ids[:k]
    if not relevant_ids:
        return 0.0, 0.0, 0.0

    relevant_retrieved = [doc_id for doc_id in retrieved_at_k if doc_id in relevant_ids]
    num_rel_retrieved = len(relevant_retrieved)

    # Fórmulas de Recuperación de Información
    precision = num_rel_retrieved / k
    recall = num_rel_retrieved / len(relevant_ids)

    # Cálculo preciso de Average Precision (AP)
    ap_sum = 0.0
    num_relevant_found = 0
    for i, doc_id in enumerate(retrieved_at_k, start=1):
        if doc_id in relevant_ids:
            num_relevant_found += 1
            ap_sum += (num_relevant_found / i)
            
    ap = ap_sum / len(relevant_ids) if len(relevant_ids) > 0 else 0.0
    return precision, recall, ap

def evaluate_all_models(documents, search_jaccard, tfidf_search, bm25_search, semantic_search, clean_text, k=5):
    """Corre una simulación automatizada exhaustiva sobre las temáticas macro del corpus."""
    test_queries = {
        "earn": "company earnings profit quarterly results revenue",
        "acq": "merger acquisition shares stake takeover corporate contract",
        "crude": "crude oil petroleum barrels energy prices output",
        "grain": "grain wheat corn agriculture commodities cargo",
        "trade": "trade deficit tariff export import economic agreement"
    }

    models = ['Jaccard', 'TF-IDF', 'BM25', 'Semántico']
    metrics_summary = {model: {'precision': [], 'recall': [], 'ap': []} for model in models}

    print("\n" + "="*75)
    print(" 🛠️  MÉTRICAS INDIVIDUALES POR CONSULTA DE EVALUACIÓN (QRELS MASIVO)")
    print("="*75)

    for topic, query_text in test_queries.items():
        # Extracción dinámica en caliente del Ground Truth real
        relevant_ids = set([
            doc['id'] for doc in documents 
            if isinstance(doc['topics'], str) and topic in doc['topics'].lower()
        ])
        
        if not relevant_ids:
            continue

        results_dict = {
            'Jaccard': search_jaccard(query_text, documents, clean_text, top_k=k),
            'TF-IDF': tfidf_search.search(query_text, clean_text, top_k=k),
            'BM25': bm25_search.search(query_text, clean_text, top_k=k),
            'Semántico': semantic_search.search(query_text, top_k=k)
        }

        print(f"\n📌 Tópico Evaluado: '{topic.upper()}' ({len(relevant_ids)} documentos emparejados en qrels)")
        
        for model_name in models:
            retrieved_ids = [res['id'] for res in results_dict[model_name]]
            p, r, ap = calculate_query_metrics(retrieved_ids, relevant_ids, k=k)
            
            metrics_summary[model_name]['precision'].append(p)
            metrics_summary[model_name]['recall'].append(r)
            metrics_summary[model_name]['ap'].append(ap)
            
            print(f"  └─ [{model_name:10}] -> Precision@{k}: {p:.4f} | Recall@{k}: {r:.4f} | AP@{k}: {ap:.4f}")

    # Estructura del reporte global unificado
    final_report = {}
    for model_name in models:
        final_report[model_name] = {
            'precision': np.mean(metrics_summary[model_name]['precision']) if metrics_summary[model_name]['precision'] else 0,
            'recall': np.mean(metrics_summary[model_name]['recall']) if metrics_summary[model_name]['recall'] else 0,
            'map': np.mean(metrics_summary[model_name]['ap']) if metrics_summary[model_name]['ap'] else 0
        }
    return final_report