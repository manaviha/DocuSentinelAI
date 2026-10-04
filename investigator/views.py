from django.shortcuts import render, redirect
from django.http import JsonResponse

from .models import Document, EvidenceChunk
from .document_extractor import extract_text_from_file
from .chunker import create_chunks
from .semantic_search import SemanticSearch
from .gemini_service import generate_investigation_answer
from .conflict_detector import detect_conflicts


# ============================================================
# HOME
# ============================================================

def home(request):

    documents = Document.objects.all().order_by("-uploaded_at")

    if request.method == "POST":

        uploaded_files = request.FILES.getlist("documents")

        for uploaded_file in uploaded_files:

            document = Document.objects.create(
                title=uploaded_file.name,
                file=uploaded_file
            )

            extracted_text = extract_text_from_file(
                document.file.path
            )

            document.extracted_text = extracted_text
            document.save()

            chunks = create_chunks(
                extracted_text
            )

            for index, chunk in enumerate(
                chunks,
                start=1
            ):

                chunk_text = chunk["text"]

                section_reference = (
                    chunk.get(
                        "section",
                        "General"
                    )
                )

                source_reference = document.title

                page_number = None

                EvidenceChunk.objects.create(
                    document=document,
                    chunk_text=chunk_text,
                    chunk_number=index,
                    source_reference=source_reference,
                    page_number=page_number,
                    section_reference=section_reference
                )

        return redirect("home")

    return render(
        request,
        "investigator/home.html",
        {
            "documents": documents
        }
    )


# ============================================================
# HELPER: BUILD EVIDENCE OBJECTS
# ============================================================

def build_all_evidence(chunks):

    evidence = []

    for chunk in chunks:

        evidence.append(
            {
                "document":
                    chunk.document.title,

                "source_reference":
                    chunk.source_reference
                    or chunk.document.title,

                "section_reference":
                    chunk.section_reference
                    or (
                        f"Evidence Chunk "
                        f"{chunk.chunk_number}"
                    ),

                "page_number":
                    chunk.page_number,

                "chunk_number":
                    chunk.chunk_number,

                "text":
                    chunk.chunk_text,

                "score":
                    0.5,

                "match_score":
                    50.0,

                "match_level":
                    "Contextual"
            }
        )

    return evidence


# ============================================================
# HELPER: FIND CONFLICTING EVIDENCE
# ============================================================

def get_conflicting_evidence(all_evidence):

    all_conflicts = detect_conflicts(
        all_evidence
    )

    if not all_conflicts:

        return (
            all_evidence[:5],
            []
        )

    conflict_documents = set()

    for conflict in all_conflicts:

        conflict_documents.add(
            conflict["document_a"]
        )

        conflict_documents.add(
            conflict["document_b"]
        )

    relevant_results = []

    added_documents = set()

    for evidence in all_evidence:

        document_name = evidence["document"]

        if (
            document_name in conflict_documents
            and document_name not in added_documents
        ):

            relevant_results.append(
                evidence
            )

            added_documents.add(
                document_name
            )

    conflicts = detect_conflicts(
        relevant_results
    )

    return (
        relevant_results,
        conflicts
    )


# ============================================================
# HELPER: DETECT FOLLOW-UP QUESTIONS
# ============================================================

def detect_follow_up_type(query):

    query_lower = query.lower().strip()

    # --------------------------------------------------------
    # TRUST / AUTHORITY
    # --------------------------------------------------------

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
        "should i trust",
        "can i trust",
        "is this source reliable"
    ]

    if any(
        keyword in query_lower
        for keyword in trust_keywords
    ):
        return "trust"

    # --------------------------------------------------------
    # CONFLICT DETAILS
    # --------------------------------------------------------

    conflict_keywords = [
        "what exactly conflicts",
        "what conflicts",
        "what is conflicting",
        "what exactly is conflicting",
        "explain the conflict",
        "explain conflict",
        "show the conflict",
        "what is the conflict",
        "which information conflicts"
    ]

    if any(
        keyword in query_lower
        for keyword in conflict_keywords
    ):
        return "conflict"

    # --------------------------------------------------------
    # EVIDENCE
    # --------------------------------------------------------

    evidence_keywords = [
        "show me the evidence",
        "show the evidence",
        "show evidence",
        "evidence for this conflict",
        "evidence for the conflict",
        "what is the evidence",
        "give me the evidence",
        "supporting evidence"
    ]

    if any(
        keyword in query_lower
        for keyword in evidence_keywords
    ):
        return "evidence"

    # --------------------------------------------------------
    # AUTHORITATIVE SOURCE
    # --------------------------------------------------------

    authority_keywords = [
        "is there an authoritative source",
        "authoritative source",
        "official source",
        "official announcement",
        "is there an official source",
        "which is the official source",
        "where can i verify",
        "where should i verify"
    ]

    if any(
        keyword in query_lower
        for keyword in authority_keywords
    ):
        return "authority"

    return None


