
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


# =========================================================
# TRAINING DATA
# =========================================================

training_data = [
    # Food
    ("swiggy food order", "Food"),
    ("zomato restaurant", "Food"),
    ("pizza burger", "Food"),
    ("biryani", "Food"),
    ("lunch dinner", "Food"),
    ("breakfast", "Food"),
    ("restaurant bill", "Food"),
    ("coffee", "Food"),
    ("groceries", "Food"),
    ("supermarket food", "Food"),
    ("food delivery", "Food"),
    ("cafe payment", "Food"),

    # Transport
    ("uber ride", "Transport"),
    ("ola cab", "Transport"),
    ("taxi", "Transport"),
    ("bus ticket", "Transport"),
    ("metro ticket", "Transport"),
    ("petrol", "Transport"),
    ("fuel", "Transport"),
    ("auto rickshaw", "Transport"),
    ("parking fee", "Transport"),
    ("train ticket", "Transport"),

    # Shopping
    ("amazon purchase", "Shopping"),
    ("flipkart order", "Shopping"),
    ("clothes", "Shopping"),
    ("shoes", "Shopping"),
    ("electronics", "Shopping"),
    ("shopping mall", "Shopping"),
    ("online shopping", "Shopping"),
    ("watch purchase", "Shopping"),

    # Bills
    ("electricity bill", "Bills"),
    ("water bill", "Bills"),
    ("internet bill", "Bills"),
    ("mobile recharge", "Bills"),
    ("phone bill", "Bills"),
    ("wifi bill", "Bills"),
    ("rent payment", "Bills"),

    # Entertainment
    ("movie ticket", "Entertainment"),
    ("netflix subscription", "Entertainment"),
    ("spotify subscription", "Entertainment"),
    ("concert ticket", "Entertainment"),
    ("gaming", "Entertainment"),
    ("playstation", "Entertainment"),
    ("cinema", "Entertainment"),

    # Education
    ("college fee", "Education"),
    ("university fee", "Education"),
    ("course fee", "Education"),
    ("books", "Education"),
    ("notebook", "Education"),
    ("exam fee", "Education"),
    ("online course", "Education"),

    # Health
    ("hospital bill", "Health"),
    ("doctor consultation", "Health"),
    ("medicine", "Health"),
    ("pharmacy", "Health"),
    ("medical test", "Health"),
    ("health checkup", "Health"),

    # Travel
    ("hotel booking", "Travel"),
    ("flight ticket", "Travel"),
    ("trip", "Travel"),
    ("vacation", "Travel"),
    ("travel booking", "Travel"),
    ("tour package", "Travel"),

    # Transfers
    ("p2p transfer", "Transfers"),
    ("upi p2p payment", "Transfers"),
    ("person to person transfer", "Transfers"),
    ("money sent to friend", "Transfers"),
    ("money sent to person", "Transfers"),
    ("fund transfer", "Transfers"),
    ("bank transfer", "Transfers"),
    ("transfer to another account", "Transfers"),
    ("imps transfer", "Transfers"),
    ("neft transfer", "Transfers"),
    ("rtgs transfer", "Transfers"),
    ("sent money", "Transfers"),
    ("self account transfer", "Transfers"),

    # Other
    ("gift", "Other"),
    ("donation", "Other"),
    ("miscellaneous expense", "Other"),
    ("other payment", "Other"),
]


training_texts = [item[0] for item in training_data]
training_categories = [item[1] for item in training_data]

vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2),
)

X = vectorizer.fit_transform(training_texts)

