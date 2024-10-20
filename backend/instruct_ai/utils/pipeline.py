from fastapi import HTTPException
import os
import json
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Settings,
)
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.groq import Groq
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.jinaai import JinaEmbedding
from llama_index.core.agent import ReActAgent
from utils.schema import QuestionsResponse
from dotenv import load_dotenv

load_dotenv()

PDF_PATH = "data/SE_Merged.pdf"
INDEX_PATH = "saved_index"


# llm = OpenAILike(
#     model="llama3.1",
#     api_base=os.getenv("BASE_API"),
#     api_key=os.getenv("API_KEY"),
# )
llm = Groq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))
slm = llm.as_structured_llm(output_cls=QuestionsResponse)
Settings.llm = slm
Settings.embed_model = JinaEmbedding(
    api_key=os.getenv("JINA_API_KEY"),
    model="jina-embeddings-v3",
)


def load_or_create_index():
    if os.path.exists(INDEX_PATH):
        storage_context = StorageContext.from_defaults(persist_dir=INDEX_PATH)
        index = load_index_from_storage(storage_context)
    else:
        documents = SimpleDirectoryReader(input_files=[PDF_PATH]).load_data()
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=INDEX_PATH)
    return index


def initialize_generator_agent(index):
    query_engine = index.as_query_engine(similarity_top_k=10)

    tools = [
        QueryEngineTool(
            query_engine=query_engine,
            metadata=ToolMetadata(
                name="study_material_query",
                description="Provides information from the study material PDF.",
            ),
        ),
    ]

    memory = ChatMemoryBuffer.from_defaults(token_limit=2048)
    custom_prompt = """You are a question generator designed to create questions based on study materials. Your task is to generate {question_type} questions about {topic} from the given context. Always use the study_material_query tool to gather relevant information before generating questions.
    Generate {num_questions} questions along with their correct answers.

    For Multiple Choice Questions (MCQs):
    - Generate questions with 4 options each (A, B, C, D).
    - Provide the correct answer for each question.
    For Subjective Questions:
    - Generate questions that require detailed answers.
    - Provide a model answer for each question."""
    agent = ReActAgent.from_tools(tools, memory=memory, system_prompt=custom_prompt)
    return agent


def generate_questions(agent, topic, question_type, num_questions):
    prompt = f"""Generate {num_questions} {question_type} questions about {topic}.
    For Multiple Choice Questions (MCQs):
    - Generate questions with 4 options each (A, B, C, D).
    - Provide the correct answer for each question.
    For Subjective Questions:
    - Generate questions that require detailed answers.
    - Provide a model answer for each question."""

    try:
        response = agent.chat(prompt)
        response_data = json.loads(response.response)

        # Validate the response structure
        if "questions" in response_data:
            return response_data
        else:
            raise ValueError("Invalid response structure")
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error processing response: {e}")
        return {"error": "Failed to generate questions"}


def evaluate_answer(question, user_answer, correct_answer):
    prompt = f"""Evaluate the following user answer:
Question: {question}
User Answer: {user_answer}
Correct Answer: {correct_answer}

Provide your feedback on the student response here :
"""
    response = Settings.llm.complete(prompt)
    return response.response
