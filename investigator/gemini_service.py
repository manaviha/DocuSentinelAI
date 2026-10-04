import os
import time
from datetime import datetime

from dotenv import load_dotenv
from google import genai

from .conflict_detector import extract_dates


load_dotenv()


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_NAME = "gemini-3.8-flash"


# ============================================================
# LOCAL GROUNDED ANSWER
# ============================================================

def local_grounded_answer(query, results):

    if not results:
        return (
            "ANSWER: No relevant evidence was found.\n"
            "EVIDENCE STATUS: Insufficient Evidence"
        )

    query_lower = query.lower()

    # ========================================================
    # TRUST / AUTHORITY ASSESSMENT
    # ========================================================

    trust_keywords = [
        "which document should i trust",
        "which document can i trust",
        "which source should i trust",
        "which source can i trust",
        "which document is reliable",
        "which source is reliable",
        "which document is authoritative",
        "which source is authoritative",
        "what document should i trust",
        "what source should i trust",
    ]

    is_trust_question = any(
        keyword in query_lower
        for keyword in trust_keywords
    )

    if is_trust_question:

        documents = []

        for result in results:

            document_name = result["document"]

            if document_name not in documents:
                documents.append(document_name)

        # ----------------------------------------------------
        # Multiple sources
        # ----------------------------------------------------

        if len(documents) >= 2:

            answer_lines = [
                "TRUST ASSESSMENT:",
                "",
                "Neither document can currently be treated as "
                "authoritative based only on the retrieved evidence.",
                ""
            ]

            source_counter = 0
            already_shown = set()

            for result in results:

                document_name = result["document"]

                if document_name in already_shown:
                    continue

                already_shown.add(document_name)

                source_counter += 1

                source_label = chr(
                    64 + source_counter
                )

                answer_lines.append(
                    f"Source {source_label}: "
                    f"{document_name}"
                )

                answer_lines.append(
                    f"Evidence: {result['text']}"
                )

                answer_lines.append("")

                if source_counter >= 2:
                    break

            answer_lines.extend([
                "RECOMMENDATION:",
                "Verify the conflicting information against an "
                "official announcement, authorized record, or "
                "other authoritative source.",
                "",
                "CONFIDENCE: Uncertain",
                "",
                "REASON:",
                "Multiple retrieved documents provide conflicting "
                "information, and the available evidence does not "
                "establish which source has higher authority."
            ])

            return "\n".join(answer_lines)

        # ----------------------------------------------------
        # Only one source
        # ----------------------------------------------------

        else:

            document_name = (
                documents[0]
                if documents
                else "the available source"
            )

            return (
                "TRUST ASSESSMENT:\n\n"
                f"The available evidence comes from "
                f"{document_name}.\n\n"
                "However, the system cannot independently verify "
                "that this source is authoritative.\n\n"
                "RECOMMENDATION:\n"
                "Verify the information against an official or "
                "authoritative source.\n\n"
                "CONFIDENCE: Limited"
            )

    # ========================================================
    # DATE CONFLICT ANALYSIS
    # ========================================================

    all_dates = []

    for result in results:

        dates = extract_dates(
            result["text"]
        )

        all_dates.extend(dates)

    unique_dates = list(
        set(all_dates)
    )

    # --------------------------------------------------------
    # Multiple different dates
    # --------------------------------------------------------

    if len(unique_dates) > 1:

        date_information = []

        for result in results:

            dates = extract_dates(
                result["text"]
            )

            if dates:

                formatted_dates = ", ".join(
                    date.strftime("%d %B %Y")
                    for date in dates
                )

                date_information.append(
                    f"{result['document']} states "
                    f"{formatted_dates}."
                )

        return (
            "ANSWER: The uploaded documents contain conflicting "
            "information. "
            + " ".join(date_information)
            + "\n\n"
            "EVIDENCE STATUS: Conflicting Evidence\n"
            "REASON: Multiple retrieved documents provide "
            "different dates. The available evidence does not "
            "establish which date is authoritative."
        )

    # ========================================================
    # SINGLE CONSISTENT DATE
    # ========================================================

    if len(unique_dates) == 1:

        formatted_date = (
            unique_dates[0]
            .strftime("%d %B %Y")
        )

        return (
            f"ANSWER: The retrieved evidence indicates "
            f"{formatted_date}.\n\n"
            "EVIDENCE STATUS: Supported\n"
            "REASON: The retrieved evidence contains a "
            "consistent date."
        )

    # ========================================================
    # GENERAL GROUNDED ANSWER
    # ========================================================

    first_result = results[0]

    return (
        "ANSWER: Based on the strongest retrieved evidence:\n\n"
        f"{first_result['text']}\n\n"
        "EVIDENCE STATUS: Partially Supported\n"
        "REASON: The answer is based on retrieved document "
        "evidence, but no independent authoritative "
        "verification is available."
    )


