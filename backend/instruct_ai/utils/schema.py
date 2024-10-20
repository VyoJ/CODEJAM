from pydantic import BaseModel
from fastapi import UploadFile
from typing import List, Union, Literal


class QuestionRequest(BaseModel):
    topic: str
    question_type: str
    num_questions: int


class AnswerSubmission(BaseModel):
    question: str
    user_answer: str
    correct_answer: str


class EvaluationResponse(BaseModel):
    grade: str
    feedback: str


class FileSchema(BaseModel):
    course_name: str
    file: UploadFile


class MCQQuestion(BaseModel):
    type: str = Literal["MCQ"]
    question: str
    options: List[str]
    correct_answer: str


class SubjectiveQuestion(BaseModel):
    type: str = Literal["Subjective"]
    question: str
    correct_answer: str


class QuestionsResponse(BaseModel):
    questions: List[Union[MCQQuestion, SubjectiveQuestion]]
