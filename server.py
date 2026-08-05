import os
import random
import numpy as np
import torch
from flask import Flask, render_template, request, jsonify
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)
app.secret_key = os.urandom(24)
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", cache_folder="./cache")


with open("math_words.txt", "r", encoding="utf-8") as math_words:
    MATH_WORDS = [word.strip().lower() for word in math_words if word.strip()]


MATH_WORDS_EMBEDDINGS = [model.encode(word, convert_to_tensor=True) for word in MATH_WORDS if word]

secret_word = None
secret_word_embedding = None
user_word = None
user_word_embedding = None


def get_cos_sim():
    if secret_word_embedding is None or user_word_embedding is None:
        return torch.tensor([[0.0]])
    
    return util.cos_sim(secret_word_embedding, user_word_embedding)


def get_random_word():
    return random.choice(MATH_WORDS)


@app.route("/guess", methods=["POST"])
def guess():
    global user_word, user_word_embedding
    data = request.get_json()
    user_word = data.get("word") if data else None
    
    if user_word == None:
        return jsonify({"cos_sim": "0"})
    elif user_word in MATH_WORDS:
        user_word_embedding = MATH_WORDS_EMBEDDINGS[MATH_WORDS.index(user_word)]
    else:
        user_word_embedding = model.encode(user_word, convert_to_tensor=True)
    
    cos_sim = round(get_cos_sim()[0, 0].item(), 6)
    
    print(f"Secret word: {secret_word}, User word: {user_word}, COS_SIM: {cos_sim}")
    
    if cos_sim == 1:
        return jsonify({"cos_sim": str(cos_sim), "win": True})
    
    return jsonify({"cos_sim": str(cos_sim), "win": False})


@app.route("/")
def index():
    global secret_word, secret_word_embedding
    secret_word = get_random_word()
    secret_word_embedding = MATH_WORDS_EMBEDDINGS[MATH_WORDS.index(secret_word)]
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)