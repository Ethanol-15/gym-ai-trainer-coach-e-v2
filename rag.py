from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json

# load your dataset
with open('gym_data.json', 'r') as f:
    gym_data = json.load(f)

# load embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# convert entries to searchable text
entry_texts = []
for entry in gym_data:
    if entry["input"] != "":
        text = entry["instruction"] + " " + entry["input"]
    else:
        text = entry["instruction"]
    entry_texts.append(text)

# build FAISS index
embeddings = embedder.encode(entry_texts)
embeddings = np.array(embeddings).astype('float32')
dimension  = embeddings.shape[1]
index      = faiss.IndexFlatL2(dimension)
index.add(embeddings)

def find_relevant_entries(question, top_k=3):
    question_vector = embedder.encode([question])
    question_vector = np.array(
        question_vector
    ).astype('float32')
    distances, indices = index.search(
        question_vector, top_k
    )
    relevant = []
    for idx in indices[0]:
        relevant.append(gym_data[idx])
    return relevant