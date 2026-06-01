from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class TFIDFSearch:
    def __init__(self, documents):
        self.documents = documents
        # Reconstruir el string limpio a partir de los tokens procesados
        self.corpus = [" ".join(doc['tokens']) for doc in documents]
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)

    def search(self, query, clean_text, top_k=5):
        query_tokens = clean_text(query)
        query_text = " ".join(query_tokens)
        
        if not query_text.strip():
            return []

        # Vectorizar consulta y calcular similitud coseno contra la matriz densa
        query_vector = self.vectorizer.transform([query_text])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()

        # Extraer los índices de los mejores scores ordenados
        top_indices = similarities.argsort()[::-1][:top_k]
        results = []

        for idx in top_indices:
            score = similarities[idx]
            if score > 0:
                results.append({
                    'id': self.documents[idx]['id'],
                    'title': self.documents[idx]['title'],
                    'score': float(score)
                })

        return results