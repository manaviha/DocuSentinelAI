import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SemanticSearch:

    def _tokenize(self, text):
        """
        Convert text into simple normalized words.
        """

        text = text.lower()

        words = re.findall(
            r"[a-zA-Z0-9]+",
            text
        )

        return set(words)

    def _keyword_score(self, query, document_text):
        """
        Calculate simple keyword overlap.

        This acts as a fallback when TF-IDF similarity
        is too weak.
        """

        query_words = self._tokenize(query)
        document_words = self._tokenize(document_text)

        if not query_words or not document_words:
            return 0.0

        # Common question words that should not strongly
        # influence relevance.
        ignored_words = {
            "what",
            "is",
            "the",
            "a",
            "an",
            "are",
            "was",
            "were",
            "when",
            "where",
            "who",
            "which",
            "how",
            "does",
            "do",
            "did",
            "tell",
            "me",
            "about",
            "can",
            "you",
            "please",
            "give",
            "show",
            "of",
            "to",
            "for",
            "in",
            "on"
        }

        meaningful_query_words = (
            query_words - ignored_words
        )

        # If all words were ignored, use the original
        # query words.
        if not meaningful_query_words:
            meaningful_query_words = query_words

        overlap = (
            meaningful_query_words
            & document_words
        )

        score = (
            len(overlap)
            / len(meaningful_query_words)
        )

        return score

    def search(self, query, chunks, top_k=5):

        if not chunks:
            return []

        texts = [
            chunk.chunk_text
            for chunk in chunks
        ]

        # ========================================================
        # TF-IDF SEARCH
        # ========================================================

        tfidf_scores = [0.0] * len(chunks)

        try:

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

            tfidf_scores = [
                float(score)
                for score in similarities
            ]

        except Exception as error:

            print(
                "TF-IDF search warning:",
                error
            )

        # ========================================================
        # COMBINE TF-IDF + KEYWORD SCORE
        # ========================================================

        ranked_results = []

        for index, chunk in enumerate(chunks):

            tfidf_score = (
                tfidf_scores[index]
                if index < len(tfidf_scores)
                else 0.0
            )

            keyword_score = (
                self._keyword_score(
                    query,
                    chunk.chunk_text
                )
            )

            # TF-IDF gets more importance.
            # Keyword overlap provides additional
            # support for direct factual questions.
            combined_score = (
                (tfidf_score * 0.70)
                +
                (keyword_score * 0.30)
            )

            ranked_results.append(
                {
                    "chunk": chunk,
                    "tfidf_score": tfidf_score,
                    "keyword_score": keyword_score,
                    "combined_score": combined_score
                }
            )

        # ========================================================
        # SORT BY COMBINED RELEVANCE
        # ========================================================

        ranked_results.sort(
            key=lambda item: item["combined_score"],
            reverse=True
        )

        # ========================================================
        # BUILD FINAL RESULTS
        # ========================================================

        results = []

        for item in ranked_results:

            chunk = item["chunk"]

            tfidf_score = item["tfidf_score"]

            keyword_score = item["keyword_score"]

            combined_score = item["combined_score"]

            # ====================================================
            # IMPORTANT RELEVANCE FILTER
            # ====================================================
            #
            # Ignore evidence with combined relevance below 10%.
            #
            # This allows useful follow-up questions to retrieve
            # relevant evidence while still filtering out very
            # weak unrelated documents.
            #
            if combined_score < 0.10:
                continue

            # ====================================================
            # MATCH LEVEL
            # ====================================================

            if combined_score >= 0.40:

                match_level = "Strong"

            elif combined_score >= 0.20:

                match_level = "Moderate"

            else:

                match_level = "Weak"

            # ====================================================
            # SOURCE INFORMATION
            # ====================================================

            page_number = (
                chunk.page_number
            )

            source_reference = (
                chunk.source_reference
                or chunk.document.title
            )

            section_reference = (
                chunk.section_reference
                or
                f"Evidence Chunk {chunk.chunk_number}"
            )

            # ====================================================
            # ADD RESULT
            # ====================================================

            results.append(
                {
                    "document":
                        chunk.document.title,

                    "source_reference":
                        source_reference,

                    "section_reference":
                        section_reference,

                    "page_number":
                        page_number,

                    "chunk_number":
                        chunk.chunk_number,

                    "text":
                        chunk.chunk_text,

                    "score":
                        combined_score,

                    "match_score":
                        min(
                            100,
                            round(
                                combined_score * 100,
                                1
                            )
                        ),

                    "match_level":
                        match_level
                }
            )

            # Stop once we have enough relevant results.
            if len(results) >= top_k:
                break

        # ========================================================
        # DEBUG INFORMATION
        # ========================================================

        print(
            "\n========== DOCUMENT SEARCH =========="
        )

        print(
            "Query:",
            query
        )

        print(
            "Minimum relevance threshold: 10%"
        )

        for result in results:

            print(
                f"{result['document']} "
                f"| Score: {result['match_score']}% "
                f"| {result['match_level']}"
            )

        print(
            "Results:",
            len(results)
        )

        print(
            "====================================\n"
        )

        return results