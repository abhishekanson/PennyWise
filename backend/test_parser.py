from pathlib import Path

from app.ocr.pdf_ocr import (
    ocr_pdf,
    parse_statement_pages
)


pdf_path = Path("bank statement.pdf")

pdf_bytes = pdf_path.read_bytes()

print("\nStarting OCR...\n")

pages = ocr_pdf(pdf_bytes)

print(
    f"OCR completed. "
    f"Pages detected: {len(pages)}"
)

print(
    "\n========== PARSING STATEMENT ==========\n"
)

transactions = parse_statement_pages(
    pages
)

for index, transaction in enumerate(
    transactions,
    start=1
):

    print(
        f"\nTransaction {index}"
    )

    print(
        "Date:",
        transaction["date"]
    )

    print(
        "Description:",
        transaction["description"]
    )

    print(
        "Merchant:",
        transaction["merchant"]
    )

    print(
        "Reference ID:",
        transaction["reference_id"]
    )

    print(
        "Amount:",
        transaction["amount"]
    )

    print(
        "Type:",
        transaction["type"]
    )

    print(
        "Payment Method:",
        transaction["payment_method"]
    )

    print(
        "Balance:",
        transaction["balance"]
    )


print(
    f"\n\nTotal transactions detected: "
    f"{len(transactions)}"
)