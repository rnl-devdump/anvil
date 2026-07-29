# Project Architecture: LLM-RAG Quiz Application

## 1. Project Overview
This project is an LLM-powered application that parses PDF documents to automatically generate JSON-formatted quizzes and allows users to ask specific questions about the document (RAG). 
**Hardware Target:** Intel Core i3 (12th Gen) with 8GB/16GB RAM (CPU-only inference).

## 2. The "Lean Stack"
To maintain performance on lightweight hardware and ensure strict prompt control, this project bypasses heavy abstractions like LangChain in favor of a lean, purpose-built stack:
*   **PDF Extraction:** `PyMuPDF` (or `pdfplumber`) for fast, reliable plaintext extraction.
*   **Vector Database:** `ChromaDB` (runs locally, handles embeddings natively).
*   **JSON Enforcement:** `Instructor` + `Pydantic` to physically constrain the LLM output.
*   **Local LLM Engine:** `Ollama` running lightweight models.

## 3. Data Flow A: Quiz Generation (Chunk-and-Map Strategy)
Due to hardware constraints (CPU memory/KV cache limits), the system must **not** feed an entire PDF into the model at once, despite large theoretical context windows.
1.  **Parse & Chunk:** Extract text from the PDF and split it into semantic chunks (approx. 500 tokens).
2.  **Iterative Micro-Prompts:** Feed one chunk at a time to the LLM. 
3.  **Generate:** Ask the LLM to generate 1-2 questions based *strictly* on that chunk.
4.  **Aggregate:** Append the generated JSON objects into a master array.

## 4. Data Flow B: The RAG Assistant (Q&A)
When a user asks a specific question about the uploaded document:
1.  **Embed Query:** The user's question (e.g., "Explain cell energy") is embedded natively by ChromaDB.
2.  **Retrieve:** ChromaDB performs a similarity search (`collection.query()`) to fetch only the top 1-3 most relevant chunks.
3.  **Answer:** The retrieved plaintext is passed to the LLM as context to answer the user's specific question, eliminating hallucinations.

## 5. JSON Schema & Enforcement
The output must be a valid JSON array of objects. `Instructor` is used with `Pydantic` to enforce this schema perfectly, avoiding the unreliability of standard prompt engineering.

**Validated Schema:**
```json
[
  {
    "type": "MULTIPLE_CHOICE",
    "question": "<question text>",
    "choices": ["<choice1>", "<choice2>", "<choice3>", "<choice4>"],
    "answer": "<exact string of the correct choice>"
  },
  {
    "type": "IDENTIFICATION",
    "question": "<question text with a blank represented by __>",
    "answer": "<correct answer>"
  }
]
```

## 6. Model & Hardware Specifications
*   **Selected Model:** `Phi-4-Mini` (3.8B parameters, Q4 Quantized).
*   **Why Phi-4-Mini:** Trained heavily on "textbook-like" synthetic data, making it exceptional at reading comprehension and logical quiz generation. It natively supports function calling.
*   **Memory Management:** The Q4 quantized model requires ~2.5 GB of RAM. The 500-token chunking strategy prevents the KV Cache from exploding, allowing smooth, continuous processing on an i3 processor without crashing the system.
