from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


# Training data
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

    # Other
    ("gift", "Other"),
    ("donation", "Other"),
    ("miscellaneous expense", "Other"),
    ("other payment", "Other"),
]


# Separate the training examples and labels
training_texts = [
    item[0] for item in training_data
]

training_categories = [
    item[1] for item in training_data
]


# Convert text into numerical features
vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2)
)

X = vectorizer.fit_transform(
    training_texts
)


# Train the classification model
model = LogisticRegression(
    max_iter=1000
)

model.fit(
    X,
    training_categories
)


def predict_category(text: str):
    """
    Predict the most likely expense category.
    """

    if not text or not text.strip():
        return {
            "category": "Other",
            "confidence": 0.0
        }

    transformed_text = vectorizer.transform(
        [text]
    )

    prediction = model.predict(
        transformed_text
    )[0]

    probabilities = model.predict_proba(
        transformed_text
    )[0]

    confidence = max(probabilities) * 100

    return {
        "category": prediction,
        "confidence": round(
            float(confidence),
            2
        )
    }