# ============================================================
# HELPER: CREATE FOLLOW-UP ANSWER
# ============================================================

def create_follow_up_answer(
    follow_up_type,
    query,
    evidence,
    conflicts
):

    # ========================================================
    # TRUST
    # ========================================================

    if follow_up_type == "trust":

        documents = []

        for item in evidence:

            document_name = item["document"]

            if document_name not in documents:

                documents.append(
                    document_name
                )

        if conflicts and len(documents) >= 2:

            lines = [
                "TRUST ASSESSMENT:",
                "",
                "Neither document can currently be "
                "treated as authoritative based only "
                "on the retrieved evidence.",
                ""
            ]

            for index, item in enumerate(
                evidence[:2],
                start=1
            ):

                lines.append(
                    f"Source {index}: "
                    f"{item['document']}"
                )

                lines.append(
                    f"Evidence: {item['text']}"
                )

                lines.append("")

            lines.extend(
                [
                    "RECOMMENDATION:",
                    "Verify the conflicting information "
                    "against an official announcement, "
                    "authorized record, or other "
                    "authoritative source.",
                    "",
                    "CONFIDENCE: Uncertain",
                    "",
                    "REASON:",
                    "Multiple retrieved documents provide "
                    "conflicting information, and the "
                    "available evidence does not establish "
                    "which source has higher authority."
                ]
            )

            return "\n".join(lines)

        return (
            "TRUST ASSESSMENT:\n\n"
            "The available evidence does not establish "
            "that any uploaded document is authoritative.\n\n"
            "RECOMMENDATION:\n"
            "Verify the information against an official "
            "or authorized source.\n\n"
            "CONFIDENCE: Limited"
        )

    # ========================================================
    # CONFLICT
    # ========================================================

    if follow_up_type == "conflict":

        if not conflicts:

            return (
                "CONFLICT ANALYSIS:\n\n"
                "No specific conflict was detected "
                "among the retrieved evidence."
            )

        lines = [
            "CONFLICT ANALYSIS:",
            ""
        ]

        for conflict in conflicts:

            lines.append(
                f"Conflict Type: "
                f"{conflict['type']}"
            )

            lines.append("")

            lines.append(
                f"Document 1: "
                f"{conflict['document_a']}"
            )

            lines.append(
                f"Evidence: "
                f"{conflict['evidence_a']}"
            )

            lines.append("")

            lines.append(
                f"Document 2: "
                f"{conflict['document_b']}"
            )

            lines.append(
                f"Evidence: "
                f"{conflict['evidence_b']}"
            )

            lines.append("")

            lines.append(
                f"Reason: "
                f"{conflict['reason']}"
            )

            lines.append("")

        lines.append(
            "CONCLUSION:"
        )

        lines.append(
            "The retrieved documents contain "
            "conflicting information. The system "
            "cannot determine which information "
            "is authoritative from the available "
            "evidence alone."
        )

        return "\n".join(lines)

    # ========================================================
    # EVIDENCE
    # ========================================================

    if follow_up_type == "evidence":

        if not evidence:

            return (
                "EVIDENCE:\n\n"
                "No supporting evidence was found."
            )

        lines = [
            "SUPPORTING EVIDENCE:",
            "",
            "The following document passages "
            "support this investigation:",
            ""
        ]

        shown_documents = set()

        for item in evidence:

            document_name = item["document"]

            if document_name in shown_documents:
                continue

            shown_documents.add(
                document_name
            )

            lines.append(
                f"Document: {document_name}"
            )

            lines.append(
                f"Section: "
                f"{item.get('section_reference', 'Unknown')}"
            )

            lines.append(
                f"Evidence: {item['text']}"
            )

            lines.append("")

        return "\n".join(lines)

    # ========================================================
    # AUTHORITATIVE SOURCE
    # ========================================================

    if follow_up_type == "authority":

        if conflicts:

            return (
                "AUTHORITATIVE SOURCE ASSESSMENT:\n\n"
                "No authoritative source was identified "
                "in the uploaded documents.\n\n"
                "The available documents contain "
                "conflicting information, so the system "
                "cannot select one document as the "
                "authoritative source.\n\n"
                "RECOMMENDATION:\n"
                "Verify the information against an official "
                "announcement, authorized record, or "
                "official project submission portal."
            )

        return (
            "AUTHORITATIVE SOURCE ASSESSMENT:\n\n"
            "No independently authoritative source was "
            "identified in the uploaded documents.\n\n"
            "RECOMMENDATION:\n"
            "Verify important information against an "
            "official or authorized source."
        )

    return None


