🛡️ DocuSentinel AI
Intelligent Document Investigation & Evidence Verification System

Investigate documents. Retrieve evidence. Detect conflicts. Communicate uncertainty.

DocuSentinel AI is an AI-powered document investigation platform that helps users find reliable information across multiple documents without manually reading every file.

The system allows users to upload multiple documents, extract and index their content, ask natural-language questions, retrieve supporting evidence, detect conflicting information, and communicate uncertainty when the available evidence does not support a single definitive answer.

🏆 Problem Statement
ALG-AI-02 — Intelligent Document Investigator

Information is often scattered across multiple PDFs, DOCX files, and text documents.

Users may need to manually:

Open multiple documents
Search for relevant information
Compare statements
Identify contradictions
Determine which information is reliable
Decide whether sufficient evidence exists

This process becomes difficult and time-consuming when many documents contain overlapping or contradictory information.

💡 Our Solution

DocuSentinel AI follows an evidence-first investigation approach.

Instead of simply sending a question to an AI model and accepting its answer, the system first retrieves relevant evidence from uploaded documents, analyzes that evidence for conflicts, and then generates an investigation result.

Upload Documents
       ↓
Text Extraction
       ↓
Document Chunking
       ↓
Evidence Indexing
       ↓
Natural-Language Question
       ↓
Relevant Evidence Retrieval
       ↓
Conflict Detection
       ↓
AI Investigation
       ↓
Evidence + Uncertainty Result
✨ Key Features
📂 1. Multiple Document Formats

The platform supports investigation across multiple document formats:

PDF
DOCX
TXT

Multiple documents can be uploaded and investigated together.

🔍 2. Automatic Text Extraction

Uploaded documents are automatically processed into searchable text.

PDF

Text extraction is performed using PyMuPDF.

DOCX

Text is extracted using python-docx.

TXT

Text files are processed directly using Python file handling.

🧩 3. Document Chunking

Large documents are divided into smaller evidence chunks for efficient retrieval.

The chunking system also attempts to identify meaningful section headings such as:

Introduction
Methodology
Results
Discussion
Conclusion
Requirements
System Architecture

This provides more structured evidence retrieval.

🔎 4. Evidence Retrieval

When the user asks a question, the system searches the indexed evidence chunks and retrieves the most relevant information.

The current retrieval system uses:

TF-IDF
Word n-grams
Cosine similarity
Similarity-based ranking

Retrieved evidence is assigned a match level such as:

Strong
Moderate

along with a similarity score.

💬 5. Natural-Language Investigation

Users can ask questions in normal language without knowing exact document keywords.

Example:

What is the final project submission deadline?

The system retrieves relevant evidence from the uploaded documents and generates an investigation response.

📚 6. Source-Grounded Evidence

Investigation results are accompanied by supporting evidence.

The interface displays information such as:

Source document
Section/evidence reference
Evidence chunk
Similarity score
Retrieved text

This allows users to inspect the evidence behind the result.

⚠️ 7. Conflict Detection

One of the most important features of DocuSentinel AI is its ability to identify potential conflicts between retrieved documents.

The current conflict detection layer checks for differences in:

Dates
Numerical values
Example

Document A

The final project submission deadline is
15 October 2026.

Document B

The final project submission deadline is
20 October 2026.

The system identifies:

⚠️ DATE CONFLICT DETECTED

and presents the conflicting evidence instead of silently selecting one value.

🎯 8. Uncertainty Handling

DocuSentinel AI is designed to avoid false certainty.

When conflicting evidence is found, the system communicates the uncertainty explicitly.

Example:

EVIDENCE STATUS: Conflicting Evidence

Multiple retrieved documents provide different dates.

The available evidence does not establish
which date is authoritative.

This is a key part of the system's investigation workflow.

🤖 9. AI-Assisted Investigation

Google Gemini is used to generate investigation responses based on the retrieved evidence.

The system follows:

User Question
      ↓
Relevant Evidence
      ↓
Conflict Analysis
      ↓
AI Investigation
      ↓
Grounded Response

