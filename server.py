import random
from flask import Flask, render_template, request, jsonify
from sentence_transformers import SentenceTransformer

app = Flask(__name__)
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", cache_folder="./cache")

with open("math_words.txt", "r", encoding="utf-8") as math_words:
    MATH_WORDS = [word.strip().lower() for word in math_words if word.strip()]

secret_word = ""
user_word = ""

def get_random_word():
    return random.choice(MATH_WORDS)

@app.route("/guess", methods=["POST"])
def guess():
    data = request.get_json()
    user_word = data.get("word") if data else None
    return jsonify({"word": user_word})

@app.route("/")
def index():
    secret_word = get_random_word()
    return render_template("index.html")

if __name__ == "__main__":
    try:
        app.run(debug=True, port=5000)
    except Exception as e:
        print("Ошибка:", e)