# ============================================================
# INVESTIGATION
# ============================================================

def investigate(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "error":
                    "Only POST requests are allowed."
            },
            status=405
        )

    query = request.POST.get(
        "query",
        ""
    ).strip()

    if not query:

        return JsonResponse(
            {
                "error":
                    "Please enter an investigation question."
            },
            status=400
        )

    # ========================================================
    # LOAD ALL EVIDENCE
    # ========================================================

    chunks = list(
        EvidenceChunk.objects
        .select_related("document")
        .all()
    )

    if not chunks:

        return JsonResponse(
            {
                "error":
                    "No evidence is available. "
                    "Please upload documents first."
            },
            status=400
        )

    # ========================================================
    # DETECT FOLLOW-UP QUESTION
    # ========================================================

    follow_up_type = detect_follow_up_type(
        query
    )

    # ========================================================
    # FOLLOW-UP INVESTIGATION
    #
    # These questions should operate on the existing
    # evidence rather than attempting a fresh semantic
    # search for words such as "conflict" or "evidence".
    # ========================================================

    if follow_up_type:

        all_evidence = build_all_evidence(
            chunks
        )

        relevant_results, conflicts = (
            get_conflicting_evidence(
                all_evidence
            )
        )

        if not relevant_results:

            return JsonResponse(
                {
                    "error":
                        "No evidence is available "
                        "for this follow-up investigation."
                },
                status=404
            )

        ai_answer = create_follow_up_answer(
            follow_up_type,
            query,
            relevant_results,
            conflicts
        )

        return JsonResponse(
            {
                "query":
                    query,

                "answer":
                    ai_answer,

                "results":
                    relevant_results,

                "conflicts":
                    conflicts,

                "conflict_count":
                    len(conflicts)
            }
        )

    # ========================================================
    # NORMAL INVESTIGATION
    # ========================================================

    search_engine = SemanticSearch()

    results = search_engine.search(
        query,
        chunks,
        top_k=5
    )

    relevant_results = [
        result
        for result in results
        if result["score"] > 0
    ]

    # --------------------------------------------------------
    # No relevant evidence
    # --------------------------------------------------------

    if not relevant_results:

        return JsonResponse(
            {
                "error":
                    "No relevant evidence was found."
            },
            status=404
        )

    # ========================================================
    # NORMAL CONFLICT DETECTION
    # ========================================================

    conflicts = detect_conflicts(
        relevant_results
    )

    # ========================================================
    # GENERATE ANSWER
    # ========================================================

    try:

        ai_answer = generate_investigation_answer(
            query,
            relevant_results
        )

    except Exception as error:

        print(
            "Investigation error:",
            error
        )

        return JsonResponse(
            {
                "error":
                    "AI investigation failed.",

                "details":
                    str(error)
            },
            status=500
        )

    # ========================================================
    # RESPONSE
    # ========================================================

    return JsonResponse(
        {
            "query":
                query,

            "answer":
                ai_answer,

            "results":
                relevant_results,

            "conflicts":
                conflicts,

            "conflict_count":
                len(conflicts)
        }
    )