A local evidence-based fallback is also available when the external AI service is unavailable or quota-limited.

📊 10. Evidence Assessment

The investigation interface provides an evidence assessment containing:

Number of sources retrieved
Number of evidence chunks
Conflict status
Match/similarity information
Supporting evidence

Example:

Sources Retrieved: 2
Evidence Chunks: 2
Conflict Status: Conflicts Detected
🧪 Demonstration Scenario

A strong demonstration scenario uses two documents containing contradictory information.

Document A
Project Submission Report

The final project submission deadline is
15 October 2026.
Document B
Project Submission Report

The final project submission deadline is
20 October 2026.

The user asks:

What is the final project submission deadline?

DocuSentinel AI retrieves both sources and produces an uncertainty-aware investigation result:

The uploaded documents contain conflicting information.

Document A states: 15 October 2026.

Document B states: 20 October 2026.

EVIDENCE STATUS: Conflicting Evidence

REASON:
Multiple retrieved documents provide different dates.
The available evidence does not establish which date
is authoritative.

The interface also displays the supporting evidence and conflict information.

🏗️ System Architecture
                         ┌─────────────────┐
                         │      USER       │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │   Django Web UI │
                         └────────┬────────┘
                                  │
                           Upload Documents
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │ Document Extraction     │
                    │                         │
                    │ PDF / DOCX / TXT        │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Document Chunking        │
                    │                         │
                    │ Section-aware chunks     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Evidence Indexing        │
                    │                         │
                    │ TF-IDF + Similarity      │
                    └────────────┬────────────┘
                                 │
                                 ▼
                         User Question
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Evidence Retrieval      │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
           ┌──────────────────┐      ┌──────────────────┐
           │ Conflict         │      │ Evidence         │
           │ Detection        │      │ Assessment       │
           └────────┬─────────┘      └────────┬─────────┘
                    │                         │
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │ Gemini Investigation    │
                    │ Service                 │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Investigation Result    │
                    │                         │
                    │ Answer                  │
                    │ Evidence                │
                    │ Sources                 │
                    │ Conflicts               │
                    │ Uncertainty             │
                    └─────────────────────────┘
🛠️ Technology Stack
Backend
Python
Django
Document Processing
PyMuPDF
python-docx
Python file handling
Information Retrieval
scikit-learn
TF-IDF
Cosine similarity
Word n-grams
Artificial Intelligence
Google Gemini
google-genai
Frontend
HTML
CSS
JavaScript
Database
Django ORM
SQLite for the current prototype
Development Tools
VS Code
Git
GitHub
Python Virtual Environment
📁 Project Structure
DocuSentinelAI/
│
├── docuintel/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── investigator/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── chunker.py
│   ├── conflict_detector.py
│   ├── document_extractor.py
│   ├── gemini_service.py
│   ├── models.py
│   ├── semantic_search.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── media/
│   └── documents/
│
├── manage.py
├── .gitignore
└── README.md
⚙️ Installation & Setup
1. Clone the repository
git clone https://github.com/manaviha/DocuSentinelAI.git
cd DocuSentinelAI
2. Create a virtual environment
python -m venv venv
3. Activate the virtual environment
Windows Command Prompt
venv\Scripts\activate.bat
4. Install dependencies
pip install django
pip install PyMuPDF
pip install python-docx
pip install pillow
pip install pytesseract
pip install scikit-learn
pip install -U google-genai python-dotenv
5. Configure the Gemini API

Create a .env file in the project root:

GEMINI_API_KEY=your_api_key_here

Important: Never commit your .env file or expose your API key publicly.

6. Run migrations
python manage.py migrate
7. Start the application
python manage.py runserver

Open:

http://127.0.0.1:8000/
🔐 Security

Sensitive credentials are stored using environment variables.

The following files/directories should not be committed:

.env
venv/
__pycache__/
*.pyc
db.sqlite3
media/
*.log

API keys should never be hard-coded into source files or uploaded to GitHub.

