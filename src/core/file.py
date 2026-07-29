# src/core/file.py
import os
import re

import pymupdf

from src.core.config import CHARS_PER_TOKEN, CHUNK_TARGET_TOKENS


class File:

    def __init__(self, filepath: str, raw_text: str | None = None):

        self.filepath = filepath

        self.filetype = self._filetype(filepath)

        self.pages_dict: dict[int, str] = {}

        self._all_chunks: list[tuple[int, str]] = []

        self.raw_text = raw_text


    @staticmethod
    def _filetype(filepath: str) -> str:

        _, ext = os.path.splitext(filepath)

        return ext.lstrip(".").lower()


    @staticmethod
    def split_into_sentences(text: str) -> list[str]:
        if not text:
            return []

        sentences = []
        for line in re.split(r"[\r\n]+", text):
            line = line.strip()
            if not line:
                continue
            for part in re.split(r"(?<=[.!?])\s+", line):
                part = part.strip()
                if part:
                    sentences.append(part)
        return sentences


    @staticmethod
    def estimate_tokens(text: str) -> int:

        return max(1, len(text) // CHARS_PER_TOKEN)


    def _chunk_sentences(self, page_num: int, sentences: list[str]) -> None:
        target_chars = CHUNK_TARGET_TOKENS * CHARS_PER_TOKEN
        current: list[str] = []
        current_len = 0

        for sentence in sentences:
            sentence_len = len(sentence)
            
            if sentence_len > target_chars:
                if current:
                    chunk_text = " ".join(current).strip()
                    if len(chunk_text) > 10:
                        self._all_chunks.append((page_num, chunk_text))
                    current = []
                    current_len = 0
                
                words = sentence.split(" ")
                for word in words:
                    word_len = len(word)
                    space_len = 1 if current else 0
                    if current and current_len + space_len + word_len > target_chars:
                        chunk_text = " ".join(current).strip()
                        if len(chunk_text) > 10:
                            self._all_chunks.append((page_num, chunk_text))
                        current = [word]
                        current_len = word_len
                    else:
                        current.append(word)
                        current_len += space_len + word_len
            else:
                space_len = 1 if current else 0
                if current and current_len + space_len + sentence_len > target_chars:
                    chunk_text = " ".join(current).strip()
                    if len(chunk_text) > 10:
                        self._all_chunks.append((page_num, chunk_text))
                    current = [sentence]
                    current_len = sentence_len
                else:
                    current.append(sentence)
                    current_len += space_len + sentence_len

        if current:
            chunk_text = " ".join(current).strip()
            if len(chunk_text) > 10:
                self._all_chunks.append((page_num, chunk_text))


    def read_pdf(self) -> None:

        try:

            doc = pymupdf.open(self.filepath)

            for page_num, page in enumerate(doc):

                raw_text = page.get_text("text", sort=True) or ""

                self.pages_dict[page_num + 1] = raw_text

            doc.close()

            self._process_pages()

        except Exception as e:

            raise RuntimeError(f"Failed to read PDF: {e}") from e


    def _process_pages(self) -> None:

        self._all_chunks.clear()

        for page_num, page_text in self.pages_dict.items():

            sentences = self.split_into_sentences(page_text)

            self._chunk_sentences(page_num, sentences)


    def read_plain_text(self) -> None:

        text = self.raw_text or ""

        self.pages_dict = {1: text}

        self._process_pages()


    def parse_file(self) -> None:

        if self.filetype == "pdf":

            self.read_pdf()

        elif self.filetype == "txt":

            with open(self.filepath, encoding="utf-8") as f:

                self.raw_text = f.read()

            self.read_plain_text()

        elif self.filepath == "NO_FILEPATH" and self.raw_text:

            self.read_plain_text()

        else:

            raise ValueError(f"Unsupported file type: {self.filetype or 'unknown'}")


    def get_chunks(self) -> list[tuple[int, str]]:

        return self._all_chunks


    @property
    def display_name(self) -> str:

        if self.filepath == "NO_FILEPATH":

            return "Pasted text"

        return os.path.basename(self.filepath)
