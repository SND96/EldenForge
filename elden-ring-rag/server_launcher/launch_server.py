from flask import Flask, request, jsonify
import pickle
import faiss
import numpy as np

app = Flask(__name__)

index = faiss.read_index("indexer/embeddings_index_flatl2.faiss")
with open("indexer/index_to_text.pkl", "rb") as f:
    index_to_text = pickle.load(f)

@app.route('/search', methods=['POST'])
def search():
    content = request.json
    query_embedding = np.array(content['embedding']).astype('float32').reshape(1, -1)
    k = content.get('k', 5)
    D, I = index.search(query_embedding, k)
    results = [index_to_text[i] for i in I[0]]
    return jsonify({'results': results, 'distances': D.tolist()})

if __name__ == '__main__':
    app.run(port=5000)