🎯 Requirement Mapping
ALG-AI-02 Requirement	DocuSentinel AI
Multiple document formats	PDF, DOCX, TXT
Extraction / indexing	Text extraction + chunking + TF-IDF retrieval
Natural-language Q&A	Investigation query interface
Source references	Source document and evidence information
Section references	Section-aware chunking and evidence references
Conflict detection	Date and numerical conflict detection
Uncertainty handling	Conflicting Evidence status and uncertainty explanation
AI assistance	Gemini-based investigation responses
Usable investigation workflow	Upload → Retrieve → Investigate → Compare → Report
🏆 Innovation

The central innovation of DocuSentinel AI is its conflict-aware evidence workflow.

A conventional AI system may behave like:

Question
   ↓
AI
   ↓
Answer

DocuSentinel AI instead follows:

Question
   ↓
Retrieve Evidence
   ↓
Compare Sources
   ↓
Detect Conflicts
   ↓
Assess Evidence
   ↓
Generate Response
   ↓
Communicate Uncertainty

If multiple sources disagree, the system does not intentionally hide the disagreement.

It exposes the conflicting evidence to the user.

Core principle

When the evidence is uncertain, the answer should communicate that uncertainty.

🎯 Judging Focus Alignment

DocuSentinel AI is designed around the key evaluation areas of the problem statement.

Answer Quality

The AI response is generated using retrieved evidence rather than relying only on general model knowledge.

Source Grounding

The interface displays the evidence and source associated with the investigation.

Conflict Handling

The system identifies conflicting dates and numerical values across retrieved documents.

Usable Investigation Workflow

The complete workflow is:

Upload
  ↓
Extract
  ↓
Index
  ↓
Ask
  ↓
Retrieve
  ↓
Detect Conflicts
  ↓
Investigate
  ↓
Review Evidence
⚠️ Current Limitations
OCR

The current implementation primarily handles text-based PDFs.

Scanned/image-only PDFs require a stronger OCR pipeline for reliable extraction.

Conflict Detection

The current conflict detector focuses mainly on detected dates and numerical values.

Complex semantic contradictions require more advanced language-level analysis.

Retrieval

The current retrieval system uses TF-IDF and cosine similarity.

Embedding-based retrieval could improve semantic matching for complex questions.

Source Authority

The system does not automatically determine whether a document is officially authoritative.

Confidence

Evidence confidence should be interpreted as an application-level assessment rather than a statistically calibrated probability.

🔮 Future Enhancements

Future versions can include:

OCR for scanned documents
Sentence-transformer embeddings
Vector database integration
Hybrid semantic + keyword retrieval
Advanced semantic conflict detection
Document version comparison
Source reliability ranking
Investigation confidence scoring
Investigation history
PDF report generation
Advanced multi-agent investigation
Improved page-level evidence mapping
🌍 Potential Applications

DocuSentinel AI can be adapted for:

🎓 Academic Research

Investigating information across research papers, reports, and academic guidelines.

🏢 Business

Comparing project documents, policies, reports, and specifications.

📋 Compliance

Investigating requirements and comparing policy documents.

📑 Document Verification

Finding inconsistent dates, numbers, and statements.

🔬 Research Investigation

Retrieving evidence from multiple documents and identifying contradictory findings.

🚀 Future Vision

DocuSentinel AI aims to evolve from a document question-answering platform into a complete AI-powered investigation assistant.

COLLECT
   ↓
EXTRACT
   ↓
INDEX
   ↓
RETRIEVE
   ↓
COMPARE
   ↓
VERIFY
   ↓
DETECT CONFLICTS
   ↓
ASSESS EVIDENCE
   ↓
INVESTIGATE
   ↓
REPORT

The long-term objective is to help users answer:

"What does the evidence actually support?"

rather than simply:

"What answer can an AI generate?"

👩‍💻 Project Information

Project: DocuSentinel AI
Problem Statement: ALG-AI-02 — Intelligent Document Investigator
Developer: Manavi H A
Repository: DocuSentinelAI

📜 License

This project is developed as a hackathon prototype for educational, research, and demonstration purposes.
