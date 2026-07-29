# samples/parser.py
import os
import re
import chromadb
import ollama
import customtkinter as ctk
from customtkinter import filedialog
from PyPDF2 import PdfReader


_currentfile = None
_pages = None
_page_content = []
_chunks = []
_isEmbedded = False

client = chromadb.PersistentClient(path="./data/test_db")
collection = client.get_or_create_collection(name="test_collection")

def split(text: str):
    return re.split(r'(?<=[.!?])\s+', text)

def open_file():

    filepath = filedialog.askopenfilename(
        title="Upload your materials",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
    )
    if filepath:
        global _currentfile
        _currentfile = filepath


        pdf_text(_currentfile)


def pdf_text(filepath: str):
    global _pages
    try:
        reader = PdfReader(filepath)
        _pages = len(reader.pages)

        for i in range(_pages):
            page_text = reader.pages[i].extract_text()
            _page_content.append(page_text)
            page_chunks = split(page_text)


            _chunks.extend(page_chunks) 

        clean_name = os.path.basename(filepath)
        print(f"Successfully read: {clean_name}")
    except Exception as e:
        print(f"Error reading PDF: {e}")

def plaintext(text: str):

    _chunks.extend(split(text))


def embed():
    for i, (page_num, text) in enumerate(_chunks):

        cleaned_text = text.replace("\n", " ").strip()
        cleaned_text = " ".join(cleaned_text.split())


        if len(cleaned_text) < 10:
            continue


        response = ollama.embed(model="nomic-embed-text", input=cleaned_text)
        vector = response["embeddings"][0]


        collection.upsert(
            ids=[f"id_{i}"],
            embeddings=[vector],
            documents=[cleaned_text],
            metadatas=[{"page": page_num}]
        )
"""
question = "What is a paragraph"
print(f"\nSearching for: '{question}'")

# -- corrects query embedding syntax
query_response = ollama.embed(model="nomic-embed-text", input=question)
query_vector = query_response["embeddings"][0]

results = collection.query(
    query_embeddings=[query_vector],
    n_results=1
)
print("\n--- Closest Match Found in Database ---")
print(results['documents'][0][0])
"""

open_file()
