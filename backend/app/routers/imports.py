from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException
)

from sqlalchemy.orm import Session

from io import BytesIO

import pandas as pd

from ..database import get_db
from ..models import Transaction, User
from ..dependencies import get_current_user
from ..ai.categorizer import predict_category

from ..ocr.pdf_ocr import (
    ocr_pdf,
    parse_statement_pages
)


router = APIRouter(
    prefix="/imports",
    tags=["Bank Statement Import"]
)


# =========================================================
# CSV IMPORT
# =========================================================

@router.post("/csv")
async def import_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # -----------------------------------------------------
    # Validate file
    # -----------------------------------------------------

    if not file.filename.lower().endswith(".csv"):

        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file."
        )

    contents = await file.read()

    if not contents:

        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    # -----------------------------------------------------
    # Read CSV
    # -----------------------------------------------------

    try:

        df = pd.read_csv(
            BytesIO(contents)
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Unable to read the CSV file."
        )

    # -----------------------------------------------------
    # Required columns
    # -----------------------------------------------------

    required_columns = {
        "date",
        "description",
        "amount",
        "type"
    }

    missing_columns = (
        required_columns -
        set(df.columns)
    )

    if missing_columns:

        raise HTTPException(
            status_code=400,
            detail=(
                "Missing required columns: "
                +
                ", ".join(
                    missing_columns
                )
            )
        )

    imported = 0
    skipped = 0
    errors = []

    # -----------------------------------------------------
    # Process rows
    # -----------------------------------------------------

    for index, row in df.iterrows():

        try:

            date_value = pd.to_datetime(
                row["date"]
            ).date()

            amount = float(
                row["amount"]
            )

            if amount <= 0:

                raise ValueError(
                    "Amount must be greater than 0."
                )

            transaction_type = str(
                row["type"]
            ).strip().lower()

            if transaction_type not in [
                "income",
                "expense"
            ]:

                raise ValueError(
                    "Type must be income or expense."
                )

            description = str(
                row["description"]
            ).strip()

            if (
                not description
                or
                description.lower() == "nan"
            ):

                description = None

            merchant = None
            payment_method = None

            # -------------------------------------------------
            # Merchant
            # -------------------------------------------------

            if "merchant" in df.columns:

                merchant_value = str(
                    row["merchant"]
                ).strip()

                if (
                    merchant_value
                    and
                    merchant_value.lower()
                    != "nan"
                ):

                    merchant = (
                        merchant_value
                    )

            # -------------------------------------------------
            # Payment method
            # -------------------------------------------------

            if "payment_method" in df.columns:

                payment_value = str(
                    row["payment_method"]
                ).strip()

                if (
                    payment_value
                    and
                    payment_value.lower()
                    != "nan"
                ):

                    payment_method = (
                        payment_value
                    )

            # -------------------------------------------------
            # AI categorization
            # -------------------------------------------------

            category = None

            if transaction_type == "expense":

                ai_text = " ".join(
                    filter(
                        None,
                        [
                            description,
                            merchant
                        ]
                    )
                )

                if ai_text:

                    ai_result = (
                        predict_category(
                            ai_text
                        )
                    )

                    category = (
                        ai_result["category"]
                    )

            # -------------------------------------------------
            # Duplicate detection
            # -------------------------------------------------

            existing = db.query(
                Transaction
            ).filter(
                Transaction.user_id ==
                current_user.id,

                Transaction.amount ==
                amount,

                Transaction.type ==
                transaction_type,

                Transaction.date ==
                date_value,

                Transaction.description ==
                description
            ).first()

            if existing:

                skipped += 1

                continue

            # -------------------------------------------------
            # Create transaction
            # -------------------------------------------------

            transaction = Transaction(
                user_id=current_user.id,
                amount=amount,
                type=transaction_type,
                description=description,
                merchant=merchant,
                category=category,
                date=date_value,
                payment_method=payment_method,
                source="csv"
            )

            db.add(transaction)

            imported += 1

        except Exception as error:

            errors.append({
                "row": index + 2,
                "error": str(error)
            })

    # -----------------------------------------------------
    # Commit
    # -----------------------------------------------------

    db.commit()

    return {
        "message": "CSV import completed.",
        "imported": imported,
        "skipped": skipped,
        "errors": errors
    }