# ============================================================
# GEMINI AI ANSWER
# ============================================================

def generate_gemini_answer(query, results):

    if not GEMINI_API_KEY:
        raise Exception(
            "GEMINI_API_KEY is not configured."
        )

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    evidence_text = []

    for index, result in enumerate(
        results,
        start=1
    ):

        evidence_text.append(
            f"""
SOURCE {index}
Document: {result['document']}
Section: {result.get('section_reference', 'Unknown')}
Page: {result.get('page_number', 'N/A')}

Evidence:
{result['text']}
"""
        )

    evidence_block = "\n".join(
        evidence_text
    )

    prompt = f"""
You are DocuSentinel AI, an intelligent document
investigation assistant.

Answer the user's question ONLY using the supplied
document evidence.

USER QUESTION:
{query}

RETRIEVED EVIDENCE:
{evidence_block}

IMPORTANT RULES:

1. Do not invent information.

2. If multiple documents contain conflicting information,
   explicitly identify the conflict.

3. Never choose one conflicting source as correct unless
   the evidence clearly establishes its authority.

4. If the evidence is insufficient, say so.

5. Communicate uncertainty clearly.

6. Mention the document names when they are relevant.

7. If the user asks which document/source should be trusted,
   assess whether the evidence establishes authority.
   If it does not, clearly recommend verification against
   an official or authoritative source.

8. Keep the answer concise and suitable for an
   investigation dashboard.

Use this structure when appropriate:

ANSWER:
...

EVIDENCE STATUS:
Supported / Conflicting Evidence / Partially Supported /
Insufficient Evidence

REASON:
...
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    if not response or not response.text:

        raise Exception(
            "Gemini returned an empty response."
        )

    return response.text.strip()


# ============================================================
# MAIN INVESTIGATION FUNCTION
# ============================================================

def generate_investigation_answer(
    query,
    results
):

    # --------------------------------------------------------
    # First attempt local handling for trust questions.
    #
    # This means the feature works even when Gemini quota
    # is exhausted.
    # --------------------------------------------------------

    query_lower = query.lower()

    trust_keywords = [
        "which document should i trust",
        "which document can i trust",
        "which source should i trust",
        "which source can i trust",
        "which document is reliable",
        "which source is reliable",
        "which document is authoritative",
        "which source is authoritative",
        "what document should i trust",
        "what source should i trust",
    ]

    is_trust_question = any(
        keyword in query_lower
        for keyword in trust_keywords
    )

    if is_trust_question:

        return local_grounded_answer(
            query,
            results
        )

    # --------------------------------------------------------
    # Try Gemini
    # --------------------------------------------------------

    try:

        return generate_gemini_answer(
            query,
            results
        )

    except Exception as error:

        error_text = str(error).lower()

        print(
            "Gemini investigation failed:",
            error
        )

        # ----------------------------------------------------
        # Free-tier quota / rate-limit fallback
        # ----------------------------------------------------

        if (
            "429" in error_text
            or "quota" in error_text
            or "resource_exhausted" in error_text
            or "rate limit" in error_text
        ):

            print(
                "Gemini quota/rate limit reached. "
                "Using local grounded fallback."
            )

        # ----------------------------------------------------
        # Temporary server error
        # ----------------------------------------------------

        elif (
            "503" in error_text
            or "unavailable" in error_text
            or "overloaded" in error_text
        ):

            print(
                "Gemini service temporarily unavailable. "
                "Using local grounded fallback."
            )

        # ----------------------------------------------------
        # Any other Gemini error
        # ----------------------------------------------------

        else:

            print(
                "Gemini unavailable. "
                "Using local grounded fallback."
            )

        return local_grounded_answer(
            query,
            results
        )