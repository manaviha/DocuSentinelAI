import re


def looks_like_heading(line):
    """
    Try to identify whether a line looks like a
    document heading or section title.
    """

    line = line.strip()

    if not line:
        return False

    # Very long lines are usually paragraphs
    if len(line) > 120:
        return False

    # Common heading patterns
    heading_patterns = [
        r"^\d+(\.\d+)*\s+.+",
        r"^[A-Z][A-Z\s]{3,}$",
        r"^(Chapter|Section|Part)\s+\w+",
        r"^(Introduction|Abstract|Conclusion|References)$",
        r"^(Project|Overview|Methodology|Results|Discussion|"
        r"System Architecture|Implementation|Requirements|"
        r"Objectives|Scope|Background|Literature Review|"
        r"Future Work|Limitations)$",
    ]

    for pattern in heading_patterns:

        if re.match(
            pattern,
            line,
            flags=re.IGNORECASE
        ):
            return True

    return False


def create_chunks(
    text,
    chunk_size=500,
    overlap=100
):

    if not text:
        return []

    # ==========================================
    # SPLIT INTO LINES
    # ==========================================

    lines = text.splitlines()

    sections = []

    current_section = "General"

    current_text = []

    # ==========================================
    # DETECT SECTIONS
    # ==========================================

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if looks_like_heading(line):

            # Save previous section
            if current_text:

                sections.append({
                    "section": current_section,
                    "text": " ".join(
                        current_text
                    )
                })

                current_text = []

            current_section = line

        else:

            current_text.append(line)

    # Save final section
    if current_text:

        sections.append({
            "section": current_section,
            "text": " ".join(
                current_text
            )
        })

    # ==========================================
    # CREATE WORD-BASED CHUNKS
    # ==========================================

    chunks = []

    for section in sections:

        words = section["text"].split()

        start = 0

        while start < len(words):

            end = start + chunk_size

            chunk_text = " ".join(
                words[start:end]
            )

            chunks.append({
                "text": chunk_text,
                "section": section["section"]
            })

            start += (
                chunk_size - overlap
            )

    return chunks