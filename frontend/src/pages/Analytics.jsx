import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
} from "recharts";

import API from "../api";

function Analytics() {
  const currentMonth = new Date()
    .toISOString()
    .slice(0, 7);

  const [selectedMonth, setSelectedMonth] =
    useState(currentMonth);

  const [analytics, setAnalytics] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const loadAnalytics = async (month) => {
    try {
      setLoading(true);
      setError("");

      const response = await API.get(
        `/analytics/advanced?month=${month}`
      );

      setAnalytics(response.data);
    } catch (err) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
        "Failed to load analytics."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalytics(selectedMonth);
  }, [selectedMonth]);

  const formatCurrency = (value) => {
    return `₹${Number(value || 0).toLocaleString(
      "en-IN",
      {
        maximumFractionDigits: 2,
      }
    )}`;
  };

  const formatPercentage = (value) => {
    const number = Number(value || 0);

    return `${number > 0 ? "+" : ""}${number.toFixed(
      2
    )}%`;
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="page-header">
          <h1>📈 Advanced Analytics</h1>
          <p>
            Analyzing your financial activity...
          </p>
        </div>

        <div className="analytics-loading">
          Loading analytics...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="page-header">
          <h1>📈 Advanced Analytics</h1>
        </div>

        <div className="error-message">
          {error}
        </div>
      </div>
    );
  }

  if (!analytics) {
    return null;
  }

  const summary =
    analytics.summary || {};

  const previousMonth =
    analytics.previous_month || {};

  const comparison =
    analytics.month_comparison || {};

  const categoryData =
    analytics.category_spending || [];

  const merchantData =
    analytics.top_merchants || [];

  const paymentData =
    analytics.payment_methods || [];

  const dailyData =
    analytics.daily_spending || [];

  const spendingPattern =
    analytics.spending_pattern || {};

  const comparisonData = [
    {
      name: "Income",
      current: summary.income || 0,
      previous:
        previousMonth.income || 0,
    },
    {
      name: "Expenses",
      current: summary.expenses || 0,
      previous:
        previousMonth.expenses || 0,
    },
    {
      name: "Savings",
      current: summary.savings || 0,
      previous:
        previousMonth.savings || 0,
    },
  ];

  const paymentChartData =
    paymentData.map((item) => ({
      name: item.payment_method,
      amount: item.amount,
    }));

  const dailyChartData =
    dailyData.map((item) => ({
      date: item.date.slice(8),
      amount: item.amount,
    }));

  const highestSpendingDay =
    spendingPattern.highest_spending_day;

  return (
    <div className="page-container">

      {/* Header */}

      <div className="page-header analytics-header">

        <div>
          <h1>
            📈 Advanced Analytics
          </h1>

          <p>
            Understand your spending patterns
            and financial behavior.
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

      {/* Summary */}

      <div className="analytics-summary-grid">

        <div className="analytics-stat">
          <span>💰</span>

          <div>
            <small>
              Income
            </small>

            <strong>
              {formatCurrency(
                summary.income
              )}
            </strong>
          </div>
        </div>

        <div className="analytics-stat">
          <span>💸</span>

          <div>
            <small>
              Expenses
            </small>

            <strong>
              {formatCurrency(
                summary.expenses
              )}
            </strong>
          </div>
        </div>

        <div className="analytics-stat">
          <span>💵</span>

          <div>
            <small>
              Savings
            </small>

            <strong>
              {formatCurrency(
                summary.savings
              )}
            </strong>
          </div>
        </div>

        <div className="analytics-stat">
          <span>🔢</span>

          <div>
            <small>
              Transactions
            </small>

            <strong>
              {summary.transaction_count ||
                0}
            </strong>
          </div>
        </div>

      </div>

      {/* Month Comparison */}

      <div className="analytics-section">

        <div className="section-heading">
          <div>
            <h2>
              📊 Month-to-Month Comparison
            </h2>

            <p>
              {selectedMonth} vs{" "}
              {previousMonth.month}
            </p>
          </div>
        </div>

        <div className="comparison-chart">

          <ResponsiveContainer
            width="100%"
            height={350}
          >
            <BarChart
              data={comparisonData}
            >
              <CartesianGrid
                strokeDasharray="3 3"
              />

              <XAxis
                dataKey="name"
              />

              <YAxis />

              <Tooltip
                formatter={(value) =>
                  formatCurrency(value)
                }
              />

              <Legend />

              <Bar
                dataKey="current"
                name={selectedMonth}
              />

              <Bar
                dataKey="previous"
                name={
                  previousMonth.month
                }
              />

            </BarChart>
          </ResponsiveContainer>

        </div>

        <div className="comparison-cards">

          <div>
            <span>
              Income Change
            </span>

            <strong>
              {formatPercentage(
                comparison.income_change_percentage
              )}
            </strong>
          </div>

          <div>
            <span>
              Expense Change
            </span>

            <strong>
              {formatPercentage(
                comparison.expense_change_percentage
              )}
            </strong>
          </div>

          <div>
            <span>
              Savings Change
            </span>

            <strong>
              {formatPercentage(
                comparison.savings_change_percentage
              )}
            </strong>
          </div>

        </div>

      </div>

      {/* Category + Payment */}

      <div className="analytics-two-column">

        {/* Categories */}

        <div className="analytics-section">

          <div className="section-heading">
            <div>
              <h2>
                🏷️ Category Spending
              </h2>

              <p>
                Your biggest expense categories
              </p>
            </div>
          </div>

          {categoryData.length > 0 ? (

            <div className="analytics-chart">

              <ResponsiveContainer
                width="100%"
                height={350}
              >
                <PieChart>

                  <Pie
                    data={categoryData}
                    dataKey="amount"
                    nameKey="category"
                    cx="50%"
                    cy="50%"
                    outerRadius={110}
                    label
                  >
                    {categoryData.map(
                      (_, index) => (
                        <Cell
                          key={`category-${index}`}
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

            <div className="analytics-empty">
              No category spending
              available.
            </div>

          )}

        </div>

        {/* Payment Methods */}

        <div className="analytics-section">

          <div className="section-heading">
            <div>
              <h2>
                💳 Payment Methods
              </h2>

              <p>
                How you spent your money
              </p>
            </div>
          </div>

          {paymentChartData.length > 0 ? (

            <ResponsiveContainer
              width="100%"
              height={350}
            >
              <BarChart
                data={paymentChartData}
                layout="vertical"
                margin={{
                  left: 20,
                  right: 20,
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                />

                <XAxis
                  type="number"
                />

                <YAxis
                  type="category"
                  dataKey="name"
                  width={80}
                />

                <Tooltip
                  formatter={(value) =>
                    formatCurrency(value)
                  }
                />

                <Bar
                  dataKey="amount"
                  name="Amount"
                />

              </BarChart>

            </ResponsiveContainer>

          ) : (

            <div className="analytics-empty">
              No payment method
              data available.
            </div>

          )}

        </div>

      </div>

      {/* Daily Spending */}

      <div className="analytics-section">

        <div className="section-heading">
          <div>
            <h2>
              📅 Daily Spending Pattern
            </h2>

            <p>
              Your spending throughout the
              selected month
            </p>
          </div>
        </div>

        {dailyChartData.length > 0 ? (

          <ResponsiveContainer
            width="100%"
            height={350}
          >
            <LineChart
              data={dailyChartData}
            >

              <CartesianGrid
                strokeDasharray="3 3"
              />

              <XAxis
                dataKey="date"
              />

              <YAxis />

              <Tooltip
                formatter={(value) =>
                  formatCurrency(value)
                }
              />

              <Line
                type="monotone"
                dataKey="amount"
                name="Daily Spending"
                strokeWidth={3}
              />

            </LineChart>

          </ResponsiveContainer>

        ) : (

          <div className="analytics-empty">
            No daily spending data
            available.
          </div>

        )}

      </div>

      {/* Spending Pattern */}

      <div className="analytics-insights-grid">

        <div className="analytics-insight-card">

          <span className="insight-icon">
            📅
          </span>

          <div>
            <small>
              Average Spending
            </small>

            <h3>
              {formatCurrency(
                spendingPattern.average_daily_spending
              )}
            </h3>

            <p>
              Average per spending day
            </p>
          </div>

        </div>

        <div className="analytics-insight-card">

          <span className="insight-icon">
            🔥
          </span>

          <div>
            <small>
              Highest Spending Day
            </small>

            <h3>
              {highestSpendingDay
                ? highestSpendingDay.date
                : "None"}
            </h3>

            <p>
              {highestSpendingDay
                ? formatCurrency(
                    highestSpendingDay.amount
                  )
                : "No spending data"}
            </p>
          </div>

        </div>

      </div>

      {/* Top Merchants */}

      <div className="analytics-section">

        <div className="section-heading">
          <div>
            <h2>
              🏪 Top Merchants
            </h2>

            <p>
              Merchants where you spent the
              most
            </p>
          </div>
        </div>

        {merchantData.length > 0 ? (

          <div className="merchant-table">

            <div className="merchant-table-header">
              <span>
                Rank
              </span>

              <span>
                Merchant
              </span>

              <span>
                Amount
              </span>
            </div>

            {merchantData.map(
              (merchant, index) => (

                <div
                  className="merchant-row"
                  key={`${merchant.merchant}-${index}`}
                >

                  <span>
                    #{index + 1}
                  </span>

                  <span>
                    {merchant.merchant}
                  </span>

                  <strong>
                    {formatCurrency(
                      merchant.amount
                    )}
                  </strong>

                </div>

              )
            )}

          </div>

        ) : (

          <div className="analytics-empty">
            No merchant data available.
          </div>

        )}

      </div>

    </div>
  );
}

export default Analytics;