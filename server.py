import os
import random
import torch
import logging
from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from sentence_transformers import SentenceTransformer, util
from config import Config as cfg

os.makedirs(cfg.LOGS_DIR, exist_ok=True)
logging.basicConfig(format=cfg.LOG_FORMAT, datefmt=cfg.LOG_DATE_FORMAT,
                    level=logging.INFO, handlers=[logging.StreamHandler(), logging.FileHandler(cfg.LOG_FILE, encoding="utf-8")])

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SESSION_TYPE"] = cfg.SESSION_TYPE
app.config["SESSION_FILE_DIR"] = cfg.SESSION_FILE_DIR
app.config["SESSION_PERMANENT"] = cfg.SESSION_PERMANENT
app.config["SESSION_USE_SIGNER"] = cfg.SESSION_USE_SIGNER
Session(app)

model = SentenceTransformer(cfg.MODEL_NAME, cache_folder=cfg.MODEL_CACHE_FOLDER)


with open(cfg.MATH_WORDS_FILE, "r", encoding="utf-8") as math_words:
    MATH_WORDS = sorted([word.strip().lower() for word in math_words if word.strip()])
    
if not MATH_WORDS:
    error_message = "Файл math_words.txt пуст, либо отсутствует."
    logger.error(error_message)
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
        logger.error("Секретное слово не назначено, игра не началась. Ошибка отправлена на front-end.")
        return jsonify({"error": "Игра не начата."})
    if user_word is None:
        logger.warning("Не удалось получить JSON с front-end. Ошибка отправлена на front-end.")
        return jsonify({"error": "JSON не передался."})
    if len(user_word) > cfg.MAX_USER_WORD_LENGTH:
        logger.warning("От пользователя пришло слишком длинное слово. Ошибка отправлена на front-end.")
        return jsonify({"error": "Слишком длинное слово."})
    
    session["user_word"] = user_word
    
    if session["user_word"] == "":
        logger.warning("От пользователя отправилась пустая строка, а не слово. Отправлено косинусное сходство = 0.0")
        return jsonify({"cos_sim": 0.0, "win": False})
    
    cos_sim = round(get_cos_sim(session["secret_word"], session["user_word"])[0, 0].item(), cfg.COS_SIM_ROUND)
    
    logger.info(f"Secret Word: {session['secret_word']}, User Word: {session['user_word']}, Cosine Similarity: {cos_sim}")
    
    if session["secret_word"] == session["user_word"] or cos_sim > cfg.COS_SIM_THRESHOLD_WIN:
        logger.info(f"Пользователь отгадал слово. Было загадано: {session['secret_word']}")
        return jsonify({"cos_sim": cos_sim, "win": True})
    
    return jsonify({"cos_sim": cos_sim, "win": False})


@app.route("/")
def index():
    logger.info("Сессия запущена.")
    session["secret_word"] = get_random_word()
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=cfg.DEBUG, port=cfg.PORT)