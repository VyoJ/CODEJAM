from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from utils.pipeline import (
    generate_questions,
    evaluate_answer,
    load_or_create_index,
    initialize_generator_agent,
)
from utils.schema import (
    QuestionRequest,
    AnswerSubmission,
    EvaluationResponse,
    FileSchema,
)
from llama_index.core import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

index = load_or_create_index()
generator_agent = initialize_generator_agent(index)

faq_index = load_or_create_index()
query_engine = faq_index.as_query_engine(similarity_top_k=10)
prompt = """You are a chatbot to market an educational course called RAGs to Rich AIs with LLM Agents. It is aimed at college students.
Using the context provided below to you with the user's query, you should try to convince the student to join the course if they seem interested.
{context_str}
If they do seem interested, you can tell them to register for the course at the website pesu.io/courses.
Some general information about the course is it is part of the PESU I/O program, it costs 1000 rupees to register and will run from October 7th to November 7th.
Do not force the course on anyone and always be polite with the user.
If the user asks something which is not related to the course, respond with 'I am sorry, I can only help you with stuff regarding the course RAGs to Rich AIs'.
Query: {query_str}
Answer: """
custom_prompt = PromptTemplate(prompt)
query_engine.update_prompts({"response_synthesizer:text_qa_template": custom_prompt})


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


@app.post("/uploadfile/")
async def upload_file(request: FileSchema = File(...)):
    if request.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    contents = await request.read()
    pdf_io = BytesIO(contents)
    return {"filename": request.course_name}


@app.get("/")
async def health_check():
    return {"message": "Welcome to the instruct_ai server!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0")
