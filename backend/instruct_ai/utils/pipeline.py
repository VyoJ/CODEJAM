from fastapi import HTTPException
import os
import json
from fastapi import HTTPException
from typing import Dict, List, Optional, Literal, Union
from enum import Enum
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
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
    model="jina-embeddings-v3",
)

PDF_PATH = "data/SE_Merged.pdf"
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
                    "model_answer": "Correct option letter"
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
    Each question object should have 'type', 'question', and either 'options' and 'model_answer' for MCQs, or 'model_answer' for subjective questions.
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


class TestCase(TypedDict):
    input: Union[List, Dict, str, int, float]
    expected: Union[List, Dict, str, int, float]


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class DifficultyParameters(BaseModel):
    time_complexity: List[str]
    typical_concepts: List[str]
    expected_time: str
    constraints: Dict[str, str]


def get_difficulty_parameters(difficulty: DifficultyLevel) -> DifficultyParameters:
    """
    Returns parameter guidelines based on difficulty level.
    """
    difficulty_params = {
        DifficultyLevel.EASY: DifficultyParameters(
            time_complexity=["O(1)", "O(n)"],
            typical_concepts=[
                "Basic array operations",
                "Simple string manipulation",
                "Basic math operations",
                "If-else conditions",
                "Basic loops",
            ],
            expected_time="10-15 minutes",
            constraints={
                "input_size": "n ≤ 1000",
                "time_limit": "1 second",
                "space_complexity": "O(1) to O(n)",
            },
        ),
        DifficultyLevel.MEDIUM: DifficultyParameters(
            time_complexity=["O(n)", "O(n log n)"],
            typical_concepts=[
                "Two pointers",
                "Hash tables",
                "Binary search",
                "Basic graph algorithms",
                "Basic dynamic programming",
            ],
            expected_time="20-30 minutes",
            constraints={
                "input_size": "n ≤ 10^5",
                "time_limit": "2 seconds",
                "space_complexity": "O(n)",
            },
        ),
        DifficultyLevel.HARD: DifficultyParameters(
            time_complexity=["O(n log n)", "O(n^2)", "O(2^n)"],
            typical_concepts=[
                "Advanced dynamic programming",
                "Complex graph algorithms",
                "Tree algorithms",
                "Advanced data structures",
                "Mathematical algorithms",
            ],
            expected_time="30-45 minutes",
            constraints={
                "input_size": "n ≤ 10^6",
                "time_limit": "3 seconds",
                "space_complexity": "Problem specific",
            },
        ),
    }
    return difficulty_params[difficulty]


def validate_programming_language(language: str) -> str:
    """
    Validates and normalizes programming language input.
    """
    supported_languages = {
        "python": "Python",
        "javascript": "JavaScript",
        "java": "Java",
        "cpp": "C++",
        "c++": "C++",
        "c": "C",
        "csharp": "C#",
        "c#": "C#",
    }
    normalized = language.lower().strip()
    if normalized not in supported_languages:
        raise ValueError(f"Unsupported programming language: {language}")
    return supported_languages[normalized]


# def generate_coding_question(
#     agent,
#     programming_language: str,
#     difficulty: DifficultyLevel,
#     topic: Optional[str] = None,
#     num_questions: int = 1,
# ) -> Dict:
#     """
#     Generate coding questions with test cases and solution templates.

#     Args:
#         agent: The LLM agent to use for generation
#         programming_language: Target programming language
#         difficulty: DifficultyLevel (easy/medium/hard)
#         topic: Specific programming topic (optional)
#         num_questions: Number of questions to generate (default: 1)

#     Returns:
#         Dict containing generated questions with test cases

#     Raises:
#         HTTPException: If question generation or parsing fails
#         ValueError: If input parameters are invalid
#     """
#     try:
#         # Input validation
#         if num_questions < 1 or num_questions > 10:
#             raise ValueError("Number of questions must be between 1 and 10")

#         programming_language = validate_programming_language(programming_language)
#         difficulty_params = get_difficulty_parameters(difficulty)
#         topic_prompt = f"about {topic}" if topic else ""

#         prompt = f"""Generate {num_questions} {difficulty.value} coding {topic_prompt} questions in {programming_language}.
#         The questions should align with the following difficulty parameters:
#         - Time Complexity Target: {', '.join(difficulty_params.time_complexity)}
#         - Typical Concepts: {', '.join(difficulty_params.typical_concepts)}
#         - Expected Solving Time: {difficulty_params.expected_time}
#         - Constraints: {json.dumps(difficulty_params.constraints, indent=2)}

