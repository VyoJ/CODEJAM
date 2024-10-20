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
from llama_index.embeddings.jinaai import JinaEmbedding
from llama_index.core.agent import ReActAgent
from dotenv import load_dotenv

load_dotenv()

Settings.llm = Groq(model="llama-3.1-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
Settings.embed_model = JinaEmbedding(
    api_key=os.getenv("JINA_API_KEY"),
    model="jina-embeddings-v2-base-en",
)

PDF_PATH = "data/course_data.pdf"
INDEX_PATH = "saved_index"


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

    custom_prompt = """
        You are a question generator designed to create questions based on study materials. Your task is to generate {question_type} questions about {topic} from the given context. Always use the study_material_query tool to gather relevant information before generating questions.

        Generate {num_questions} questions along with their correct answers.

        For Multiple Choice Questions (MCQs):
        - Generate questions with 4 options each (A, B, C, D).
        - Provide the correct answer for each question.

        For Subjective Questions:
        - Generate diverse questions that require detailed answers following Bloom's Taxonomy.
        - Provide the correct content for each question.

        Bloom's Taxonomy has 6 layers which inlcudes ("Remember/Knowledge","Understand/Comprehension","Apply","Analyze","Evaluate","Create")
        Here is what each layer means with some examples:
        - 1st Layer - "Remember/Knowledge"  - Recall facts and basic concepts (define , identify , describe , recognize , tell , explain , recite , memorize , illustrate , quote)
        - Example questions will start with: [What is…?   Who were the main…?  Where is…?  How would you explain…? How would you know…?    ]
        - 2nd Layer - "Understand/Comprehension" - Understanding what the fact means (summarize , interpret , classify , compare , contrast , infer , relate , extract , paraphrase , cite )
        - Example questions will start with: [What does… mean?   What is the main idea of…?    How would you summarize…?]
        - 3rd Layer - "Apply" - Use the facts to solve a problem (solve , change , relate , complete , use , sketch , teach , articulate , discover , transfer )
        - Example questions will start with: [How would you use… to solve…?   How would you apply?   What would result if…?   Can you make use of the facts to…?]
        - 4th Layer - "Analyze" - Break down the facts into smaller parts (contrast , connect , relate , devise , correlate , illustrate , distill , conclude , categorize , take apart )
        - Example questions will start with: [What are the similarities and differences between…?   What is the relationship between…?  What inference can you make…?]
        - 5th Layer - "Evaluate" - Make a judgment about the facts (critcize , reframe , judge , defend , appraise, value , prioritze , plan , grade , reframe)
        - Example questions : [What are the strengths and weaknesses of…?   What are the advantages?   What could be combined to improve/change…? Can you formulate a theory for…?  ] 
        - 6th Layer - "Create" - Make something new using the facts (design , modify , role-play , develop , rewrite , pivot , modify , collaborate , invent , write)
        - Example questions will start with: [What would happen if…?   What would you do if…?  How would you prioritize…?  What judgment would you make about…?]

        Your response must be a valid JSON object with the following structure:
        {{
            "questions": [
                {{
                    "type": "MCQ",
                    "question": "Question text here",
                    "options": [
                        "Option A text",
                        "Option B text",
                        "Option C text",
                        "Option D text"
                    ],
                    "correct_answer": "Correct option letter"
                }},
                {{
                    "type": "Subjective",
                    "question": "Question text here",
                    "model_answer": "Model answer text here"
                }}
            ]
        }}

        Ensure that the questions are diverse and cover different parts of the topic. Use the context provided by the study_material_query tool to create accurate and relevant questions. Double-check that your response is a valid JSON object before submitting.
        """
    agent = ReActAgent.from_tools(
        tools, memory=memory, system_prompt=custom_prompt, max_iterations=15
    )
    return agent


def generate_questions(agent, topic, question_type, num_questions):
    prompt = f"""Generate {num_questions} {question_type} questions about {topic}. 
    Your response must be a valid JSON object with a 'questions' key containing an array of question objects.
    Each question object should have 'type', 'question', and either 'options' and 'correct_answer' for MCQs, or 'model_answer' for subjective questions.
    Ensure that your response is a properly formatted JSON object. Double-check the JSON structure before submitting.
    """
    response = agent.chat(prompt)

    try:
        questions_data = json.loads(response.response)
        if not isinstance(questions_data, dict) or "questions" not in questions_data:
            raise ValueError("Response is not in the expected format")
        return questions_data
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Failed to parse the generated questions. The output was not in valid JSON format.",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=500, detail=f"Error in question generation: {str(e)}"
        )


def evaluate_answer(question, user_answer, correct_answer):
    prompt = f"""Evaluate the following user answer:
Question: {question}
User Answer: {user_answer}
Correct Answer: {correct_answer}

Provide your evaluation as a valid JSON object with the following structure:
{{
    "grade": "Grade here",
    "feedback": "Feedback text here"
}}

Ensure that your response is always a valid JSON object before submitting.
"""
    response = Settings.llm.complete(prompt)

    try:
        evaluation_data = json.loads(response.text)
        if (
            not isinstance(evaluation_data, dict)
            or "grade" not in evaluation_data
            or "feedback" not in evaluation_data
        ):
            raise ValueError("Response is not in the expected format")
        return evaluation_data
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Failed to parse the evaluation. The output was not in valid JSON format.",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=500, detail=f"Error in answer evaluation: {str(e)}"
        )
