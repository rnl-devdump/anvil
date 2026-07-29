# src/core/llm.py
import threading
import json
from typing import Type, TypeVar
from openai import OpenAI

from src.core.config import LLM_MODEL
from src.core.schema import ChunkQuizResponse, ParagraphEvaluation, RagAnswer
from src.model import ensure_model_setup


T = TypeVar("T")


EXAMPLES = {

    "ChunkQuizResponse": {
        "questions": [
            {
                "type": "MULTIPLE_CHOICE",
                "question": "What is the powerhouse of the cell?",
                "choices": ["Mitochondria", "Nucleus", "Ribosome", "Vacuole"],
                "answer": "Mitochondria"
            },
            {
                "type": "IDENTIFICATION",
                "question": "The ___ is known as the powerhouse of the cell.",
                "answer": "mitochondria"
            },
            {
                "type": "TRUE_FALSE",
                "question": "The mitochondria is the powerhouse of the cell.",
                "answer": True
            },
            {
                "type": "MATCHING",
                "question": "Match the following organelles to their functions:",
                "pairs": [
                    {"premise": "Mitochondria", "response": "Powerhouse"},
                    {"premise": "Nucleus", "response": "Stores DNA"},
                    {"premise": "Ribosome", "response": "Protein synthesis"}
                ]
            }
        ]
    },

    "RagAnswer": {
        "answer": "The mitochondria is the powerhouse of the cell and generates ATP.",
        "sources": ["Page 1: Cell Biology Introduction"]
    },

    "ParagraphEvaluation": {
        "is_correct": True,
        "is_relevant": True,
        "feedback": "Great explanation of cell respiration stages.",
        "score": 90
    }
}


class LlmService:

    def __init__(self, model: str = LLM_MODEL):

        self.model = model

        self._openai_client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        )

        threading.Thread(target=ensure_model_setup, daemon=True).start()


    def _create_completion(self, messages: list[dict], response_model: Type[T]) -> T:

        max_retries = 4

        last_exception = None


        schema_json = json.dumps(response_model.model_json_schema(), indent=2)

        model_name = response_model.__name__

        example_obj = EXAMPLES.get(model_name, {})

        example_json = json.dumps(example_obj, indent=2)


        schema_instruction = (
            f"\n\nCRITICAL: You must return a JSON object containing the actual data (do not copy the schema or definition itself), conforming strictly to this JSON Schema:\n"
            f"{schema_json}\n\n"
            f"Here is an example of a valid JSON response conforming to the schema:\n"
            f"```json\n{example_json}\n```\n"
            "Ensure you populate the JSON with actual data from the provided text/context (do not use the example values). "
            "Do not include any preambles, apologies, or conversational text. Output ONLY the raw JSON block."
        )


        history = []

        for msg in messages:

            history.append(dict(msg))


        system_msg_idx = -1

        for idx, msg in enumerate(history):

            if msg.get("role") == "system":

                system_msg_idx = idx

                break


        if system_msg_idx != -1:

            history[system_msg_idx]["content"] += schema_instruction

        else:

            history.insert(0, {"role": "system", "content": schema_instruction})


        for attempt in range(max_retries):

            raw_content = ""

            try:

                completion = self._openai_client.chat.completions.create(
                    model=self.model,
                    messages=history,
                    temperature=0.0,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": model_name,
                            "schema": response_model.model_json_schema(),
                            "strict": True
                        }
                    }
                )

                raw_content = completion.choices[0].message.content or ""

                return response_model.model_validate_json(raw_content)

            except Exception as e:

                last_exception = e

                print(f"[Attempt {attempt+1}/{max_retries}] JSON validation failed for {response_model.__name__}: {e}")
                print(f"Raw response was:\n{raw_content}\n")


                history.append({"role": "assistant", "content": raw_content})

                history.append({
                    "role": "user",
                    "content": (
                        f"Your response failed validation: {e}.\n"
                        f"Please output ONLY valid JSON matching this schema:\n{schema_json}\n"
                        f"Follow this example structure:\n{example_json}"
                    )
                })


        raise RuntimeError(f"Max retries exceeded. Total attempts: {max_retries}, Last error: {last_exception}")


    def generate_questions_for_chunk(self, chunk_text: str, preferences: str = "") -> ChunkQuizResponse:
        pref_instruction = f"\nUser preferences for quiz generation: {preferences}\nPlease adapt the questions to match these preferences." if preferences else ""

        return self._create_completion(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a quiz author. Generate 1-2 quiz questions strictly "
                        "from the provided text chunk. Do not use outside knowledge. "
                        "Use these types:\n"
                        "- MULTIPLE_CHOICE: exactly 4 choices; answer must match one choice exactly\n"
                        "- IDENTIFICATION: question contains __ for the blank\n"
                        "- ENUMERATION: ask to list items; answer is a list of expected items\n"
                        "- PARAGRAPH: open-ended question; answer is a model rubric answer\n"
                        "- TRUE_FALSE: a statement that is either true or false; answer is boolean true or false\n"
                        "- MATCHING: match premises to responses; requires 3 to 6 logical pairs\n"
                        f"{pref_instruction}"
                    ),
                },
                {"role": "user", "content": f"Text chunk:\n\n{chunk_text}"},
            ],
            response_model=ChunkQuizResponse,
        )


    def answer_question(self, question: str, context_chunks: list[str], chat_history: list[dict] | None = None) -> RagAnswer:
        context = "\n\n---\n\n".join(context_chunks)
        messages = [
            {
                "role": "system",
                "content": (
                    "Answer the user's question based primarily on the provided context (grounded-facts first). "
                    "If the provided context does not contain enough information to answer the question, "
                    "you may use your own general knowledge to generate a helpful response. Be concise."
                ),
            }
        ]
        
        if chat_history:
            messages.extend(chat_history)
            
        messages.append({"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"})
        
        return self._create_completion(
            messages=messages,
            response_model=RagAnswer,
        )


    def evaluate_paragraph_answer(
        self,
        question: str,
        model_answer: str,
        user_answer: str,
    ) -> ParagraphEvaluation:

        return self._create_completion(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Grade a student's paragraph answer. Compare against the model answer/rubric. "
                        "Determine if the answer is correct, relevant, and assign a score 0-100. "
                        "Provide constructive feedback."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Question: {question}\n\n"
                        f"Model answer/rubric:\n{model_answer}\n\n"
                        f"Student answer:\n{user_answer}"
                    ),
                },
            ],

            response_model=ParagraphEvaluation,
        )
