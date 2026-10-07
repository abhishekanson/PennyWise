import { useEffect, useState } from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

import API from "../api";

function Reports() {
  const currentMonth = new Date()
    .toISOString()
    .slice(0, 7);

  const [selectedMonth, setSelectedMonth] = useState(
    currentMonth
  );

  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadReport = async (month) => {
    try {
      setLoading(true);
      setError("");

      const response = await API.get(
        `/reports/monthly?month=${month}`
      );

      setReport(response.data);
    } catch (err) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
        "Failed to load monthly report."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReport(selectedMonth);
  }, [selectedMonth]);

  const formatCurrency = (value) => {
    return `₹${Number(value || 0).toLocaleString(
      "en-IN",
      {
        maximumFractionDigits: 2,
      }
    )}`;
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="page-header">
          <h1>📊 Financial Reports</h1>
          <p>Loading your monthly financial report...</p>
        </div>

        <div className="report-loading">
          Loading...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="page-header">
          <h1>📊 Financial Reports</h1>
        </div>

        <div className="error-message">
          {error}
        </div>
      </div>
    );
  }

  if (!report) {
    return null;
  }

  const summary = report.summary || {};
  const budget = report.budget || {};
  const health = report.financial_health || {};

  const categoryData =
    report.category_spending || [];

  const pieData = categoryData.map((item) => ({
    name: item.category,
    value: item.amount,
  }));

  return (
    <div className="page-container">

      {/* Header */}
      <div className="page-header report-header">

        <div>
          <h1>📊 Financial Reports</h1>

          <p>
            Analyze your financial performance
            month by month.
          </p>
        </div>

        <div className="month-selector">
          <label>
            Select Month
          </label>

          <input
            type="month"
            value={selectedMonth}
            onChange={(e) =>
              setSelectedMonth(
                e.target.value
              )
            }
          />
        </div>

      </div>

      {/* Summary Cards */}
      <div className="report-summary-grid">

        <div className="report-card income-card">
          <span className="report-card-icon">
            💰
          </span>

          <div>
            <p>Total Income</p>

            <h2>
              {formatCurrency(
                summary.income
              )}
            </h2>
          </div>
        </div>

        <div className="report-card expense-card">
          <span className="report-card-icon">
            💸
          </span>

          <div>
            <p>Total Expenses</p>

            <h2>
              {formatCurrency(
                summary.expenses
              )}
            </h2>
          </div>
        </div>

        <div className="report-card savings-card">
          <span className="report-card-icon">
            💵
          </span>

          <div>
            <p>Net Savings</p>

            <h2>
              {formatCurrency(
                summary.savings
              )}
            </h2>
          </div>
        </div>

        <div className="report-card rate-card">
          <span className="report-card-icon">
            📈
          </span>

          <div>
            <p>Savings Rate</p>

            <h2>
              {summary.savings_rate || 0}%
            </h2>
          </div>
        </div>

      </div>

      {/* Secondary Summary */}
      <div className="report-info-grid">

        <div className="report-info-card">
          <span>🔢</span>

          <div>
            <small>
              Transactions
            </small>

            <strong>
              {summary.transaction_count || 0}
            </strong>
          </div>
        </div>

        <div className="report-info-card">
          <span>🔥</span>

          <div>
            <small>
              Highest Spending Category
            </small>

            <strong>
              {report.highest_spending_category ||
                "None"}
            </strong>
          </div>
        </div>

        <div className="report-info-card">
          <span>📉</span>

          <div>
            <small>
              Expense Ratio
            </small>

            <strong>
              {summary.expense_ratio || 0}%
            </strong>
          </div>
        </div>

      </div>

      {/* Main Report Grid */}
      <div className="reports-main-grid">

        {/* Category Spending */}
        <div className="report-section">

          <div className="section-heading">
            <div>
              <h2>
                Category-wise Spending
              </h2>

              <p>
                Where your money went this month
              </p>
            </div>
          </div>

          {pieData.length > 0 ? (
            <div className="report-chart">

              <ResponsiveContainer
                width="100%"
                height={330}
              >
                <PieChart>

                  <Pie
                    data={pieData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={105}
                    label
                  >
                    {pieData.map(
                      (_, index) => (
                        <Cell
                          key={`cell-${index}`}
                        />
                      )
                    )}
                  </Pie>

                  <Tooltip
                    formatter={(value) =>
                      formatCurrency(value)
                    }
                  />

                  <Legend />

                </PieChart>
              </ResponsiveContainer>

            </div>
          ) : (
            <div className="empty-report">
              No expenses recorded
              for this month.
            </div>
          )}

        </div>

        {/* Budget Performance */}
        <div className="report-section">

          <div className="section-heading">
            <div>
              <h2>
                🎯 Budget Performance
              </h2>

              <p>
                Monthly budget utilization
              </p>
            </div>
          </div>

          <div className="budget-overview">

            <div className="budget-total">
              <span>
                Total Budget
              </span>

              <strong>
                {formatCurrency(
                  budget.total_budget
                )}
              </strong>
            </div>

            <div className="budget-total">
              <span>
                Total Spent
              </span>

              <strong>
                {formatCurrency(
                  budget.total_expenses
                )}
              </strong>
            </div>

            <div className="budget-total">
              <span>
                Overall Usage
              </span>

              <strong>
                {budget.usage_percentage || 0}%
              </strong>
            </div>

          </div>

          <div className="budget-list">

            {budget.categories?.length > 0 ? (
              budget.categories.map(
                (item) => {

                  const percentage =
                    Number(
                      item.percentage_used || 0
                    );

                  return (
                    <div
                      className="budget-row"
                      key={item.category}
                    >

                      <div className="budget-row-header">

                        <span>
                          {item.category}
                        </span>

                        <span>
                          {formatCurrency(
                            item.spent_amount
                          )}{" "}
                          /{" "}
                          {formatCurrency(
                            item.budget_amount
                          )}
                        </span>

                      </div>

                      <div className="budget-progress">
                        <div
                          className="budget-progress-fill"
                          style={{
                            width: `${Math.min(
                              percentage,
                              100
                            )}%`,
                          }}
                        />
                      </div>

                      <small>
                        {percentage}% used
                      </small>

                    </div>
                  );
                }
              )
            ) : (
              <div className="empty-report">
                No budgets created
                for this month.
              </div>
            )}

          </div>

        </div>

      </div>

      {/* Financial Health */}
      <div className="health-report-section">

        <div className="section-heading">
          <div>
            <h2>
              ❤️ Financial Health
            </h2>

            <p>
              Your overall financial health
              for {selectedMonth}
            </p>
          </div>

          <div className="health-rating">
            {health.rating || "N/A"}
          </div>
        </div>

        <div className="health-report-content">

          <div className="health-score-large">

            <div className="health-score-number">
              {health.score || 0}
            </div>

            <span>
              out of 100
            </span>

          </div>

          <div className="health-components">

            <div className="health-component">
              <span>
                Savings
              </span>

              <strong>
                {health.component_scores
                  ?.savings || 0}/40
              </strong>
            </div>

            <div className="health-component">
              <span>
                Expenses
              </span>

              <strong>
                {health.component_scores
                  ?.expenses || 0}/25
              </strong>
            </div>

            <div className="health-component">
              <span>
                Budget
              </span>

              <strong>
                {health.component_scores
                  ?.budget || 0}/20
              </strong>
            </div>

            <div className="health-component">
              <span>
                Savings Goals
              </span>

              <strong>
                {health.component_scores
                  ?.savings_goals || 0}/15
              </strong>
            </div>

          </div>

          <div className="health-recommendations">

            <h3>
              💡 Recommendations
            </h3>

            {health.recommendations?.map(
              (recommendation, index) => (
                <div
                  className="recommendation-item"
                  key={index}
                >
                  <span>✓</span>
                  <p>
                    {recommendation}
                  </p>
                </div>
              )
            )}

          </div>

        </div>

      </div>

    </div>
  );
}

export default Reports;