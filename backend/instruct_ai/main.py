from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from utils.pipeline import (
    generate_questions,
    evaluate_answer,
    load_or_create_index,
    initialize_generator_agent,
    generate_coding_question,
    evaluate_coding_answer,
)
from utils.schema import *
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import StorageContext
from pinecone import Pinecone
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

PDF_PATH = "data/SE_Merged.pdf"
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
pinecone_index = pc.Index("instructor-ai")
documents = SimpleDirectoryReader(input_files=[PDF_PATH]).load_data()
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
generator_agent = initialize_generator_agent(index)


@app.post("/generate_questions")
async def api_generate_questions(request: QuestionRequest):
    questions = generate_questions(
        generator_agent, request.topic, request.question_type, request.num_questions
    )
    return questions


@app.post("/evaluate_answer", response_model=EvaluationResponse)
async def api_evaluate_answer(submission: AnswerSubmission):
    evaluation = evaluate_answer(
        submission.question, submission.user_answer, submission.correct_answer
    )
    return evaluation


@app.post("/upload_file/")
async def upload_file(request: FileSchema = File(...)):
    if request.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    contents = await request.read()
    pdf_io = BytesIO(contents)
    return {"filename": request.course_name}


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union, Any
from enum import Enum


# Route Handlers
@app.post("/generate_coding_questions", response_model=CodingQuestionsResponse)
async def api_generate_coding_questions(request: CodingQuestionRequest):
    """
    Generate coding questions based on specified parameters.
    """
    try:
        raw_questions = generate_coding_question(
            generator_agent,
            programming_language=request.programming_language,
            difficulty=request.difficulty,
            topic=request.topic,
            num_questions=request.num_questions,
        )

        # Validate and transform the raw response
        if not isinstance(raw_questions, dict) or "questions" not in raw_questions:
            raise ValueError("Invalid response format from question generator")

        # Transform and validate each question
        validated_questions = []
        for q in raw_questions["questions"]:
            # Ensure difficulty is in the correct format
            if isinstance(q["difficulty"], str):
                q["difficulty"] = {"level": q["difficulty"], "explanation": None}
            elif isinstance(q["difficulty"], dict) and "level" not in q["difficulty"]:
                q["difficulty"] = {
                    "level": request.difficulty.value,
                    "explanation": None,
                }

            # Ensure test cases are in the correct format
            formatted_test_cases = []
            for tc in q["test_cases"]:
                if isinstance(tc, dict) and "input" in tc and "expected" in tc:
                    formatted_test_cases.append(tc)
                else:
                    # Handle malformed test cases
                    raise ValueError(f"Invalid test case format: {tc}")
            q["test_cases"] = formatted_test_cases

            # Initialize optional fields if they don't exist
            q["hints"] = q.get("hints", [])
            q["learning_points"] = q.get("learning_points", [])

            validated_questions.append(q)

        return CodingQuestionsResponse(questions=validated_questions)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate coding questions: {str(e)}"
        )


@app.post("/evaluate_coding_answer", response_model=CodingEvaluationResponse)
async def api_evaluate_coding_answer(submission: CodingAnswerSubmission):
    """
    Evaluate a submitted coding solution against test cases.
    """
    try:
        raw_evaluation = evaluate_coding_answer(
            generator_agent,
            question=submission.question,
            user_code=submission.user_code,
            programming_language=submission.programming_language,
        )

        # Transform test results into the correct format
        if isinstance(raw_evaluation.get("test_results"), list):
            formatted_test_results = []
            for result in raw_evaluation["test_results"]:
                if isinstance(result, dict):
                    test_result = TestResult(
                        passed=result.get("passed", False),
                        input=result.get("input", {}),
                        expected=result.get("expected"),
                        actual=result.get("actual"),
                        error=result.get("error"),
                    )
                    formatted_test_results.append(test_result)
            raw_evaluation["test_results"] = formatted_test_results

        return CodingEvaluationResponse(**raw_evaluation)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to evaluate coding answer: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0")
