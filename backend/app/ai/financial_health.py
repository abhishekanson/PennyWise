def calculate_financial_health(
    total_income: float,
    total_expenses: float,
    budget_usage: list,
    savings_progress: list,
):
    """
    Calculate PennyWise Financial Health Score.

    Maximum score: 100

    Savings rate       -> 40 points
    Expense ratio      -> 25 points
    Budget management  -> 20 points
    Savings goals      -> 15 points
    """

    # ---------------------------------------------
    # Basic calculations
    # ---------------------------------------------

    if total_income > 0:
        savings_rate = (
            (total_income - total_expenses)
            / total_income
        ) * 100
    else:
        savings_rate = 0

    if total_income > 0:
        expense_ratio = (
            total_expenses /
            total_income
        ) * 100
    else:
        expense_ratio = 100

    # ---------------------------------------------
    # 1. Savings Rate Score - 40 points
    # ---------------------------------------------

    if savings_rate >= 30:
        savings_score = 40

    elif savings_rate >= 20:
        savings_score = 35

    elif savings_rate >= 10:
        savings_score = 25

    elif savings_rate > 0:
        savings_score = 15

    else:
        savings_score = 0

    # ---------------------------------------------
    # 2. Expense Ratio Score - 25 points
    # ---------------------------------------------

    if expense_ratio <= 50:
        expense_score = 25

    elif expense_ratio <= 60:
        expense_score = 22

    elif expense_ratio <= 70:
        expense_score = 18

    elif expense_ratio <= 80:
        expense_score = 12

    elif expense_ratio <= 100:
        expense_score = 5

    else:
        expense_score = 0

    # ---------------------------------------------
    # 3. Budget Management - 20 points
    # ---------------------------------------------

    if not budget_usage:
        budget_score = 10

    else:
        budget_scores = []

        for budget in budget_usage:

            percentage = float(
                budget.get(
                    "percentage_used",
                    0
                )
            )

            if percentage <= 70:
                score = 20

            elif percentage <= 80:
                score = 16

            elif percentage <= 90:
                score = 12

            elif percentage <= 100:
                score = 8

            else:
                score = 0

            budget_scores.append(score)

        budget_score = round(
            sum(budget_scores)
            / len(budget_scores)
        )

    # ---------------------------------------------
    # 4. Savings Goals - 15 points
    # ---------------------------------------------

    if not savings_progress:
        savings_goal_score = 5

    else:
        goal_scores = []

        for goal in savings_progress:

            percentage = float(
                goal.get(
                    "percentage_completed",
                    0
                )
            )

            if percentage >= 75:
                score = 15

            elif percentage >= 50:
                score = 12

            elif percentage >= 25:
                score = 8

            elif percentage > 0:
                score = 5

            else:
                score = 0

            goal_scores.append(score)

        savings_goal_score = round(
            sum(goal_scores)
            / len(goal_scores)
        )

    # ---------------------------------------------
    # Final score
    # ---------------------------------------------

    score = (
        savings_score
        + expense_score
        + budget_score
        + savings_goal_score
    )

    score = max(
        0,
        min(score, 100)
    )

    # ---------------------------------------------
    # Rating
    # ---------------------------------------------

    if score >= 80:
        rating = "Excellent"

    elif score >= 60:
        rating = "Good"

    elif score >= 40:
        rating = "Fair"

    else:
        rating = "Needs Improvement"

    # ---------------------------------------------
    # Recommendations
    # ---------------------------------------------

    recommendations = []

    if savings_rate < 10:
        recommendations.append(
            "Try to increase your savings rate "
            "by reducing non-essential expenses."
        )

    if expense_ratio > 80:
        recommendations.append(
            "Your expenses are consuming most "
            "of your income. Review your spending."
        )

    if budget_usage:
        exceeded = [
            item
            for item in budget_usage
            if float(
                item.get(
                    "percentage_used",
                    0
                )
            ) > 100
        ]

        if exceeded:
            recommendations.append(
                "You have exceeded one or more "
                "category budgets."
            )

    if not savings_progress:
        recommendations.append(
            "Create a savings goal to improve "
            "your long-term financial planning."
        )

    if not recommendations:
        recommendations.append(
            "Your financial habits are healthy. "
            "Continue monitoring your spending and savings."
        )

    return {
        "score": score,
        "rating": rating,
        "savings_rate": round(
            savings_rate,
            2
        ),
        "expense_ratio": round(
            expense_ratio,
            2
        ),
        "component_scores": {
            "savings": savings_score,
            "expenses": expense_score,
            "budget": budget_score,
            "savings_goals": savings_goal_score,
        },
        "recommendations": recommendations,
    }