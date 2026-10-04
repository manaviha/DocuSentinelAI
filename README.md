# 🛡️ DocuSentinel AI

### Intelligent Document Investigation & Evidence Verification System

> **Investigate documents. Retrieve evidence. Detect conflicts. Communicate uncertainty.**

DocuSentinel AI is an intelligent document investigation platform that allows users to upload multiple documents, ask natural-language questions, retrieve relevant evidence, detect conflicting information, and communicate uncertainty instead of providing an unsupported confident answer.

The system is designed for scenarios where important information is distributed across multiple documents and manually comparing every document is time-consuming.

---

## 🚀 Problem

Information is often scattered across multiple documents such as PDFs, DOCX files, and text files.

Traditional document search requires users to:

* Open documents individually
* Search for relevant information
* Compare information manually
* Identify conflicting statements
* Decide which information can be trusted

This becomes difficult when many documents contain overlapping or contradictory information.

---

## 💡 Solution

DocuSentinel AI provides a unified investigation workflow:

```text
Upload Documents
       ↓
Text Extraction
       ↓
Document Chunking
       ↓
Evidence Indexing
       ↓
Natural-Language Query
       ↓
Relevant Evidence Retrieval
       ↓
Conflict Detection
       ↓
AI Investigation
       ↓
Evidence + Uncertainty Report
```

Instead of blindly returning one answer, the system identifies conflicting evidence and communicates when the available documents do not establish a reliable conclusion.

---

## ✨ Key Features

### 📂 Multiple Document Formats

Supports investigation across:

* PDF
* DOCX
* TXT

Multiple documents can be uploaded and analyzed together.

### 🔎 Evidence Extraction & Indexing

Uploaded documents are converted into searchable text and divided into smaller evidence chunks for efficient retrieval.

### 💬 Natural-Language Investigation

Users can ask questions using normal language.

Example:

```text
What is the final project submission deadline?
```

The system retrieves the most relevant evidence from the uploaded documents.

### 📚 Source-Grounded Answers

Investigation results include supporting evidence such as:

* Source document
* Evidence chunk
* Section reference
* Similarity score
* Retrieved evidence text

This allows users to verify where an answer came from.

### ⚠️ Conflict Detection

DocuSentinel AI compares retrieved evidence from different documents and detects potential conflicts.

Example:

```text
Document A → 15 October 2026

Document B → 20 October 2026

⚠️ Date Conflict Detected
```

### 🎯 Uncertainty Handling

When conflicting evidence is found, the system does not simply select one answer.

Instead, it reports:

```text
EVIDENCE STATUS: Conflicting Evidence

The available evidence does not establish
which date is authoritative.
```

This is a key feature of the system and helps prevent unsupported confident answers.

### 🤖 AI-Assisted Investigation

Gemini is used to generate grounded investigation responses from retrieved evidence.

A local evidence-based fallback is also available when the external AI service is unavailable.

### 📊 Evidence Assessment

The investigation interface provides:

* Number of retrieved sources
* Number of evidence chunks
* Conflict status
* Similarity/match information
* Supporting evidence

---

## 🧪 Example Investigation

Suppose two uploaded documents contain:

### Document A

```text
The final project submission deadline is
15 October 2026.
```

### Document B

```text
The final project submission deadline is
20 October 2026.
```

User asks:

```text
What is the final project submission deadline?
```

DocuSentinel AI identifies both pieces of evidence and produces an uncertainty-aware result:

```text
The uploaded documents contain conflicting information.

Document A states: 15 October 2026.
Document B states: 20 October 2026.

EVIDENCE STATUS:
Conflicting Evidence

The available evidence does not establish
which date is authoritative.
```

This demonstrates how the system handles contradictory evidence instead of blindly choosing one source.

---

## 🏗️ System Architecture

```text
                   ┌─────────────────────┐
                   │       User          │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │   Django Web UI     │
                   └──────────┬──────────┘
                              │
                     Upload Documents
                              │
                              ▼
              ┌─────────────────────────────┐
              │    Document Extraction      │
              │       PDF / DOCX / TXT      │
              └──────────────┬──────────────┘
                             │
                             ▼
              ┌─────────────────────────────┐
              │    Document Chunking        │
              │   Section-aware processing  │
              └──────────────┬──────────────┘
                             │
                             ▼
              ┌─────────────────────────────┐
              │    TF-IDF Evidence Index    │
              │     + Similarity Search     │
              └──────────────┬──────────────┘
                             │
                       User Question
                             │
                             ▼
              ┌─────────────────────────────┐
              │    Evidence Retrieval       │
              └──────────────┬──────────────┘
                             │
                  ┌──────────┴──────────┐
                  ▼                     ▼
        ┌─────────────────┐   ┌──────────────────┐
        │ Conflict        │   │ Gemini AI        │
        │ Detection       │   │ Investigation    │
        └────────┬────────┘   └─────────┬────────┘
                 │                      │
                 └──────────┬───────────┘
                            ▼
                 ┌─────────────────────┐
                 │ Investigation Result│
                 │ Evidence + Conflict │
                 │ + Uncertainty      │
                 └─────────────────────┘
```

