from .behavior import analyze_spending_behavior

def generate_financial_insights(
    total_income: float,
    total_expenses: float,
    category_spending: list,
    budget_usage: list,
    savings_progress: list,
    db,
    user_id,
):
    """
    Generate personalized AI-style financial recommendations.
    """

    insights = []

    # --------------------------------------------------
    # Basic calculations
    # --------------------------------------------------

    savings = total_income - total_expenses

    if total_income > 0:
        savings_rate = (
            savings / total_income
        ) * 100
    else:
        savings_rate = 0

    if total_income > 0:
        expense_ratio = (
            total_expenses / total_income
        ) * 100
    else:
        expense_ratio = 100

    # --------------------------------------------------
    # 1. Savings recommendation
    # --------------------------------------------------

    if total_income <= 0:
        insights.append({
            "type": "info",
            "title": "Add your income",
            "message": (
                "Add your income transactions to "
                "receive personalized savings recommendations."
            )
        })

    elif savings_rate < 10:
        recommended_savings = total_income * 0.10

        insights.append({
            "type": "warning",
            "title": "Increase your savings",
            "message": (
                f"Your current savings rate is "
                f"{savings_rate:.1f}%. "
                f"Try saving at least ₹"
                f"{recommended_savings:,.0f} per month."
            )
        })

    elif savings_rate < 20:
        recommended_savings = total_income * 0.20

        insights.append({
            "type": "suggestion",
            "title": "Build stronger savings",
            "message": (
                f"You're saving {savings_rate:.1f}% "
                f"of your income. Consider gradually "
                f"increasing this toward 20% "
                f"(about ₹{recommended_savings:,.0f})."
            )
        })

    else:
        insights.append({
            "type": "positive",
            "title": "Healthy savings rate",
            "message": (
                f"You're saving {savings_rate:.1f}% "
                "of your income. Keep maintaining "
                "this healthy savings habit."
            )
        })

    # --------------------------------------------------
    # 2. Expense ratio
    # --------------------------------------------------

    if expense_ratio > 90:
        insights.append({
            "type": "warning",
            "title": "Very high expenses",
            "message": (
                f"Your expenses consume {expense_ratio:.1f}% "
                "of your income. Review non-essential "
                "spending and look for areas to reduce."
            )
        })

    elif expense_ratio > 75:
        insights.append({
            "type": "warning",
            "title": "Watch your spending",
            "message": (
                f"You're using {expense_ratio:.1f}% "
                "of your income for expenses. "
                "Try to keep more room for savings."
            )
        })

    # --------------------------------------------------
    # 3. Highest spending category
    # --------------------------------------------------

    if category_spending:
        highest_category = max(
            category_spending,
            key=lambda item: float(
                item.get("amount", 0)
            )
        )

        category = highest_category.get(
            "category",
            "Other"
        )

        amount = float(
            highest_category.get(
                "amount",
                0
            )
        )

        if total_expenses > 0:
            category_percentage = (
                amount / total_expenses
            ) * 100
        else:
            category_percentage = 0

        if category_percentage >= 40:
            insights.append({
                "type": "warning",
                "title": f"High {category} spending",
                "message": (
                    f"{category} accounts for "
                    f"{category_percentage:.1f}% of your "
                    f"total expenses (₹{amount:,.0f}). "
                    "Consider setting a limit for this category."
                )
            })

        elif category_percentage >= 25:
            insights.append({
                "type": "suggestion",
                "title": f"Monitor {category} spending",
                "message": (
                    f"{category} is your largest expense "
                    f"category at ₹{amount:,.0f}. "
                    "Keep an eye on this category."
                )
            })

    # --------------------------------------------------
    # 4. Budget recommendations
    # --------------------------------------------------

    exceeded_budgets = []
    near_limit_budgets = []

    for budget in budget_usage:
        percentage = float(
            budget.get(
                "percentage_used",
                0
            )
        )

        category = budget.get(
            "category",
            "Unknown"
        )

        if percentage > 100:
            exceeded_budgets.append(category)

        elif percentage >= 80:
            near_limit_budgets.append(category)

    if exceeded_budgets:
        categories = ", ".join(
            exceeded_budgets
        )

        insights.append({
            "type": "warning",
            "title": "Budget exceeded",
            "message": (
                f"You have exceeded your budget for: "
                f"{categories}. Consider reducing "
                "spending in these categories."
            )
        })

    if near_limit_budgets:
        categories = ", ".join(
            near_limit_budgets
        )

        insights.append({
            "type": "suggestion",
            "title": "Budget approaching limit",
            "message": (
                f"You're approaching your budget limit "
                f"for: {categories}. "
                "Monitor upcoming expenses carefully."
            )
        })

    # --------------------------------------------------
    # 5. Savings goals
    # --------------------------------------------------

    if not savings_progress:
        insights.append({
            "type": "suggestion",
            "title": "Create a savings goal",
            "message": (
                "Set a savings goal such as an emergency "
                "fund, education, travel, or a major purchase "
                "to give your savings a clear purpose."
            )
        })

    else:
        incomplete_goals = []

        for goal in savings_progress:
            percentage = float(
                goal.get(
                    "percentage_completed",
                    0
                )
            )

            if percentage < 50:
                incomplete_goals.append(
                    goal.get(
                        "goal_name",
                        "Savings goal"
                    )
                )

        if incomplete_goals:
            goal_name = incomplete_goals[0]

            insights.append({
                "type": "suggestion",
                "title": "Focus on your savings goal",
                "message": (
                    f"Your goal '{goal_name}' is "
                    "less than 50% complete. "
                    "Consider allocating part of your "
                    "monthly savings toward it."
                )
            })
        else:
            insights.append({
                "type": "positive",
                "title": "Savings goals are progressing",
                "message": (
                    "Your savings goals are making good "
                    "progress. Keep contributing regularly."
                )
            })

    # --------------------------------------------------
    # 6. General positive recommendation
    # --------------------------------------------------

    if not insights:
        insights.append({
            "type": "info",
            "title": "Keep tracking",
            "message": (
                "Continue recording your income and expenses "
                "to receive more personalized recommendations."
            )
        })

        # ---------------------------------------------------------
    # Historical spending behaviour
    # ---------------------------------------------------------

    behavior = analyze_spending_behavior(
        db=db,
        user_id=user_id,
        months=6
    )

        # ---------------------------------------------------------
    # Add historical behaviour insights
    # ---------------------------------------------------------

    if behavior:

        # Overall spending trend
        overall_trend = behavior.get(
            "overall_trend"
        )

        if overall_trend == "increasing":

            insights.append({
                "type": "warning",
                "title": "Spending trend is increasing",
                "message": (
                    "Your spending has been increasing "
                    "across recent months. Review your "
                    "major expense categories."
                )
            })

        elif overall_trend == "decreasing":

            insights.append({
                "type": "positive",
                "title": "Spending trend is improving",
                "message": (
                    "Your recent spending is lower than "
                    "earlier months."
                )
            })

        # -----------------------------------------------------
        # Weekend / weekday behaviour
        # -----------------------------------------------------

        weekday_weekend = behavior.get(
            "weekday_weekend",
            {}
        )

        pattern = weekday_weekend.get(
            "pattern"
        )

        if pattern == "higher_on_weekends":

            insights.append({
                "type": "suggestion",
                "title": "Higher weekend spending",
                "message": (
                    "Your average spending is noticeably "
                    "higher on weekends. Consider setting "
                    "a weekend spending limit."
                )
            })

        elif pattern == "higher_on_weekdays":

            insights.append({
                "type": "info",
                "title": "Higher weekday spending",
                "message": (
                    "Your average spending is noticeably "
                    "higher on weekdays."
                )
            })

        # -----------------------------------------------------
        # Category behaviour
        # -----------------------------------------------------

        category_behavior = behavior.get(
            "category_behavior",
            []
        )

        for category in category_behavior:

            if category.get("trend") == "increasing":

                insights.append({
                    "type": "warning",
                    "title": (
                        f"{category['category']} spending increased"
                    ),
                    "message": (
                        f"Your spending in "
                        f"{category['category']} has increased "
                        f"significantly compared with the "
                        f"previous month."
                    )
                })

        # -----------------------------------------------------
        # Recurring transactions
        # -----------------------------------------------------

        recurring = behavior.get(
            "recurring_transactions",
            []
        )

        if recurring:

            insights.append({
                "type": "info",
                "title": "Recurring spending detected",
                "message": (
                    f"PennyWise detected "
                    f"{len(recurring)} recurring spending "
                    f"pattern(s) in your transaction history."
                )
            })

        # -----------------------------------------------------
        # Unusual expenses
        # -----------------------------------------------------

        unusual = behavior.get(
            "unusual_expenses",
            []
        )

        if unusual:

            insights.append({
                "type": "warning",
                "title": "Unusual spending detected",
                "message": (
                    f"{len(unusual)} unusually high "
                    f"expense transaction(s) were found "
                    f"in your historical spending."
                )
            })

    return insights