#         Your response must be a valid JSON object with a 'questions' key containing an array of question objects.
#         Each question object should have:
#         - 'title': A short descriptive title
#         - 'difficulty': The difficulty level with explanation
#         - 'description': Detailed problem description including constraints and examples
#         - 'function_signature': The required function signature/template
#         - 'test_cases': Array of test cases with input and expected output
#         - 'solution': A sample solution
#         - 'time_complexity': Expected time complexity
#         - 'space_complexity': Expected space complexity
#         - 'hints': Array of helpful hints (optional)
#         - 'learning_points': Key concepts and patterns used in the solution

#         Use appropriate syntax and conventions for {programming_language}.
#         Include comprehensive test cases covering edge cases.
#         """

#         try:
#             response = agent.chat(prompt)
#         except Exception as e:
#             raise HTTPException(
#                 status_code=500, detail=f"Failed to generate questions: {str(e)}"
#             )

#         try:
#             questions_data = json.loads(response.response)
#         except json.JSONDecodeError:
#             raise HTTPException(
#                 status_code=500,
#                 detail="Failed to parse the generated questions. Invalid JSON format.",
#             )

#         # Validate response structure
#         if not isinstance(questions_data, dict) or "questions" not in questions_data:
#             raise ValueError("Response is missing required 'questions' field")

#         # Validate each question
#         for question in questions_data["questions"]:
#             required_fields = [
#                 "title",
#                 "difficulty",
#                 "description",
#                 "function_signature",
#                 "test_cases",
#                 "solution",
#                 "time_complexity",
#                 "space_complexity",
#             ]
#             missing_fields = [
#                 field for field in required_fields if field not in question
#             ]
#             if missing_fields:
#                 raise ValueError(
#                     f"Question missing required fields: {', '.join(missing_fields)}"
#                 )

#             # if question["difficulty"]["level"] != difficulty.value:
#             #     raise ValueError(
#             #         f"Question difficulty '{question['difficulty']['level']}' "
#             #         f"does not match requested level: {difficulty.value}"
#             #     )

#         return questions_data

#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


def generate_coding_question(
    agent,
    programming_language: str,
    difficulty: DifficultyLevel,
    topic: Optional[str] = None,
    num_questions: int = 1,
) -> Dict:
    try:
        if num_questions < 1 or num_questions > 10:
            raise ValueError("Number of questions must be between 1 and 10")

        programming_language = validate_programming_language(programming_language)
        difficulty_params = get_difficulty_parameters(difficulty)
        topic_prompt = f"about {topic}" if topic else ""

        # Create a sample test case structure
        sample_test_case = {
            "input": {"nums": [1, 2, 3, 4, 5], "target": 9},
            "expected": [3, 4],
        }

        # Create a sample question structure
        sample_question = {
            "title": "Example: Find Target Sum Pair",
            "difficulty": {
                "level": "easy",
                "explanation": "Basic array traversal with nested loops",
            },
            "description": "Example description",
            "function_signature": "def find_pair(nums: List[int], target: int) -> List[int]:",
            "test_cases": [sample_test_case],
            "solution": "Example solution",
            "time_complexity": "O(n^2)",
            "space_complexity": "O(1)",
            "hints": ["Consider using nested loops"],
            "learning_points": ["Array traversal", "Brute force approach"],
        }

        prompt = f"""Generate {num_questions} {difficulty.value} coding {topic_prompt} questions in {programming_language}.
        The questions should align with the following difficulty parameters:
        - Time Complexity Target: {', '.join(difficulty_params.time_complexity)}
        - Typical Concepts: {', '.join(difficulty_params.typical_concepts)}
        - Expected Solving Time: {difficulty_params.expected_time}
        - Constraints: {json.dumps(difficulty_params.constraints, indent=2)}

        Your response must follow this exact JSON structure (using the example format below):

        {json.dumps({"questions": [sample_question]}, indent=2)}

        IMPORTANT REQUIREMENTS:
        1. Each question must follow the exact structure shown above
        2. All test cases must have 'input' as an object with named parameters
        3. The 'expected' field in test cases must match the function's return type
        4. Include at least 3 test cases per question, including edge cases
        5. The function signature must match the programming language syntax
        6. All JSON must be valid and properly formatted

        Use appropriate syntax and conventions for {programming_language}.
        Ensure all test cases are properly formatted as objects with named parameters.
        """

        try:
            response = agent.chat(prompt)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to generate questions: {str(e)}"
            )

        try:
            questions_data = json.loads(response.response)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse the generated questions. Invalid JSON format. Error: {str(e)}",
            )

        # Validate response structure
        if not isinstance(questions_data, dict) or "questions" not in questions_data:
            raise ValueError("Response is missing required 'questions' field")

        # Validate and clean each question
        for i, question in enumerate(questions_data["questions"]):
            # Check required fields
            required_fields = [
                "title",
                "difficulty",
                "description",
                "function_signature",
                "test_cases",
                "solution",
                "time_complexity",
                "space_complexity",
            ]
            missing_fields = [
                field for field in required_fields if field not in question
            ]
            if missing_fields:
                raise ValueError(
                    f"Question {i+1} missing required fields: {', '.join(missing_fields)}"
                )

            # Validate test cases
            if not isinstance(question["test_cases"], list):
                raise ValueError(f"Question {i+1}: Test cases must be an array")

            cleaned_test_cases = []
            for j, test_case in enumerate(question["test_cases"]):
                if not isinstance(test_case, dict):
                    raise ValueError(
                        f"Question {i+1}, Test case {j+1}: Must be an object"
                    )

                if "input" not in test_case or "expected" not in test_case:
                    raise ValueError(
                        f"Question {i+1}, Test case {j+1}: Must have 'input' and 'expected' fields"
                    )

                # Ensure input is a dictionary
                if not isinstance(test_case["input"], dict):
                    raise ValueError(
                        f"Question {i+1}, Test case {j+1}: Input must be an object with named parameters"
                    )

                # Add cleaned test case
                cleaned_test_cases.append(
                    {"input": test_case["input"], "expected": test_case["expected"]}
                )

            # Replace test cases with cleaned version
            question["test_cases"] = cleaned_test_cases

            # Validate difficulty format
            if (
                not isinstance(question["difficulty"], dict)
                or "level" not in question["difficulty"]
            ):
                raise ValueError(
                    f"Question {i+1}: Difficulty must be an object with a 'level' field"
                )

        return questions_data

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


