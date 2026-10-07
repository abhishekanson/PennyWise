import io
import re
from datetime import datetime

import fitz
import pytesseract

from PIL import Image


# =========================================================
# TESSERACT CONFIGURATION
# =========================================================

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# =========================================================
# OCR PDF
# =========================================================

def ocr_pdf(pdf_bytes):
    """
    Convert every PDF page to an image and perform OCR.

    Returns OCR words with their coordinates.
    """

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    pages = []

    for page_number, page in enumerate(
        document,
        start=1
    ):

        matrix = fitz.Matrix(
            3,
            3
        )

        pix = page.get_pixmap(
            matrix=matrix,
            alpha=False
        )

        image_bytes = pix.tobytes(
            "png"
        )

        image = Image.open(
            io.BytesIO(image_bytes)
        )

        # OCR with coordinates
        data = pytesseract.image_to_data(
            image,
            output_type=pytesseract.Output.DICT,
            config="--psm 6"
        )

        words = []

        for i in range(
            len(data["text"])
        ):

            text = data["text"][i].strip()

            if not text:
                continue

            try:
                confidence = float(
                    data["conf"][i]
                )
            except (
                ValueError,
                TypeError
            ):
                confidence = 0

            words.append({
                "text": text,
                "x": int(data["left"][i]),
                "y": int(data["top"][i]),
                "width": int(data["width"][i]),
                "height": int(data["height"][i]),
                "confidence": confidence
            })

        pages.append({
            "page": page_number,
            "words": words
        })

    document.close()

    return pages


# =========================================================
# GROUP WORDS INTO ROWS
# =========================================================

def group_words_into_rows(
    words,
    y_tolerance=18
):
    """
    Group OCR words that belong to the same
    horizontal line.
    """

    sorted_words = sorted(
        words,
        key=lambda word: (
            word["y"],
            word["x"]
        )
    )

    rows = []

    for word in sorted_words:

        placed = False

        for row in rows:

            average_y = sum(
                item["y"]
                for item in row
            ) / len(row)

            if abs(
                word["y"] - average_y
            ) <= y_tolerance:

                row.append(word)

                placed = True

                break

        if not placed:

            rows.append([
                word
            ])

    for row in rows:

        row.sort(
            key=lambda word: word["x"]
        )

    rows.sort(
        key=lambda row: min(
            word["y"]
            for word in row
        )
    )

    return rows


# =========================================================
# ROW TEXT
# =========================================================

def row_text(row):

    return " ".join(
        word["text"]
        for word in row
    )


# =========================================================
# FIND STATEMENT HEADER
# =========================================================

def find_header_columns(rows):
    """
    Detect the X coordinates of:

    Date
    Transaction Reference
    Ref.No./Chq.No.
    Credit
    Debit
    Balance
    """

    columns = {
        "date": None,
        "transaction_reference": None,
        "reference_number": None,
        "credit": None,
        "debit": None,
        "balance": None
    }

    for row in rows:

        text = row_text(row).lower()

        # Header must contain multiple known keywords
        header_score = 0

        if "date" in text:
            header_score += 1

        if "transaction" in text:
            header_score += 1

        if "reference" in text:
            header_score += 1

        if "credit" in text:
            header_score += 1

        if "debit" in text:
            header_score += 1

        if "balance" in text:
            header_score += 1

        if header_score < 3:
            continue

        for word in row:

            word_text = (
                word["text"]
                .lower()
                .replace(".", "")
                .replace("/", "")
            )

            if word_text == "date":

                columns["date"] = word["x"]

            elif word_text in [
                "transaction",
                "transactions"
            ]:

                columns[
                    "transaction_reference"
                ] = word["x"]

            elif (
                "ref" in word_text
                or "chq" in word_text
            ):

                columns[
                    "reference_number"
                ] = word["x"]

            elif word_text == "credit":

                columns["credit"] = word["x"]

            elif word_text == "debit":

                columns["debit"] = word["x"]

            elif word_text == "balance":

                columns["balance"] = word["x"]

        break

    return columns


