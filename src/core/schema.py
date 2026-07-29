# src/core/schema.py
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class MultipleChoiceQuestion(BaseModel):

    type: Literal["MULTIPLE_CHOICE"] = "MULTIPLE_CHOICE"

    question: str

    choices: Annotated[list[str], Field(min_length=4, max_length=4)]

    answer: str


class IdentificationQuestion(BaseModel):

    type: Literal["IDENTIFICATION"] = "IDENTIFICATION"

    question: str

    answer: str


class EnumerationQuestion(BaseModel):

    type: Literal["ENUMERATION"] = "ENUMERATION"

    question: str

    answer: Annotated[list[str], Field(min_length=1, max_length=10)]


class ParagraphQuestion(BaseModel):

    type: Literal["PARAGRAPH"] = "PARAGRAPH"

    question: str

    answer: str


class TrueFalseQuestion(BaseModel):
    type: Literal["TRUE_FALSE"] = "TRUE_FALSE"
    question: str
    answer: bool


class MatchingPair(BaseModel):
    premise: str
    response: str


class MatchingQuestion(BaseModel):
    type: Literal["MATCHING"] = "MATCHING"
    question: str
    pairs: Annotated[list[MatchingPair], Field(min_length=3, max_length=6)]


QuizQuestion = Annotated[
    Union[
        MultipleChoiceQuestion,
        IdentificationQuestion,
        EnumerationQuestion,
        ParagraphQuestion,
        TrueFalseQuestion,
        MatchingQuestion,
    ],
    Field(discriminator="type"),
]


class ChunkQuizResponse(BaseModel):

    questions: Annotated[list[QuizQuestion], Field(min_length=1, max_length=2)]


class RagAnswer(BaseModel):

    answer: str

    sources: list[str] = Field(default_factory=list)


class ParagraphEvaluation(BaseModel):

    is_correct: bool

    is_relevant: bool

    feedback: str

    score: Annotated[int, Field(ge=0, le=100)]
