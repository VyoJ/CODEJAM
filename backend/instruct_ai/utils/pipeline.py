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
    - Generate questions for the student to provide detailed answer.
    - Provide a model answer for each question."""
    agent = ReActAgent.from_tools(tools, memory=memory, system_prompt=custom_prompt)
    return agent


def generate_questions(agent, topic, question_type, num_questions):
    prompt = f"""Generate {num_questions} {question_type} questions about {topic}.
    For Multiple Choice Questions (MCQs):
    - Generate questions with 4 options each (A, B, C, D).
    - Provide the correct answer for each question.
    For Subjective Questions:
    - Generate questions for the student to provide detailed answer using Bloom's Taxonomy  .
    - Bloom's Taxonomy has 6 layers which inlcudes ("Remember/Knowledge","Understand/Comprehension","Apply","Analyze","Evaluate","Create")
    - Here is what each layer means with some examples:
    - 1st Layer - "Remember/Knowledge"  - Recall facts and basic concepts (define , identify , describe , recognize , tell , explain , recite , memorize , illustrate , quote)
    - Example questions : [What is…?   Who were the main…?  Where is…?  How would you explain…? How would you know…?    ]
    - 2nd Layer - "Understand/Comprehension" - Understanding what the fact means (summarize , interpret , classify , compare , contrast , infer , relate , extract , paraphrase , cite )
    - Example questions : [What does… mean?   What is the main idea of…?    How would you summarize…?]
    - 3rd Layer - "Apply" - Use the facts to solve a problem (solve , change , relate , complete , use , sketch , teach , articulate , discover , transfer )
    - Example questions : [How would you use… to solve…?   How would you apply?   What would result if…?   Can you make use of the facts to…?]
    - 4th Layer - "Analyze" - Break down the facts into smaller parts (contrast , connect , relate , devise , correlate , illustrate , distill , conclude , categorize , take apart )
    - Example questions : [What are the similarities and differences between…?   What is the relationship between…?  What inference can you make…?]
    - 5th Layer - "Evaluate" - Make a judgment about the facts (critcize , reframe , judge , defend , appraise, value , prioritze , plan , grade , reframe)
    - Example questions : [What are the strengths and weaknesses of…?   What are the advantages?   What could be combined to improve/change…? Can you formulate a theory for…?  ] 
    - 6th Layer - "Create" - Make something new using the facts (design , modify , role-play , develop , rewrite , pivot , modify , collaborate , invent , write)
    - Example questions : [What would happen if…?   What would you do if…?  How would you prioritize…?  What judgment would you make about…?]
    - Provide a model answer for each generated question.
."""

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