---

## 🛠️ Technology Stack

### Backend

* Python
* Django

### Document Processing

* PyMuPDF
* python-docx
* Python file handling

### Information Retrieval

* scikit-learn
* TF-IDF
* Cosine similarity
* Section-aware document chunking

### AI

* Google Gemini API
* `google-genai`

### Frontend

* HTML
* CSS
* JavaScript

### Environment

* Python virtual environment
* Django development server

---

## 📁 Project Structure

```text
DocuSentinelAI/
│
├── docuintel/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── investigator/
│   ├── migrations/
│   ├── chunker.py
│   ├── conflict_detector.py
│   ├── document_extractor.py
│   ├── gemini_service.py
│   ├── models.py
│   ├── semantic_search.py
│   ├── urls.py
│   └── views.py
│
├── media/
│   └── documents/
│
├── manage.py
├── .gitignore
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/manaviha/DocuSentinelAI.git
cd DocuSentinelAI
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

#### Windows CMD

```cmd
venv\Scripts\activate.bat
```

### 4. Install dependencies

```bash
pip install django
pip install PyMuPDF
pip install python-docx
pip install pillow
pip install pytesseract
pip install scikit-learn
pip install -U google-genai python-dotenv
```

### 5. Configure the Gemini API key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

> Never commit your `.env` file or expose your API key publicly.

### 6. Run migrations

```bash
python manage.py migrate
```

### 7. Start the server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

## 🔐 Security

The project uses environment variables for sensitive API credentials.

The following files should not be committed:

```text
.env
venv/
db.sqlite3
__pycache__/
```

---

## 🎯 Hackathon Relevance

DocuSentinel AI addresses **ALG-AI-02 — Intelligent Document Investigator**.

The project focuses on:

* Multi-document investigation
* Information extraction
* Evidence retrieval
* Natural-language questions
* Source grounding
* Conflict detection
* Uncertainty communication
* Usable investigation workflow

The conflict-aware design is especially important because the system is designed to recognize when multiple documents disagree rather than confidently returning one unsupported answer.

---

## 🧠 Design Philosophy

DocuSentinel AI follows an **evidence-first investigation approach**.

Instead of:

```text
Question → AI → Answer
```

the system follows:

```text
Question
   ↓
Retrieve Evidence
   ↓
Compare Evidence
   ↓
Detect Conflicts
   ↓
Assess Support
   ↓
Generate Answer
   ↓
Communicate Uncertainty
```

This helps users understand not only **what the system found**, but also **why the result may or may not be reliable**.

---

## ⚠️ Current Limitations

* Current extraction primarily handles text-based PDFs; scanned/image-only documents require OCR integration for reliable text extraction.
* Conflict detection currently focuses mainly on detected dates and numerical values.
* Conflict detection may require additional semantic analysis for complex real-world contradictions.
* TF-IDF retrieval is lightweight and does not provide the semantic depth of large embedding-based vector databases.
* AI-generated responses depend on the availability and limits of the configured AI service.

---

## 🔮 Future Enhancements

Planned improvements include:

* Advanced semantic embeddings
* Vector database integration
* OCR for scanned documents
* More sophisticated semantic conflict detection
* Document version comparison
* Source reliability ranking
* Investigation confidence scoring
* Automatic investigation report generation
* Advanced document relationship analysis
* Improved PDF page-level evidence mapping

---

## 🏆 Expected Impact

DocuSentinel AI can assist users in scenarios where decisions depend on information distributed across multiple documents.

Potential applications include:

* Academic document investigation
* Policy and guideline comparison
* Compliance document analysis
* Project documentation
* Business reports
* Research document investigation
* Contract and agreement review
* Administrative document verification

---

## 👩‍💻 Team

**Project:** DocuSentinel AI
**Problem Statement:** ALG-AI-02 — Intelligent Document Investigator
**Repository:** https://github.com/manaviha/DocuSentinelAI

---

## 📜 License

This project is developed as a hackathon prototype for educational and demonstration purposes.