# =========================================================
# DATE PARSER
# =========================================================

def parse_date(text):

    patterns = [
        r"\b(\d{1,2})[\/\-.](\d{1,2})[\/\-.](\d{4})\b",
        r"\b(\d{1,2})[\/\-.](\d{1,2})[\/\-.](\d{2})\b"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if not match:
            continue

        day = match.group(1)
        month = match.group(2)
        year = match.group(3)

        if len(year) == 2:
            year = "20" + year

        try:

            return datetime.strptime(
                f"{day}-{month}-{year}",
                "%d-%m-%Y"
            ).date()

        except ValueError:

            return None

    return None


# =========================================================
# AMOUNT PARSER
# =========================================================

def parse_amount(text):

    if not text:
        return None

    cleaned = (
        text
        .replace(",", "")
        .replace("₹", "")
        .replace("Rs.", "")
        .replace("Rs", "")
        .replace("INR", "")
        .strip()
    )

    # Remove OCR garbage
    cleaned = re.sub(
        r"[^\d.]",
        "",
        cleaned
    )

    if not cleaned:
        return None

    try:

        return float(cleaned)

    except ValueError:

        return None


# =========================================================
# UPI REFERENCE PARSER
# =========================================================

def parse_transaction_reference(reference):
    result = {
        "party": None,
        "payment_method": None,
        "reference_id": None
    }

    if not reference:
        return result

    reference = reference.strip()

    # -----------------------------------------------------
    # Normalize OCR errors before parsing
    # -----------------------------------------------------

    # OCR may produce:
    # "_ UPI/CR/..."
    # "_ UPI/DR/..."
    #
    # Convert these to:
    # "UPI/CR/..."
    # "UPI/DR/..."

    reference = re.sub(
        r"^[^A-Za-z0-9]*UPI\s*/",
        "UPI/",
        reference,
        flags=re.IGNORECASE
    )

    parts = [
        part.strip()
        for part in reference.split("/")
    ]

    # -----------------------------------------------------
    # UPI transaction
    #
    # UPI/CR/REFERENCE/PARTY/BANK/USERNAME/UPI
    # UPI/DR/REFERENCE/PARTY/BANK/USERNAME/UPI
    # -----------------------------------------------------

    if (
        len(parts) >= 4
        and parts[0].upper() == "UPI"
        and parts[1].upper() in ["CR", "DR"]
    ):

        result["payment_method"] = "UPI"

        result["reference_id"] = parts[2].strip()

        candidate = parts[3].strip()

        if candidate not in [
            "",
            "_",
            "-",
            "—",
            "–"
        ]:
            result["party"] = candidate

        return result

    # -----------------------------------------------------
    # General fallback
    # -----------------------------------------------------

    excluded = {
        "UPI",
        "CR",
        "DR",
        "HDFC",
        "SBI",
        "SBIN",
        "ICICI",
        "AXIS",
        "CNRB",
        "YESB",
        "FDRL",
        "BKID",
        "NESF",
        "BANK"
    }

    for part in parts:

        candidate = part.strip()
        upper = candidate.upper()

        if upper in excluded:
            continue

        if upper in [
            "",
            "_",
            "-",
            "—",
            "–"
        ]:
            continue

        if re.fullmatch(
            r"\d+",
            candidate
        ):
            continue

        if len(candidate) < 3:
            continue

        result["party"] = candidate
        break

    return result

# =========================================================
# EXTRACT TRANSACTION ROW
# =========================================================

def parse_transaction_row(row, columns=None):
    """
    Parse an SBI transaction row.

    Actual OCR format:

    DATE
    TRANSACTION REFERENCE
    -
    CREDIT
    DEBIT
    BALANCE

    Example:

    04-08-26 UPI/CR/127369090408/RAHUL KR/HDFC/
    rahulkrish/UPI - 9.00 0 11.40
    """

    if not row:
        return None

    # -----------------------------------------------------
    # 1. Get complete OCR row text
    # -----------------------------------------------------

    text = row_text(row).strip()

    if not text:
        return None

    # -----------------------------------------------------
    # 2. Find date at beginning of row
    # -----------------------------------------------------

    date_match = re.match(
        r"^(\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4})\s+(.+)$",
        text
    )

    if not date_match:
        return None

    date_text = date_match.group(1)
    remaining = date_match.group(2).strip()

    date = parse_date(date_text)

    if not date:
        return None

    # -----------------------------------------------------
    # 3. Ignore non-transaction lines
    # -----------------------------------------------------

    if not (
        "/CR/" in remaining.upper()
        or "/DR/" in remaining.upper()
    ):
        return None

    # -----------------------------------------------------
    # 4. Extract credit/debit/balance from the end
    #
    # Expected:
    #
    # reference - credit debit balance
    #
    # Example:
    #
    # UPI/CR/.../UPI - 9.00 0 11.40
    # -----------------------------------------------------

    amount_pattern = (
        r"(.+?)"
        r"\s+[-=]?\s*"
        r"([\d,]+(?:\.\d{1,2})?)"
        r"\s+"
        r"([\d,]+(?:\.\d{1,2})?)"
        r"\s+"
        r"([\d,]+(?:\.\d{1,2})?)"
        r"\s*$"
    )

    amount_match = re.match(
        amount_pattern,
        remaining
    )

    if not amount_match:

        # Try OCR where separator may be missing
        amount_pattern_alt = (
            r"(.+?)"
            r"\s+"
            r"([\d,]+(?:\.\d{1,2})?)"
            r"\s+"
            r"([\d,]+(?:\.\d{1,2})?)"
            r"\s+"
            r"([\d,]+(?:\.\d{1,2})?)"
            r"\s*$"
        )

        amount_match = re.match(
            amount_pattern_alt,
            remaining
        )

    if not amount_match:
        return None

    reference = amount_match.group(1).strip()

    credit_text = amount_match.group(2)
    debit_text = amount_match.group(3)
    balance_text = amount_match.group(4)

    credit = parse_amount(credit_text)
    debit = parse_amount(debit_text)
    balance = parse_amount(balance_text)

    if credit is None or debit is None:
        return None

    # -----------------------------------------------------
    # 5. Determine transaction type
    # -----------------------------------------------------

    if debit > 0:

        amount = debit
        transaction_type = "expense"

    elif credit > 0:

        amount = credit
        transaction_type = "income"

    else:

        # No actual transaction amount
        return None

    # -----------------------------------------------------
    # 6. Parse UPI/reference information
    # -----------------------------------------------------

    reference_info = parse_transaction_reference(
        reference
    )

    payment_method = (
        reference_info["payment_method"]
    )

    party = reference_info["party"]

    parsed_reference_id = (
        reference_info["reference_id"]
    )

    # -----------------------------------------------------
    # 7. Extract reference number
    # -----------------------------------------------------

    reference_id = parsed_reference_id

    # -----------------------------------------------------
    # 8. Build description
    # -----------------------------------------------------

    description = reference

    if party:

        description = (
            f"{party} - {reference}"
        )

    # -----------------------------------------------------
    # 9. Return transaction
    # -----------------------------------------------------

    return {
        "date": date,
        "description": description,
        "merchant": party,
        "reference_id": reference_id,
        "amount": amount,
        "type": transaction_type,
        "payment_method": payment_method,
        "balance": balance
    }

# =========================================================
# PARSE COMPLETE STATEMENT
# =========================================================

def parse_statement_pages(pages):
    """
    Parse OCR pages into transactions.

    This parser does not depend on detecting
    column headers because the SBI statement
    transaction pages contain transaction rows
    in a consistent format.
    """

    transactions = []

    for page in pages:

        rows = group_words_into_rows(
            page["words"]
        )

        for row in rows:

            transaction = parse_transaction_row(
                row
            )

            if transaction:

                transactions.append(
                    transaction
                )

    return transactions