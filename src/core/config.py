# src/core/config.py
import os


LLM_MODEL = os.getenv("ANVIL_LLM_MODEL", "model")

EMBED_MODEL = os.getenv("ANVIL_EMBED_MODEL", "nomic-embed-text")


CHUNK_TARGET_TOKENS = int(os.getenv("ANVIL_CHUNK_TOKENS", "500"))

CHARS_PER_TOKEN = 4


RAG_TOP_K = int(os.getenv("ANVIL_RAG_TOP_K", "3"))


CHROMA_PATH = os.getenv("ANVIL_CHROMA_PATH", "./data/chroma_db")

COLLECTION_NAME = os.getenv("ANVIL_COLLECTION", "documents")


QUIZ_HISTORY_PATH = os.getenv("ANVIL_QUIZ_HISTORY", "./data/quiz_history/history.json")
