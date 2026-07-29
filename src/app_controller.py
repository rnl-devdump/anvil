# src/app_controller.py
import json
from typing import Callable

from customtkinter import filedialog

from src.core.db import Db
from src.core.file import File
from src.core.llm import LlmService
from src.core.quiz_store import QuizStore
from src.core.schema import ParagraphEvaluation, QuizQuestion


class AppController:

    def __init__(self):

        self.db = Db()

        self.llm = LlmService()

        self.quiz_store = QuizStore()

        self.file: File | None = None

        self.quiz: list[QuizQuestion] = []

        self.active_quiz_id: str | None = None

        self.chat_history: list[dict] = []

        self.pdf_engine: str = "pymupdf"


    def set_pdf_engine(self, engine: str) -> None:

        self.pdf_engine = engine


    def load_file_path(self, filepath: str) -> None:

        self.file = File(filepath, pdf_engine=self.pdf_engine)

        self._load_and_embed()


    def open_file(self) -> str | None:

        filepath = filedialog.askopenfilename(
            title="Upload your materials",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ],
        )

        if not filepath:

            return None

        self.load_file_path(filepath)

        return filepath


    def load_pasted_text(self, text: str) -> None:

        cleaned = text.strip()

        if not cleaned:

            raise ValueError("Pasted text is empty.")

        self.file = File(filepath="NO_FILEPATH", raw_text=cleaned, pdf_engine=self.pdf_engine)

        self._load_and_embed()


    def _load_and_embed(self) -> None:

        if not self.file:

            return

        self.file.parse_file()

        count = self.db.embed(self.file)

        if count == 0:

            raise RuntimeError("No usable text chunks found in the document.")

        self.quiz = []

        self.active_quiz_id = None
        
        self.chat_history = []


    @property

    def is_loaded(self) -> bool:

        return self.file is not None and self.db.chunk_count > 0


    @property
    def document_label(self) -> str:

        if not self.file:

            return "No document loaded"

        chunks = len(self.file.get_chunks())

        return f"{self.file.display_name} — {chunks} chunks embedded"


    def generate_quiz(
        self,
        on_progress: Callable[[int, int, str], None] | None = None,
        on_chunk_error: Callable[[int, str], None] | None = None,
        preferences: str = ""
    ) -> list[dict]:

        if not self.is_loaded or not self.file:
            raise RuntimeError("Load a document before generating a quiz.")

        chunks = self.file.get_chunks()
        self.quiz = []
        total = len(chunks)

        for index, (_page_num, chunk_text) in enumerate(chunks):
            if on_progress:
                on_progress(index + 1, total, chunk_text[:80])

            try:
                response = self.llm.generate_questions_for_chunk(chunk_text, preferences=preferences)
                self.quiz.extend(response.questions)
            except Exception as e:
                if on_chunk_error:
                    on_chunk_error(index + 1, str(e))
                continue


        if not self.quiz:

            raise RuntimeError("Quiz generation failed for all chunks. Is Ollama running?")


        return [q.model_dump() for q in self.quiz]


    def save_quiz_to_history(self, questions: list[dict] | None = None) -> dict:

        payload = questions or [q.model_dump() for q in self.quiz]

        if not payload:

            raise RuntimeError("No quiz to save.")


        source = self.file.display_name if self.file else "Unknown"

        title = f"{source} ({len(payload)} Q)"

        record = self.quiz_store.add(title=title, source=source, questions=payload)

        self.active_quiz_id = record["id"]

        return record


    def load_quiz_from_history(self, quiz_id: str) -> list[dict]:

        record = self.quiz_store.get(quiz_id)

        if not record:

            raise ValueError("Quiz not found in history.")

        self.active_quiz_id = quiz_id

        self.quiz = record["questions"]

        return self.quiz


    def ask(self, question: str) -> tuple[str, list[str]]:

        cleaned = question.strip()

        if not cleaned:

            raise ValueError("Enter a question.")

        if not self.is_loaded:

            raise RuntimeError("Load a document first. Use Import in Quiz to add materials.")


        # Use the conversation history for better context
        history_text = "\n".join([m["content"] for m in self.chat_history[-2:]]) if self.chat_history else ""
        query_text = f"{history_text}\n{cleaned}".strip()
        
        context_chunks = self.db.query(query_text)

        if not context_chunks:

            raise RuntimeError("No relevant context found in the vector store.")


        response = self.llm.answer_question(cleaned, context_chunks, chat_history=self.chat_history)

        self.chat_history.append({"role": "user", "content": cleaned})
        self.chat_history.append({"role": "assistant", "content": response.answer})

        return response.answer, context_chunks


    def evaluate_paragraph(
        self, question: str, model_answer: str, user_answer: str
    ) -> ParagraphEvaluation:

        cleaned = user_answer.strip()

        if not cleaned:

            raise ValueError("Enter an answer before submitting.")

        return self.llm.evaluate_paragraph_answer(question, model_answer, cleaned)


    def quiz_as_json(self, indent: int = 2) -> str:

        if not self.quiz:

            return "[]"

        if isinstance(self.quiz[0], dict):

            payload = self.quiz
        else:

            payload = [q.model_dump() for q in self.quiz]

        return json.dumps(payload, indent=indent)
