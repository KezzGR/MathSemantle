from flask import Flask, render_template, request, jsonify
from sentence_transformers import SentenceTransformer

app = Flask(__name__)
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", cache_folder="./cache")

@app.route("/guess", methods=["POST"])
def guess():
    data = request.get_json()
    user_word = data.get("word") if data else None
    return jsonify({"word": user_word})

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    try:
        app.run(debug=True, port=5000)
    except Exception as e:
        print("Ошибка:", e)