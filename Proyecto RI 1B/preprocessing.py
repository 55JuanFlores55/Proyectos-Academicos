import pandas as pd
import re
import os
import glob
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Set de stopwords en inglés
STOPWORDS = set(stopwords.words('english'))

def clean_text(text):
    """
    Realiza el procesamiento básico de texto: minúsculas, remoción de etiquetas HTML,
    eliminación de caracteres especiales, tokenización y filtrado de stopwords.
    """
    # Minúsculas
    text = text.lower()

    # Eliminar etiquetas html tipo <...>
    text = re.sub(r'<.*?>', ' ', text)

    # Eliminar caracteres especiales y números
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)

    # Tokenización
    tokens = word_tokenize(text)

    # Eliminar stopwords y palabras excesivamente cortas (longitud <= 2)
    tokens = [
        word for word in tokens
        if word not in STOPWORDS and len(word) > 2
    ]

    return tokens

def load_all_corpora(directory_path):
    """
    Escanea dinámicamente el directorio buscando todos los archivos CSV, unifica
    los documentos y genera identificadores únicos combinando el origen para evitar colisiones.
    """
    csv_files = glob.glob(os.path.join(directory_path, "*.csv"))
    all_documents = []
    
    print(f"\n📂 Detectados {len(csv_files)} archivos de datos en la carpeta '{directory_path}'.")
    
    for file_path in csv_files:
        file_name = os.path.basename(file_path)
        # Crear un prefijo identificador según el archivo (ej: ModApte_train.csv -> apte_tr)
        prefix = file_name.replace("Mod", "").replace(".csv", "").lower()[:7]
        
        print(f"  ├─ Procesando e indexando: {file_name}...")
        try:
            df = pd.read_csv(file_path)
            
            for _, row in df.iterrows():
                text = str(row['text'])
                title = str(row['title']) if pd.notna(row['title']) else "Sin Título"
                topics = str(row['topics']) if pd.notna(row['topics']) else ""
                
                # Prevenir colisiones de IDs combinando el prefijo con el new_id del renglón
                unique_id = f"{prefix}_{row['new_id']}"
                
                all_documents.append({
                    'id': unique_id,
                    'title': title,
                    'text': text,
                    'tokens': clean_text(text),
                    'topics': topics
                })
        except Exception as e:
            print(f"  ❌ Error crítico al procesar el archivo {file_name}: {e}")
            
    return all_documents