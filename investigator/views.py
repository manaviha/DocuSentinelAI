from django.shortcuts import render, redirect
from django.http import JsonResponse

from .models import Document, EvidenceChunk
from .document_extractor import extract_text_from_file
from .chunker import create_chunks
from .semantic_search import SemanticSearch
from .gemini_service import generate_investigation_answer
from .conflict_detector import detect_conflicts


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

                # create_chunks() returns a dictionary
                # containing both text and section.
                chunk_text = chunk["text"]

                section_reference = chunk.get(
                    "section",
                    "General"
                )

                # Keep the document name as the source.
                source_reference = document.title

                # Page number is not available for TXT/DOCX
                # documents. PDF page handling can be improved
                # separately later.
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


def investigate(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "error": (
                    "Only POST requests are allowed."
                )
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
                "error": (
                    "Please enter an investigation question."
                )
            },
            status=400
        )

    chunks = list(
        EvidenceChunk.objects
        .select_related("document")
        .all()
    )

    if not chunks:

        return JsonResponse(
            {
                "error": (
                    "No evidence is available. "
                    "Please upload documents first."
                )
            },
            status=400
        )

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

    if not relevant_results:

        return JsonResponse(
            {
                "error": (
                    "No relevant evidence was found."
                )
            },
            status=404
        )

    conflicts = detect_conflicts(
        relevant_results
    )

    try:

        ai_answer = generate_investigation_answer(
            query,
            relevant_results
        )

    except Exception as error:

        print()
        print("========================================")
        print("         GEMINI INVESTIGATION ERROR")
        print("========================================")
        print(
            "Error Type:",
            type(error).__name__
        )
        print(
            "Error Message:",
            str(error)
        )
        print("========================================")
        print()

        return JsonResponse(
            {
                "error": (
                    "AI investigation failed."
                ),
                "details": str(error)
            },
            status=500
        )

    return JsonResponse(
        {
            "query": query,
            "answer": ai_answer,
            "results": relevant_results,
            "conflicts": conflicts,
            "conflict_count": len(conflicts)
        }
    )