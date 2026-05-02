from flask import Flask, render_template, request, jsonify
import re
from knowledge_base import KNOWLEDGE_BASE
app = Flask(__name__)


def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text


def get_response(user_input):
    user_input = preprocess(user_input)
    user_words = set(user_input.split())

    for question, answer in KNOWLEDGE_BASE.items():
        key_words = set(preprocess(question).split())

        
        if key_words.issubset(user_words):
            return answer

    return "Answer not found"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    return jsonify({"response": get_response(user_message)})

if __name__ == "__main__":
    app.run(debug=True)