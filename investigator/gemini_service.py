import os
import time
import re

from dotenv import load_dotenv
from google import genai


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


# ============================================================
# CREATE GEMINI CLIENT
# ============================================================

client = None

if API_KEY:
    client = genai.Client(
        api_key=API_KEY
    )


# ============================================================
# LOCAL GROUNDED FALLBACK
# ============================================================

def local_grounded_answer(question, evidence):

    if not evidence:

        return """ANSWER:
Insufficient evidence in the uploaded documents.

EVIDENCE STATUS:
Insufficient Evidence

REASON:
No relevant evidence was retrieved from the uploaded documents."""


    # --------------------------------------------------------
    # Collect evidence by document
    # --------------------------------------------------------

    documents = {}

    for item in evidence:

        document_name = item["document"]

        if document_name not in documents:
            documents[document_name] = []

        documents[document_name].append(
            item["text"]
        )


    # --------------------------------------------------------
    # Detect dates inside retrieved evidence
    # --------------------------------------------------------

    date_pattern = re.compile(
        r"\b\d{1,2}\s+"
        r"(?:January|February|March|April|May|June|July|"
        r"August|September|October|November|December)"
        r"\s+\d{4}\b",
        re.IGNORECASE
    )


    document_dates = {}

    for document_name, texts in documents.items():

        combined_text = " ".join(texts)

        dates = date_pattern.findall(
            combined_text
        )

        if dates:

            document_dates[document_name] = list(
                dict.fromkeys(dates)
            )


    # ========================================================
    # CONFLICTING DATES
    # ========================================================

    all_dates = []

    for dates in document_dates.values():

        all_dates.extend(dates)


    unique_dates = list(
        dict.fromkeys(
            date.lower()
            for date in all_dates
        )
    )


    if len(unique_dates) > 1:

        answer_parts = []

        for document_name, dates in document_dates.items():

            for date in dates:

                answer_parts.append(
                    f"{document_name} states "
                    f"{date}."
                )


        answer = (
            "The uploaded documents contain conflicting "
            "information. "
            + " ".join(answer_parts)
        )


        return f"""ANSWER:
{answer}

EVIDENCE STATUS:
Conflicting Evidence

REASON:
Multiple retrieved documents provide different dates. The available evidence does not establish which date is authoritative."""


    # ========================================================
    # SINGLE DATE / SUPPORTED EVIDENCE
    # ========================================================

    if len(unique_dates) == 1:

        date_value = all_dates[0]

        supporting_documents = list(
            document_dates.keys()
        )

        answer = (
            f"The retrieved documents state "
            f"{date_value}."
        )

        if len(supporting_documents) == 1:

            reason = (
                f"The date is supported by "
                f"{supporting_documents[0]}."
            )

        else:

            reason = (
                "The same date appears in multiple "
                "retrieved documents."
            )


        return f"""ANSWER:
{answer}

EVIDENCE STATUS:
Supported

REASON:
{reason}"""


    # ========================================================
    # GENERAL EVIDENCE FALLBACK
    # ========================================================

    first_evidence = evidence[0]

    evidence_text = first_evidence["text"].strip()

    return f"""ANSWER:
The retrieved evidence states:

"{evidence_text}"

EVIDENCE STATUS:
Partially Supported

REASON:
The answer is based directly on the retrieved evidence because the AI analysis service is unavailable."""


# ============================================================
# GEMINI INVESTIGATION
# ============================================================

def generate_investigation_answer(
    question,
    evidence
):

    # --------------------------------------------------------
    # If Gemini is not configured
    # --------------------------------------------------------

    if client is None:

        print(
            "Gemini API key not configured. "
            "Using local grounded fallback."
        )

        return local_grounded_answer(
            question,
            evidence
        )


    # --------------------------------------------------------
    # BUILD EVIDENCE CONTEXT
    # --------------------------------------------------------

    evidence_text = ""

    for item in evidence:

        evidence_text += f"""
SOURCE: {item['document']}
EVIDENCE CHUNK: {item['chunk_number']}
RELEVANCE LEVEL: {item.get('match_level', 'Unknown')}
RELEVANCE SCORE: {item.get('score', 0):.3f}

{item['text']}

-------------------------
"""


    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are DocuSentinel AI, an intelligent document
investigation assistant.

Answer the user's question using ONLY the retrieved
evidence from the uploaded documents.

IMPORTANT RULES:

1. Never invent facts.

2. Never use outside knowledge.

3. If evidence is insufficient, say:

"Insufficient evidence in the uploaded documents."

4. If multiple documents disagree, identify the conflict.

5. Never silently choose one conflicting source.

6. Clearly communicate uncertainty.

7. Base every claim on the retrieved evidence.

User Question:
{question}

Retrieved Evidence:
{evidence_text}

Return exactly:

ANSWER:
<answer>

EVIDENCE STATUS:
<Supported / Partially Supported / Insufficient Evidence / Conflicting Evidence>

REASON:
<brief explanation based only on the evidence>
"""


    # ========================================================
    # GEMINI REQUEST
    # ========================================================

    max_retries = 2

    for attempt in range(1, max_retries + 1):

        try:

            print()
            print("========================================")
            print("       GEMINI INVESTIGATION REQUEST")
            print("========================================")
            print("Attempt:", attempt)
            print("Model: gemini-3.8-flash")
            print("========================================")


            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt
            )


            if not response.text:

                raise RuntimeError(
                    "Gemini returned an empty response."
                )


            print()
            print("========================================")
            print("       GEMINI INVESTIGATION SUCCESS")
            print("========================================")


            return response.text


        except Exception as error:

            error_message = str(error)

            print()
            print("========================================")
            print("        GEMINI SERVICE ERROR")
            print("========================================")
            print("Attempt:", attempt)
            print("Error Type:", type(error).__name__)
            print("Error Message:", error_message)
            print("========================================")


            # ------------------------------------------------
            # QUOTA EXHAUSTED
            # ------------------------------------------------

            if (
                "429" in error_message
                or "RESOURCE_EXHAUSTED" in error_message
                or "quota" in error_message.lower()
            ):

                print(
                    "Gemini quota exhausted."
                )

                print(
                    "Switching to local grounded fallback."
                )

                return local_grounded_answer(
                    question,
                    evidence
                )


            # ------------------------------------------------
            # TEMPORARY SERVER ERROR
            # ------------------------------------------------

            temporary_error = (
                "503" in error_message
                or "UNAVAILABLE" in error_message
                or "overloaded" in error_message.lower()
                or "high demand" in error_message.lower()
            )


            if temporary_error:

                if attempt < max_retries:

                    wait_time = attempt * 2

                    print(
                        f"Gemini temporarily unavailable."
                    )

                    print(
                        f"Retrying in {wait_time} seconds..."
                    )

                    time.sleep(wait_time)

                    continue


                return local_grounded_answer(
                    question,
                    evidence
                )


            # ------------------------------------------------
            # OTHER GEMINI ERROR
            # ------------------------------------------------

            print(
                "Unknown Gemini error."
            )

            print(
                "Switching to local grounded fallback."
            )

            return local_grounded_answer(
                question,
                evidence
            )


    # ========================================================
    # FINAL FALLBACK
    # ========================================================

    return local_grounded_answer(
        question,
        evidence
    )