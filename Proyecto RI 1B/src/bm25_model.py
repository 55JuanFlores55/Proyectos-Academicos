from rank_bm25 import BM25Okapi

class BM25Search:
    def __init__(self, documents):
        self.documents = documents
        self.corpus = [doc['tokens'] for doc in documents]
        self.bm25 = BM25Okapi(self.corpus)

    def search(self, query, clean_text, top_k=5):
        query_tokens = clean_text(query)
        
        if not query_tokens:
            return []

        # Calcular scores a través del índice probabilístico
        scores = self.bm25.get_scores(query_tokens)
        top_indices = scores.argsort()[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = scores[idx]
            if score > 0:
                results.append({
                    'id': self.documents[idx]['id'],
                    'title': self.documents[idx]['title'],
                    'score': float(score)
                })

        return results