# Motor de Búsqueda para Gutenberg 1000 usando TF-IDF

## Descripción

Este proyecto implementa un **sistema de recuperación de información** sobre un corpus de aproximadamente **1000 libros** de Project Gutenberg utilizando el modelo **TF-IDF (Term Frequency - Inverse Document Frequency)** y **similitud coseno**.

El sistema permite ingresar una consulta textual mediante una función `Buscar()` y devuelve un **ranking de los documentos más relevantes** según su similitud con la consulta.

---

## Objetivos

* Cargar un corpus de 1000 documentos en formato `.txt`
* Preprocesar el texto
* Calcular la matriz **TF-IDF**
* Implementar una función de búsqueda
* Ordenar resultados por relevancia
* Recuperar los documentos mejor puntuados

---

## Tecnologías utilizadas

* **Python 3**
* scikit-learn
* pandas
* NumPy
* OS

---

## Estructura del proyecto

```bash id="v77mch"
proyecto/
│── gutenberg_1000/
│   │── book1.txt
│   │── book2.txt
│   │── book3.txt
│   │── ...
│   │── book1000.txt
│
│── buscador.py
│── notebook.ipynb
│── README.md
```

---

## Funcionamiento

### 1. Carga del corpus

Se recorren todos los archivos `.txt` almacenados en la carpeta `gutenberg_1000` y se guarda:

* contenido textual del libro
* nombre del archivo

---

### 2. Vectorización TF-IDF

Se utiliza scikit-learn para transformar cada documento en un vector numérico ponderado según:

* frecuencia del término (TF)
* frecuencia inversa del término (IDF)

Esto genera una **matriz documento-término**:

$$
documentos \times términos
$$

---

### 3. Función `Buscar()`

La función:

* recibe una consulta
* vectoriza la consulta usando el mismo modelo TF-IDF
* calcula similitud coseno con todos los documentos
* ordena resultados por score
* devuelve ranking

Ejemplo:

```python id="r5yz4w"
Buscar("love war king")
```

Salida esperada:

| Ranking | Documento    | Score |
| ------- | ------------ | ----: |
| 1       | book_102.txt |  0.81 |
| 2       | book_345.txt |  0.77 |
| 3       | book_020.txt |  0.74 |

---

## Código principal

```python id="u9n5c2"
def Buscar(consulta, top_n=10):
    query_vector = vectorizer_gutenberg.transform([consulta])
    similitudes = cosine_similarity(query_vector, tfidf_matrix_gutenberg).flatten()

    resultados = pd.DataFrame({
        "Documento": nombres_gutenberg,
        "Score": similitudes
    })

    resultados = resultados.sort_values(
        by="Score",
        ascending=False
    ).reset_index(drop=True)

    resultados.index += 1

    return resultados.head(top_n)
```

---

## Ejemplos de consultas

Búsqueda romántica:

```python id="b9z9q7"
Buscar("love romance marriage")
```

Búsqueda histórica:

```python id="s52i5x"
Buscar("war king battle")
```

Búsqueda científica:

```python id="yjlwmz"
Buscar("science technology future")
```

---

## Instalación

Clonar repositorio:

```bash id="w1nbu3"
git clone https://github.com/tuusuario/tu-repositorio.git
cd tu-repositorio
```

Instalar dependencias:

```bash id="yk9pju"
pip install pandas scikit-learn
```

---

## Resultados

El sistema genera un ranking de relevancia basado en contenido textual, permitiendo recuperar rápidamente documentos similares a una consulta dada.

Este enfoque constituye una base para motores de búsqueda más avanzados como los utilizados en bibliotecas digitales y sistemas de búsqueda documental.

---

## Autor

**Juan Flores**
Proyecto académico – Recuperación de Información

