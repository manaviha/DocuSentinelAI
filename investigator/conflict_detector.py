import re
from itertools import combinations
from datetime import datetime


# ---------------------------------------------------------
# TEXT NORMALIZATION
# ---------------------------------------------------------

def normalize_text(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ---------------------------------------------------------
# DATE EXTRACTION
# ---------------------------------------------------------

def extract_dates(text):

    dates = []

    # Example:
    # 15 October 2026
    # 15 October, 2026
    # 15 October 26
    month_pattern = (
        r"\b("
        r"\d{1,2}"
        r"\s+"
        r"(?:january|february|march|april|may|june|july|"
        r"august|september|october|november|december)"
        r",?\s+\d{2,4}"
        r")\b"
    )

    month_matches = re.findall(
        month_pattern,
        text,
        flags=re.IGNORECASE
    )

    for value in month_matches:

        cleaned = value.replace(",", "")

        for fmt in [
            "%d %B %Y",
            "%d %B %y"
        ]:

            try:
                date_value = datetime.strptime(
                    cleaned,
                    fmt
                ).date()

                dates.append(date_value)

                break

            except ValueError:
                pass

    # Example:
    # 15/10/2026
    # 15-10-2026
    # 15.10.2026

    numeric_pattern = (
        r"\b"
        r"(\d{1,2})"
        r"[-/.]"
        r"(\d{1,2})"
        r"[-/.]"
        r"(\d{2,4})"
        r"\b"
    )

    numeric_matches = re.findall(
        numeric_pattern,
        text
    )

    for day, month, year in numeric_matches:

        try:

            if len(year) == 2:
                year = "20" + year

            date_value = datetime.strptime(
                f"{day}/{month}/{year}",
                "%d/%m/%Y"
            ).date()

            dates.append(date_value)

        except ValueError:
            pass

    return list(set(dates))


# ---------------------------------------------------------
# NUMBER EXTRACTION
# ---------------------------------------------------------

def extract_numbers(text):

    # Remove dates before extracting ordinary numbers.
    # This prevents 15, 10 and 2026 from being treated
    # as three unrelated numerical conflicts.

    text_without_dates = re.sub(
        r"\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b",
        " ",
        text
    )

    text_without_dates = re.sub(
        r"\b\d{1,2}\s+"
        r"(?:january|february|march|april|may|june|july|"
        r"august|september|october|november|december)"
        r",?\s+\d{2,4}\b",
        " ",
        text_without_dates,
        flags=re.IGNORECASE
    )

    numbers = re.findall(
        r"\b\d+(?:\.\d+)?\b",
        text_without_dates
    )

    return numbers


# ---------------------------------------------------------
# MAIN CONFLICT DETECTOR
# ---------------------------------------------------------

def detect_conflicts(results):

    conflicts = []

    if len(results) < 2:
        return conflicts

    # Compare evidence from different documents.
    for first, second in combinations(results, 2):

        if first["document"] == second["document"]:
            continue

        text1 = normalize_text(first["text"])
        text2 = normalize_text(second["text"])

        # -------------------------------------------------
        # DATE CONFLICT
        # -------------------------------------------------

        dates1 = extract_dates(text1)
        dates2 = extract_dates(text2)

        if dates1 and dates2:

            if set(dates1) != set(dates2):

                conflict = {
                    "type": "Date Conflict",
                    "document_a": first["document"],
                    "document_b": second["document"],
                    "evidence_a": first["text"],
                    "evidence_b": second["text"],
                    "reason": (
                        "The documents contain different dates "
                        "for the retrieved evidence."
                    )
                }

                conflicts.append(conflict)

                # Don't also report the same disagreement
                # as a generic numerical conflict.
                continue

        # -------------------------------------------------
        # NUMERICAL CONFLICT
        # -------------------------------------------------

        numbers1 = extract_numbers(text1)
        numbers2 = extract_numbers(text2)

        if numbers1 and numbers2:

            if set(numbers1) != set(numbers2):

                conflict = {
                    "type": "Numerical Conflict",
                    "document_a": first["document"],
                    "document_b": second["document"],
                    "evidence_a": first["text"],
                    "evidence_b": second["text"],
                    "reason": (
                        "The documents contain different "
                        "numerical values."
                    )
                }

                conflicts.append(conflict)

    # -----------------------------------------------------
    # REMOVE DUPLICATE CONFLICTS
    # -----------------------------------------------------

    unique_conflicts = []

    seen = set()

    for conflict in conflicts:

        key = (
            conflict["type"],
            tuple(
                sorted(
                    [
                        conflict["document_a"],
                        conflict["document_b"]
                    ]
                )
            )
        )

        if key not in seen:

            seen.add(key)
            unique_conflicts.append(conflict)

    return unique_conflicts