# CODEJAM - CoDMAV and people+ai Hackathon

## Team TARS

### Track

Text Analytics and Natural Language Processing (NLP)

### Domain

Generative AI for Education

### Problem Statement

A platform for college students to be able to prepare for college exams / interviews on subjects of their choice (or those curated by us such as Computer Networks, Operating Systems, etc). The platform will allow students to generate MCQs or subjective questions on topics of their choice and grade their answers and give them feedback on what to focus on for better understanding. The subjective questions will be
generated following Bloom’s Taxonomy to thoroughly test the student’s understanding.

We will also try to add code execution and interpretation to allow our agentic system to give feedback for DSA and coding questions too.

### Technology

Agentic AI system implemented powered by an open-source LLM such as Llama 3.2 8B.

#### Frameworks
- LlamaIndex for orchestration
- FastAPI for backend
- Next.js + shadcn/ui for frontend

#### Additional features
- Poetry for python environment and dependency management
- Safety/Content Moderation models like LlamaGuard or ShieldGemma to prevent misuse of the system