# =========================================================
# OCR PDF IMPORT
# =========================================================

@router.post("/pdf")
async def import_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # -----------------------------------------------------
    # Validate file
    # -----------------------------------------------------

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file."
        )

    contents = await file.read()

    if not contents:

        raise HTTPException(
            status_code=400,
            detail="The uploaded PDF is empty."
        )

    # =====================================================
    # STEP 1 — OCR
    # =====================================================

    try:

        pages = ocr_pdf(
            contents
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"OCR failed: {str(error)}"
        )

    # =====================================================
    # STEP 2 — PARSE TRANSACTIONS
    # =====================================================

    try:

        transactions = (
            parse_statement_pages(
                pages
            )
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Transaction parsing failed: "
                f"{str(error)}"
            )
        )

    # -----------------------------------------------------
    # No transactions
    # -----------------------------------------------------

    if not transactions:

        return {
            "message": (
                "OCR completed, but no "
                "transactions were detected."
            ),
            "imported": 0,
            "skipped": 0,
            "errors": [],
            "transactions_detected": 0
        }

    imported = 0
    skipped = 0
    errors = []

    # =====================================================
    # STEP 3 — PROCESS TRANSACTIONS
    # =====================================================

    for index, item in enumerate(
        transactions,
        start=1
    ):

        try:

            # -------------------------------------------------
            # Extract parsed values
            # -------------------------------------------------

            date_value = item["date"]

            amount = float(
                item["amount"]
            )

            transaction_type = (
                item["type"]
            )

            description = (
                item["description"]
            )

            merchant = (
                item["merchant"]
            )

            reference_id = (
                item["reference_id"]
            )

            payment_method = (
                item["payment_method"]
            )

            # -------------------------------------------------
            # Validate amount
            # -------------------------------------------------

            if amount <= 0:

                raise ValueError(
                    "Amount must be greater than 0."
                )

            # -------------------------------------------------
            # Validate transaction type
            # -------------------------------------------------

            if transaction_type not in [
                "income",
                "expense"
            ]:

                raise ValueError(
                    "Invalid transaction type."
                )

            # =================================================
            # STEP 4 — AI CATEGORY
            # =================================================

            category = None

            if transaction_type == "expense":

                ai_text = " ".join(
                    filter(
                        None,
                        [
                            description,
                            merchant
                        ]
                    )
                )

                if ai_text:

                    ai_result = (
                        predict_category(
                            ai_text
                        )
                    )

                    category = (
                        ai_result["category"]
                    )

            # =================================================
            # STEP 5 — DUPLICATE DETECTION
            # =================================================

            existing = db.query(
                Transaction
            ).filter(
                Transaction.user_id ==
                current_user.id,

                Transaction.amount ==
                amount,

                Transaction.type ==
                transaction_type,

                Transaction.date ==
                date_value,

                Transaction.description ==
                description
            ).first()

            if existing:

                skipped += 1

                continue

            # =================================================
            # STEP 6 — SAVE TO DATABASE
            # =================================================

            transaction = Transaction(
                user_id=current_user.id,
                amount=amount,
                type=transaction_type,
                description=description,
                merchant=merchant,
                category=category,
                date=date_value,
                payment_method=payment_method,
                source="pdf",
                reference_id=reference_id
            )

            db.add(transaction)

            imported += 1

        except Exception as error:

            errors.append({
                "row": index,
                "error": str(error)
            })

    # =====================================================
    # STEP 7 — COMMIT
    # =====================================================

    try:

        db.commit()

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Database import failed: "
                f"{str(error)}"
            )
        )

    # =====================================================
    # RESPONSE
    # =====================================================

    return {
        "message": "PDF import completed.",
        "imported": imported,
        "skipped": skipped,
        "errors": errors,
        "transactions_detected": len(
            transactions
        )
    }