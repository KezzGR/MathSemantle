import os

class Config:
    LOGS_DIR = "logs"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    LOG_FILE = os.path.join(LOGS_DIR, "app.log")
    
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = "./flask_session"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    
    MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
    MODEL_CACHE_FOLDER = "./cache"
    
    MATH_WORDS_FILE = "math_words.txt"
    
    MAX_USER_WORD_LENGTH = 100
    COS_SIM_ROUND = 6
    COS_SIM_THRESHOLD_WIN = 0.9999
    
    DEBUG = True
    PORT = 5000