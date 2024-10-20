from pydantic import BaseModel, Field
from fastapi import UploadFile
from typing import List, Union, Literal, Optional, Dict , Any 
from enum import Enum

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

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class TestCase(BaseModel):
    input: Dict[str, Any]  # Changed to Dict[str, Any] to handle various input types
    expected: Any  # Changed to Any to handle various output types

class CodingQuestionRequest(BaseModel):
    programming_language: str
    difficulty: DifficultyLevel
    topic: Optional[str] = None
    num_questions: int = Field(default=1, ge=1, le=10)

class QuestionDifficulty(BaseModel):
    level: str
    explanation: Optional[str] = None

class CodingQuestion(BaseModel):
    title: str
    difficulty: QuestionDifficulty
    description: str
    function_signature: str
    test_cases: List[TestCase]
    solution: str
    time_complexity: str
    space_complexity: str
    hints: Optional[List[str]] = None
    learning_points: List[str]

    class Config:
        extra = "allow"  # Allow additional fields in the response

class CodingQuestionsResponse(BaseModel):
    questions: List[CodingQuestion]

    class Config:
        extra = "allow"  # Allow additional fields in the response

class CodingAnswerSubmission(BaseModel):
    question: Dict[str, Any]  # Changed to Dict[str, Any] to handle various question formats
    user_code: str
    programming_language: str

class TestResult(BaseModel):
    passed: bool
    input: Dict[str, Any]
    expected: Any
    actual: Any
    error: Optional[str] = None

class CodingEvaluationResponse(BaseModel):
    passed: bool
    test_results: List[TestResult]
    feedback: str
    score: float
    difficulty_appropriate: bool
    time_complexity_analysis: Optional[str] = None
    space_complexity_analysis: Optional[str] = None
    code_quality_feedback: Optional[str] = None
    improvement_suggestions: Optional[List[str]] = None

    class Config:
        extra = "allow"  # Allow additional fields in the response