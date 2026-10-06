from pathlib import Path

from app.ocr.pdf_ocr import ocr_pdf


pdf_path = Path(
    "bank statement.pdf"
)

pdf_bytes = pdf_path.read_bytes()

pages = ocr_pdf(
    pdf_bytes
)

for page in pages:

    print(
        f"\n===== PAGE {page['page']} ====="
    )

    for word in page["words"]:

        print(
            word["text"],
            "x=",
            word["x"],
            "y=",
            word["y"],
            "confidence=",
            word["confidence"]
        )