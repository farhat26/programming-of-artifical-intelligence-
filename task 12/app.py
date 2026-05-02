from flask import Flask, render_template, request, jsonify
import numpy as np
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Load dataset
dataset = load_dataset("ag_news")
df = dataset["train"].to_pandas()
df["text"] = df["text"]

# Load ML model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Precompute embeddings
news_embeddings = model.encode(df["text"].tolist(), show_progress_bar=True)


def get_top_news(query, top_k=5):
    query_vec = model.encode([query])
    scores = cosine_similarity(query_vec, news_embeddings)[0]
    top_indices = np.argsort(scores)[-top_k:][::-1]
    return df.iloc[top_indices]["text"].tolist()


# 🌐 Frontend page
@app.route("/")
def home():
    return render_template("index.html")


# 🔍 API endpoint
@app.route("/search", methods=["POST"])
def search():
    data = request.json
    query = data["query"]

    results = get_top_news(query)

    return jsonify({"results": results})


if __name__ == "__main__":
    app.run(debug=True)