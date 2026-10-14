
from pathlib import Path
from app.ocr.pdf_ocr import ocr_pdf, parse_statement_pages

pdf_path = Path(r"D:\Abhishek\Mini Project CET\bank_statement.pdf")

pages = ocr_pdf(pdf_path.read_bytes())
transactions = parse_statement_pages(pages)

print("Transactions detected:", len(transactions))

for transaction in transactions:
    print(transaction)