model = LogisticRegression(max_iter=1000)
model.fit(X, training_categories)


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_text(text: str) -> str:
    """Normalize narration text for reliable rule matching."""

    text = (text or "").lower()
    text = re.sub(r"[_\-]+", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =========================================================
# EXPLICIT TRANSFER DETECTION
# =========================================================

TRANSFER_PATTERNS = [
    r"\bp2p\b",
    r"\bperson\s+to\s+person\b",
    r"\bpeer\s+to\s+peer\b",
    r"\bfund\s+transfer\b",
    r"\bbank\s+transfer\b",
    r"\baccount\s+transfer\b",
    r"\bself\s+transfer\b",
    r"\bself\s+account\b",
    r"\bmoney\s+sent\b",
    r"\bsent\s+money\b",
    r"\btransfer\s+to\b",
    r"\bupi\s*/?\s*p2p\b",
]



def is_transfer(text: str) -> bool:
    """Detect explicit P2P transfers and common bank transfer narrations."""

    normalized = normalize_text(text)

    if not normalized:
        return False

    # Explicit transfer wording
    if any(
        re.search(pattern, normalized)
        for pattern in TRANSFER_PATTERNS
    ):
        return True

    # UPI P2P narration with CR (credit) or DR (debit)
    if re.search(
        r"\bupi\s*/\s*(?:cr|dr)\s*/",
        normalized,
    ):
        return True

    # Common explicit P2P narration formats
    if re.search(
        r"\bp2p\b|person\s+to\s+person|peer\s+to\s+peer|"
        r"upi\s+p2p",
        normalized,
    ):
        return True

    return False



# =========================================================
# BANK NARRATION RULES
# =========================================================

def detect_bank_category(text: str):
    """
    Return (category, confidence) for recognizable bank narrations.
    Return None when no reliable rule matches.
    """

    normalized = normalize_text(text)

    if not normalized:
        return None

    # ATM and cash withdrawals
    if re.search(
        r"\batm\b|cash\s*withdrawal|cash\s*wdl\b|"
        r"withdrawal\s+by\s+cash|cash\s+withdrawal",
        normalized,
    ):
        return ("Cash Withdrawal", 100.0)

    # Cash deposits are not automatically treated as new income.
    if re.search(
        r"cash\s+deposit|cash\s+dep\b"
        r"\bdeposit\s+by\s+cash\b",
        normalized,
    ):
        return ("Cash Deposit", 100.0)

    # Bank fees and service charges.
    if re.search(
        r"bank\s+charges|service\s+charge|"
        r" sms\s+charge|annual\s+fee|"
        r"debit\s+card\s+fee",
        normalized,
    ):
        return ("Bank Charges", 100.0)

    # Salary/payroll credits.
    if re.search(
        r"\bsalary\b|\bpayroll\b|salary\s+credit",
        normalized,
    ):
        return ("Salary", 100.0)

    # Explicitly identified transfers.
    if is_transfer(normalized):
        return ("Transfers", 100.0)

    return None

def is_cash_deposit(text):
    text = str(text or "").upper()

    return bool(
        re.search(r"\bDEPOSIT\b|\bCDM\b", text)
    )


# =========================================================
# CATEGORY PREDICTION
# =========================================================

def predict_category(text: str):
    """
    Apply reliable bank rules first, then use the ML model.

    The ML model is a fallback, not a guarantee that every
    bank narration has been classified correctly.
    """

    if not text or not text.strip():
        return {
            "category": "Uncategorized",
            "confidence": 0.0,
        }

    # 1. Apply bank-specific rules before machine learning.
    rule_result = detect_bank_category(text)

    if rule_result is not None:
        category, confidence = rule_result

        return {
            "category": category,
            "confidence": confidence,
        }

    # 2. Use the ML model for remaining descriptions.
    transformed_text = vectorizer.transform([text])

    prediction = model.predict(transformed_text)[0]
    probabilities = model.predict_proba(transformed_text)[0]

    confidence = float(max(probabilities) * 100)

    # Avoid forcing a weak prediction onto an unrelated category.
    if confidence < 40:
        return {
            "category": prediction,
            "confidence": round(confidence, 2)
        }

    return {
        "category": str(prediction),
        "confidence": round(float(confidence), 2)
    }