def evaluate_coding_answer(
    agent, question: Dict, user_code: str, programming_language: str
) -> Dict:
    """
    Evaluate a user's coding answer against test cases and provide feedback.

    Args:
        agent: The LLM agent to use for evaluation
        question: The original question dictionary containing test cases
        user_code: The user's submitted code
        programming_language: The programming language of the solution

    Returns:
        Dict containing evaluation results and feedback

    Raises:
        HTTPException: If evaluation fails
        ValueError: If input parameters are invalid
    """
    try:
        # Input validation
        if not user_code.strip():
            raise ValueError("User code cannot be empty")

        programming_language = validate_programming_language(programming_language)

        # Validate question structure
        required_fields = [
            "difficulty",
            "description",
            "function_signature",
            "test_cases",
        ]
        missing_fields = [field for field in required_fields if field not in question]
        if missing_fields:
            raise ValueError(
                f"Question missing required fields: {', '.join(missing_fields)}"
            )

        difficulty_params = get_difficulty_parameters(
            DifficultyLevel(question["difficulty"]["level"])
        )

        prompt = f"""Evaluate the following coding solution:
Programming Language: {programming_language}

Question:
{question['description']}

Difficulty Level: {question['difficulty']['level']}
Expected Time Complexity: {question.get('time_complexity', 'Not specified')}
Expected Space Complexity: {question.get('space_complexity', 'Not specified')}

Expected Function Signature:
{question['function_signature']}

User's Solution:
{user_code}

Test Cases:
{json.dumps(question['test_cases'], indent=2)}

Difficulty Parameters:
{json.dumps(difficulty_params.dict(), indent=2)}

Provide a comprehensive evaluation including:
1. Test case results
2. Time and space complexity analysis
3. Code style and best practices
4. Error handling
5. Edge cases coverage
6. Language-specific feedback

Return the evaluation as a valid JSON object.
"""

        try:
            response = agent.chat(prompt)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to evaluate answer: {str(e)}"
            )

        try:
            evaluation_data = json.loads(response.response)
            print(evaluation_data)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500,
                detail="Failed to parse evaluation results. Invalid JSON format.",
            )

        # Validate evaluation data
        required_fields = [
            "passed",
            "test_results",
            "feedback",
            "score",
            "difficulty_appropriate",
        ]
        missing_fields = [
            field for field in required_fields if field not in evaluation_data
        ]
        if missing_fields:
            raise ValueError(
                f"Evaluation missing required fields: {', '.join(missing_fields)}"
            )

        return evaluation_data

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
