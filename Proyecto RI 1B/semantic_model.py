import os
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

class SemanticSearch:
    def __init__(self, documents, model_name='all-MiniLM-L6-v2', cache_path='corpus/embeddings_cache.npy'):
        self.documents = documents
        self.model = SentenceTransformer(model_name)
        self.texts = [doc['text'] for doc in documents]
        self.cache_path = cache_path
        
        # Sistema de persistencia para el bloque multicorpus masivo
        if os.path.exists(self.cache_path):
            print("   📦 Cargando embeddings vectoriales desde el caché en disco...")
            self.embeddings = np.load(self.cache_path)
            # Control de cambios en los CSV del corpus
            if self.embeddings.shape[0] != len(self.texts):
                print("   ⚠ Modificación detectada en los CSV. Recalculando matriz vectorial...")
                self.embeddings = self.model.encode(self.texts, show_progress_bar=True, convert_to_numpy=True)
                np.save(self.cache_path, self.embeddings)
        else:
            print("   ⏳ Generando embeddings semánticos por primera vez (esto tomará unos minutos)...")
            self.embeddings = self.model.encode(self.texts, show_progress_bar=True, convert_to_numpy=True)
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            np.save(self.cache_path, self.embeddings)
            print("   💾 Embeddings guardados en disco duro con éxito.")
        
        # Normalizar L2 para forzar que el producto interno equivalga a Similitud Coseno
        faiss.normalize_L2(self.embeddings)
        dimension = self.embeddings.shape[1]
        
        # Almacenamiento e Indexación de Base Vectorial en FAISS
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(self.embeddings)

    def search(self, query, top_k=5):
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)
        
        # Búsqueda matemática a bajo nivel por similitud vectorial
        scores, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:
                results.append({
                    'id': self.documents[idx]['id'],
                    'title': self.documents[idx]['title'],
                    'score': float(score)
                })
        return results