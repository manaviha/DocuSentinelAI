from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SemanticSearch:

    def search(
        self,
        query,
        chunks,
        top_k=5
    ):

        if not chunks:
            return []

        # ==========================================
        # GET CHUNK TEXT
        # ==========================================

        texts = [
            chunk.chunk_text
            for chunk in chunks
        ]

        # ==========================================
        # TF-IDF VECTOR SEARCH
        # ==========================================

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True
        )

        documents = texts + [query]

        matrix = vectorizer.fit_transform(
            documents
        )

        document_vectors = matrix[:-1]

        query_vector = matrix[-1]

        similarities = cosine_similarity(
            query_vector,
            document_vectors
        )[0]

        # ==========================================
        # RANK RESULTS
        # ==========================================

        ranked_indices = similarities.argsort()[::-1]

        results = []

        for index in ranked_indices:

            raw_score = float(
                similarities[index]
            )

            # Ignore unrelated chunks
            if raw_score < 0.15:
                continue

            chunk = chunks[index]

            # ======================================
            # MATCH LEVEL
            # ======================================

            if raw_score >= 0.30:

                match_level = "Strong"

            elif raw_score >= 0.15:

                match_level = "Moderate"

            else:

                match_level = "Weak"

            # ======================================
            # PAGE INFORMATION
            # ======================================

            page_number = chunk.page_number

            # ======================================
            # SOURCE INFORMATION
            # ======================================

            source_reference = (
                chunk.source_reference
                or chunk.document.title
            )

            # ======================================
            # SECTION INFORMATION
            # ======================================

            section_reference = (
                chunk.section_reference
                or f"Evidence Chunk {chunk.chunk_number}"
            )

            # ======================================
            # RESULT
            # ======================================

            results.append({

                "document": (
                    chunk.document.title
                ),

                "source_reference": (
                    source_reference
                ),

                "section_reference": (
                    section_reference
                ),

                "page_number": (
                    page_number
                ),

                "chunk_number": (
                    chunk.chunk_number
                ),

                "text": (
                    chunk.chunk_text
                ),

                "score": (
                    raw_score
                ),

                "match_score": min(
                    100,
                    round(
                        raw_score * 100,
                        1
                    )
                ),

                "match_level": (
                    match_level
                )
            })

            # Stop after top K
            if len(results) >= top_k:
                break

        return results