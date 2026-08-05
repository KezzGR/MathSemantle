import os
import random
import torch
import logging
from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from sentence_transformers import SentenceTransformer, util

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.INFO, handlers=[logging.StreamHandler(), logging.FileHandler("logs/app.log", encoding="utf-8")])

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SESSION_TYPE"] = 'filesystem'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
Session(app)

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", cache_folder="./cache")


with open("math_words.txt", "r", encoding="utf-8") as math_words:
    MATH_WORDS = sorted([word.strip().lower() for word in math_words if word.strip()])
    
if not MATH_WORDS:
    error_message = "Файл math_words.txt пуст, либо отсутствует."
    logging.error(error_message)
    raise RuntimeError(error_message)

MATH_WORDS_SET = set(MATH_WORDS)

MATH_WORDS_EMBEDDINGS = [model.encode(word, convert_to_tensor=True) for word in MATH_WORDS if word]
MATH_WORDS_TO_EMBEDDINGS_DICT = dict(zip(MATH_WORDS, MATH_WORDS_EMBEDDINGS))


def get_word_embedding(word: str) -> torch.Tensor:
    if word in MATH_WORDS_TO_EMBEDDINGS_DICT:
        return MATH_WORDS_TO_EMBEDDINGS_DICT[word]
    else:
        logger.info(f"В кэш добавлен эмбеддинг для нового слова {word}.")
        embedding = model.encode(word, convert_to_tensor=True)
        MATH_WORDS_TO_EMBEDDINGS_DICT[word] = embedding
        return embedding


def get_cos_sim(first_word: str, second_word: str) -> torch.Tensor:
    if first_word == "" or second_word == "":
        logger.warning("При попытке получить косинусное сходство первое и(или) второе слово оказалось пустым. Метод server.get_cos_sim(str, str) вернул нулевой тензор.")
        return torch.tensor([[0.0]])
    
    return util.cos_sim(get_word_embedding(first_word), get_word_embedding(second_word))


def get_random_word():
    return random.choice(MATH_WORDS)


@app.route("/guess", methods=["POST"])
def guess():
    user_word = request.get_json().get("word").strip().lower() if request.get_json() else None
    
    if "secret_word" not in session:
        logging.error("Секретное слово не назначено, игра не началась. Ошибка отправлена на front-end.")
        return jsonify({"error": "Игра не начата."})
    if user_word is None:
        logging.warning("Не удалось получить JSON с front-end. Ошибка отправлена на front-end.")
        return jsonify({"error": "JSON не передался."})
    if len(user_word) > 100:
        logging.warning("От пользователя пришло слишком длинное слово. Ошибка отправлена на front-end.")
        return jsonify({"error": "Слишком длинное слово."})
    
    session["user_word"] = user_word
    
    if session["user_word"] == "":
        logging.warning("От пользователя отправилась пустая строка, а не слово. Отправлено косинусное сходство = 0.0")
        return jsonify({"cos_sim": 0.0, "win": False})
    
    cos_sim = round(get_cos_sim(session["secret_word"], session["user_word"])[0, 0].item(), 6)
    
    logger.info(f"Secret Word: {session['secret_word']}, User Word: {session['user_word']}, Cosine Similarity: {cos_sim}")
    
    if session["secret_word"] == session["user_word"] or cos_sim > 0.9999:
        logging.info(f"Пользователь отгадал слово. Было загадано: {session["secret_word"]}")
        return jsonify({"cos_sim": cos_sim, "win": True})
    
    return jsonify({"cos_sim": cos_sim, "win": False})


@app.route("/")
def index():
    logging.info("Сессия запущена.")
    session["secret_word"] = get_random_word()
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)