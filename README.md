# EduTrust AI: Trustworthy Conversational AI Student Assistant

EduTrust AI is a production-grade, trustworthy conversational AI system designed for higher education institutions. It provides context-aware academic advising, course registration guidance, policy clarification, and intelligent human handover for university students.

---

## Key Capabilities & Features

### 1. Context Awareness & Multi-Turn Memory (`memory_manager.py`)
- **Session Context Tracking**: Maintains full dialogue history across multi-turn sessions.
- **Entity Store & Extraction**: Automatically extracts and persists student profile entities:
  - Student ID, Name, Major, CGPA/GPA, Academic Year, Target Course Code, Attendance Percentage.
- **Topic Stack & Topic Switching**: Tracks active discussion topics (e.g. *Attendance Policy* -> *Course Registration*) and seamlessly handles topic returns/resumes.
- **Sliding Window + Summary Memory**: Maintains an active sliding window for recent turns while generating structured summaries for earlier overflow messages.

### 2. Responsible AI, Groundedness & Uncertainty Handling (`agent_engine.py` & `knowledge_base.py`)
- **RAG-Based Factual Groundedness**: Every answer is grounded in official university regulations, course catalogs, and student FAQs with inline source citations.
- **Confidence Estimation & Scoring (0.0 to 1.0)**: Combines TF-IDF vector similarity and query token coverage to calculate a live confidence score.
- **Transparent Admission of Missing Info**: Admits when knowledge is absent or below confidence threshold without fabricating hallucinated responses.
- **Guardrail Checks**:
  - **Academic Integrity**: Detects requests to write code, solve assignments, or cheat on exams.
  - **Self-Harm / Mental Health Crisis**: Detects distress keywords and instantly provides University Health Center and 24/7 hotline resources (+1-800-EDUTRUST-HEALTH).
  - **Toxicity & Profanity**: Enforces respectful academic discourse.

### 3. Intelligent Human Handover (`handover_manager.py`)
- **Multi-Criteria Handover Triggers**:
  - Explicit user escalation request ("connect me to an advisor").
  - High student frustration / negative sentiment threshold (> 0.60).
  - Low AI groundedness confidence (< 0.40).
  - Complex policy disputes (suspension appeals, fee waivers, debarment).
- **Auto-Generated Structured Handover Tickets**:
  - **User Issue**: High-level problem statement.
  - **Attempted Steps**: Summary of student-AI dialogue.
  - **Missing Context**: Missing student records or required documentation (e.g. medical certificates, fee receipts).
  - **Recommended Human Action**: Actionable guidance for the academic advisor.
- **Live Advisor Support Queue**: Complete dashboard for human advisors to review tickets, inspect conversation transcripts, and update ticket status.

---

## System Architecture & File Structure

```
edutrust_ai/
│
├── app.py                      # Full Streamlit Web Application (4 Multi-Tab Dashboard)
├── agent_engine.py             # Core AI Orchestrator, Guardrails, & Confidence Engine
├── memory_manager.py           # Session Context, Entity Store, Topic Stack, & Summary Memory
├── handover_manager.py         # Sentiment/Friction Analysis, Trigger Evaluation, & Ticket Queue
├── knowledge_base.py           # RAG Engine (TF-IDF Vector Search, Chunking, Groundedness)
├── requirements.txt            # Package Dependencies
├── README.md                   # Complete Documentation & Test Guide
│
└── data/
    ├── academic_regulations.json # Official University Grading, Attendance, Tuition & Exam Policies
    ├── course_catalog.json       # Detailed Course Catalog, Prerequisites, Syllabus & Credits
    └── student_faqs.txt          # Campus Life, Scholarships, Hostels, & Placement FAQs
```

---

## Installation & Running the Application

### 1. Prerequisites
Ensure Python 3.9+ is installed on your system.

### 2. Install Dependencies
```bash
cd /working_dir/c_608c0f17e2e78757/edutrust_ai/
pip install -r requirements.txt
```

### 3. Launch Streamlit Web Application
```bash
streamlit run app.py
```
The web application will open in your browser at `http://localhost:8501`.

---

## Demo Test Scenarios & Walkthrough

You can test the core capabilities using the **Quick Test Buttons** in Tab 1 or by typing the following prompts:

### Scenario A: Multi-Turn Memory & Entity Extraction
1. **Turn 1**: *"Hi, my name is Alex, student ID STU2025102. I major in Computer Science."*
   - *Result*: Extracted Student Profile in sidebar updates to `Alex`, `STU2025102`, `Computer Science`.
2. **Turn 2**: *"What is the minimum attendance requirement?"*
   - *Result*: Active Topic changes to `Attendance Policy`. EduTrust AI responds with 75% attendance rule and cites `[Academic Regulations]`.

### Scenario B: Responsible AI Guardrails (Academic Integrity)
- **Prompt**: *"Can you write my CS101 programming assignment solution code for me?"*
- *Result*: Academic Integrity Guardrail triggers immediately. EduTrust AI politely declines generated coursework and offers tutoring center options.

### Scenario C: High Sentiment Friction & Human Handover
- **Prompt**: *"This website is terrible and useless! Connect me to a real academic advisor right now!"*
- *Result*: Friction score rises, explicit escalation is detected. EduTrust AI generates an urgent **Handover Ticket** (`TICK-2026-XXXX`). Check **Tab 3 (Human Handover Portal)** to view the structured ticket summary and recommended human advisor action.

### Scenario D: Knowledge Base Ingestion & Inspection
1. Open **Tab 2 (Knowledge Base Manager)**.
2. Ingest custom text under *"Ingest Custom Document"*.
3. Test live vector retrieval with the *"Live RAG Vector Search Tester"*.

### Scenario E: Debug & AI Inspector
- Open **Tab 4 (Debug & Memory Inspector)** to view live JSON state dumps of student entities, topic stack, sliding window buffer, and raw prompt context.

---

## License & Compliance
Designed in compliance with responsible AI principles, data privacy guidelines, and academic integrity regulations for higher education institutions.
