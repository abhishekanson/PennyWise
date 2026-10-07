from collections import defaultdict
from datetime import date, timedelta

import pandas as pd
from sqlalchemy.orm import Session

from ..models import Transaction


def analyze_spending_behavior(
    db: Session,
    user_id: int,
    months: int = 6
):
    """
    Analyze historical spending behaviour for a user.

    Looks at:
    - Monthly spending trends
    - Category trends
    - Weekday vs weekend spending
    - Top merchants
    - Payment method usage
    - Recurring transactions
    - Unusually high expenses
    """

    # ---------------------------------------------------------
    # 1. Get historical transactions
    # ---------------------------------------------------------

    end_date = date.today()

    start_date = (
        end_date.replace(day=1)
        - timedelta(days=months * 31)
    )

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == user_id,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.type == "expense"
        )
        .order_by(Transaction.date.asc())
        .all()
    )

    if not transactions:
        return {
            "period_months": months,
            "transactions_analyzed": 0,
            "monthly_trend": [],
            "category_behavior": [],
            "weekday_weekend": {},
            "top_merchants": [],
            "payment_methods": [],
            "recurring_transactions": [],
            "unusual_expenses": [],
            "behaviour_summary": []
        }

    # ---------------------------------------------------------
    # 2. Convert transactions to DataFrame
    # ---------------------------------------------------------

    data = []

    for transaction in transactions:
        data.append({
            "id": transaction.id,
            "date": transaction.date,
            "amount": float(transaction.amount),
            "category": transaction.category or "Other",
            "merchant": transaction.merchant or "Unknown",
            "payment_method": (
                transaction.payment_method or "Unknown"
            ),
            "description": (
                transaction.description or ""
            )
        })

    df = pd.DataFrame(data)

    df["date"] = pd.to_datetime(df["date"])

    df["month"] = df["date"].dt.strftime("%Y-%m")

    df["day_of_week"] = df["date"].dt.day_name()

    df["is_weekend"] = (
        df["date"].dt.dayofweek >= 5
    )

    # ---------------------------------------------------------
    # 3. Monthly spending trend
    # ---------------------------------------------------------

    monthly = (
        df.groupby("month")["amount"]
        .sum()
        .reset_index()
    )

    monthly = monthly.sort_values("month")

    monthly_trend = []

    for _, row in monthly.iterrows():

        monthly_trend.append({
            "month": row["month"],
            "spending": round(
                float(row["amount"]),
                2
            )
        })

    # ---------------------------------------------------------
    # 4. Detect monthly spending direction
    # ---------------------------------------------------------

    trend = "stable"

    if len(monthly) >= 2:

        first_half = monthly.iloc[
            : max(1, len(monthly) // 2)
        ]["amount"].mean()

        second_half = monthly.iloc[
            len(monthly) // 2:
        ]["amount"].mean()

        if second_half > first_half * 1.10:
            trend = "increasing"

        elif second_half < first_half * 0.90:
            trend = "decreasing"

    # ---------------------------------------------------------
    # 5. Category behaviour
    # ---------------------------------------------------------

    category_totals = (
        df.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    category_behavior = []

    for category, total in category_totals.items():

        category_df = df[
            df["category"] == category
        ]

        category_monthly = (
            category_df.groupby("month")["amount"]
            .sum()
            .sort_index()
        )

        category_trend = "stable"

        if len(category_monthly) >= 2:

            previous = float(
                category_monthly.iloc[-2]
            )

            current = float(
                category_monthly.iloc[-1]
            )

            if previous > 0:

                change = (
                    (current - previous)
                    / previous
                ) * 100

                if change >= 20:
                    category_trend = "increasing"

                elif change <= -20:
                    category_trend = "decreasing"

        category_behavior.append({
            "category": category,
            "total_spending": round(
                float(total),
                2
            ),
            "transaction_count": int(
                len(category_df)
            ),
            "trend": category_trend
        })

    # ---------------------------------------------------------
    # 6. Weekday vs weekend behaviour
    # ---------------------------------------------------------

    weekday_spending = float(
        df.loc[
            ~df["is_weekend"],
            "amount"
        ].sum()
    )

    weekend_spending = float(
        df.loc[
            df["is_weekend"],
            "amount"
        ].sum()
    )

    weekday_count = int(
        (~df["is_weekend"]).sum()
    )

    weekend_count = int(
        df["is_weekend"].sum()
    )

    weekday_average = (
        weekday_spending / weekday_count
        if weekday_count > 0
        else 0
    )

    weekend_average = (
        weekend_spending / weekend_count
        if weekend_count > 0
        else 0
    )

    if weekend_average > weekday_average * 1.20:
        spending_pattern = "higher_on_weekends"

    elif weekday_average > weekend_average * 1.20:
        spending_pattern = "higher_on_weekdays"

    else:
        spending_pattern = "balanced"

    weekday_weekend = {
        "weekday_spending": round(
            weekday_spending,
            2
        ),
        "weekend_spending": round(
            weekend_spending,
            2
        ),
        "weekday_average": round(
            weekday_average,
            2
        ),
        "weekend_average": round(
            weekend_average,
            2
        ),
        "pattern": spending_pattern
    }

    # ---------------------------------------------------------
    # 7. Top merchants
    # ---------------------------------------------------------

    merchant_totals = (
        df.groupby("merchant")
        .agg(
            total_spending=("amount", "sum"),
            transaction_count=("amount", "count")
        )
        .sort_values(
            "total_spending",
            ascending=False
        )
        .head(10)
    )

    top_merchants = []

    for merchant, row in merchant_totals.iterrows():

        top_merchants.append({
            "merchant": merchant,
            "total_spending": round(
                float(row["total_spending"]),
                2
            ),
            "transaction_count": int(
                row["transaction_count"]
            )
        })

    # ---------------------------------------------------------
    # 8. Payment method behaviour
    # ---------------------------------------------------------

    payment_totals = (
        df.groupby("payment_method")["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    total_spending = float(
        df["amount"].sum()
    )

    payment_methods = []

    for method, amount in payment_totals.items():

        percentage = (
            (float(amount) / total_spending) * 100
            if total_spending > 0
            else 0
        )

        payment_methods.append({
            "payment_method": method,
            "total_spending": round(
                float(amount),
                2
            ),
            "percentage": round(
                percentage,
                2
            )
        })

    # ---------------------------------------------------------
    # 9. Detect recurring transactions
    # ---------------------------------------------------------

    recurring_transactions = []

    grouped = defaultdict(list)

    for _, row in df.iterrows():

        # Group by merchant and approximate amount
        key = (
            str(row["merchant"]).lower().strip(),
            round(float(row["amount"]), -1)
        )

        grouped[key].append(row)

    for key, rows in grouped.items():

        if len(rows) >= 3:

            merchant = rows[0]["merchant"]

            amounts = [
                float(row["amount"])
                for row in rows
            ]

            recurring_transactions.append({
                "merchant": merchant,
                "average_amount": round(
                    sum(amounts) / len(amounts),
                    2
                ),
                "occurrences": len(rows)
            })

    recurring_transactions = (
        recurring_transactions[:10]
    )

    # ---------------------------------------------------------
    # 10. Detect unusually high expenses
    # ---------------------------------------------------------

    average_expense = float(
        df["amount"].mean()
    )

    standard_deviation = float(
        df["amount"].std()
    ) if len(df) > 1 else 0

    unusual_expenses = []

    threshold = max(
        average_expense * 2,
        average_expense + standard_deviation * 2
    )

    unusual_df = df[
        df["amount"] >= threshold
    ].sort_values(
        "amount",
        ascending=False
    )

    for _, row in unusual_df.head(10).iterrows():

        unusual_expenses.append({
            "date": row["date"].strftime(
                "%Y-%m-%d"
            ),
            "amount": round(
                float(row["amount"]),
                2
            ),
            "category": row["category"],
            "merchant": row["merchant"],
            "description": row["description"]
        })

    # ---------------------------------------------------------
    # 11. Generate behaviour summaries
    # ---------------------------------------------------------

    behaviour_summary = []

    # Overall spending trend

    if trend == "increasing":

        behaviour_summary.append({
            "type": "warning",
            "title": "Spending is increasing",
            "message": (
                "Your average spending in recent "
                "months is higher than earlier months."
            )
        })

    elif trend == "decreasing":

        behaviour_summary.append({
            "type": "positive",
            "title": "Spending is decreasing",
            "message": (
                "Your recent average spending is "
                "lower than earlier months."
            )
        })

    # Highest spending category

    if category_behavior:

        highest_category = category_behavior[0]

        behaviour_summary.append({
            "type": "info",
            "title": "Highest spending category",
            "message": (
                f"{highest_category['category']} is "
                f"your highest spending category with "
                f"₹{highest_category['total_spending']:.2f} "
                f"spent during the analysis period."
            )
        })

    # Weekend behaviour

    if spending_pattern == "higher_on_weekends":

        behaviour_summary.append({
            "type": "suggestion",
            "title": "Weekend spending pattern",
            "message": (
                "Your average spending is noticeably "
                "higher on weekends."
            )
        })

    elif spending_pattern == "higher_on_weekdays":

        behaviour_summary.append({
            "type": "info",
            "title": "Weekday spending pattern",
            "message": (
                "Your average spending is noticeably "
                "higher on weekdays."
            )
        })

    # Recurring transactions

    if recurring_transactions:

        behaviour_summary.append({
            "type": "info",
            "title": "Recurring spending detected",
            "message": (
                f"{len(recurring_transactions)} recurring "
                "spending pattern(s) were detected."
            )
        })

    # Unusual spending

    if unusual_expenses:

        behaviour_summary.append({
            "type": "warning",
            "title": "Unusual spending detected",
            "message": (
                f"{len(unusual_expenses)} unusually high "
                "expense transaction(s) were detected."
            )
        })

    # ---------------------------------------------------------
    # 12. Return complete analysis
    # ---------------------------------------------------------

    return {
        "period_months": months,
        "transactions_analyzed": len(df),

        "overall_trend": trend,

        "monthly_trend": monthly_trend,

        "category_behavior": category_behavior,

        "weekday_weekend": weekday_weekend,

        "top_merchants": top_merchants,

        "payment_methods": payment_methods,

        "recurring_transactions": recurring_transactions,

        "unusual_expenses": unusual_expenses,

        "behaviour_summary": behaviour_summary
    }