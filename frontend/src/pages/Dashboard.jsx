import { useEffect, useState } from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Bar,
  BarChart,
} from "recharts";

import API from "../api";

function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [categorySpending, setCategorySpending] = useState([]);
  const [monthlySpending, setMonthlySpending] = useState([]);
  const [budgetUsage, setBudgetUsage] = useState([]);
  const [savingsProgress, setSavingsProgress] = useState([]);
  const [recentTransactions, setRecentTransactions] = useState([]);
  const [financialInsights, setFinancialInsights] = useState([]);
  const [healthScore, setHealthScore] = useState(null);
  const [spendingBehaviour, setSpendingBehaviour] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState(
  new Date().toISOString().slice(0, 7)
);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const hasMonthData = recentTransactions.length > 0;

  const changeMonth = (offset) => {
    const [year, month] = selectedMonth
      .split("-")
      .map(Number);

    const date = new Date(year, month - 1 + offset, 1);

    const newMonth = `${date.getFullYear()}-${String(
      date.getMonth() + 1
    ).padStart(2, "0")}`;

    setSelectedMonth(newMonth);
  };

  const goToCurrentMonth = () => {
    setSelectedMonth(
      new Date().toISOString().slice(0, 7)
    );
  };

  const formattedSelectedMonth = new Date(
    `${selectedMonth}-01T00:00:00`
  ).toLocaleDateString("en-US", {
    month: "long",
    year: "numeric",
  });

  const currentMonth = new Date()
    .toISOString()
    .slice(0, 7);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError("");

        const [
          summaryResponse,
          categoryResponse,
          monthlyResponse,
          budgetResponse,
          savingsResponse,
          transactionsResponse,
          insightsResponse,
          healthResponse,
          behaviourResponse,
        ] = await Promise.all([
          API.get(
            `/analysis/summary?month=${selectedMonth}`
          ),

          API.get(
            `/analysis/category-spending?month=${selectedMonth}`
          ),

          API.get(
            `/analysis/monthly-spending?month=${selectedMonth}`
          ),

          API.get(
            `/analysis/budget-usage?month=${selectedMonth}`
          ),
          API.get("/analysis/savings-progress"),
          API.get("/transactions/"),
          API.get(`/ai/insights?month=${selectedMonth}`),
          API.get(`/ai/health-score?month=${selectedMonth}`),
          API.get("/ai/spending-behaviour?months=6"),
        ]);

        setSummary(summaryResponse.data);
        setCategorySpending(categoryResponse.data);
        setMonthlySpending(monthlyResponse.data);
        setBudgetUsage(budgetResponse.data);
        setSavingsProgress(savingsResponse.data);

        // Filter transactions for the selected month
        const monthTransactions =
          transactionsResponse.data.filter(
            (transaction) =>
              transaction.date?.slice(0, 7) === selectedMonth
          );

        // Sort newest first and show only 5
        const sortedTransactions =
          [...monthTransactions].sort(
            (a, b) =>
              new Date(b.date) -
              new Date(a.date)
          );

        setRecentTransactions(
          sortedTransactions.slice(0, 5)
        );

        setFinancialInsights(
          insightsResponse.data || []
        );

        setHealthScore(
          healthResponse.data || null
        );

        setSpendingBehaviour(
          behaviourResponse.data || null
        );

      } catch (error) {
        console.error(error);

        if (error.response?.status === 401) {
          localStorage.removeItem("token");
          window.location.href = "/login";
        } else {
          setError(
            error.response?.data?.detail ||
              "Failed to load dashboard data"
          );
        }
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [selectedMonth]);

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading your finances...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard">
        <h1>PennyWise Dashboard</h1>
        <p className="error">{error}</p>
      </div>
    );
  }

  const totalIncome = Number(
    summary?.total_income || 0
  );

  const totalExpenses = Number(
    summary?.total_expenses || 0
  );

  const balance = Number(
    summary?.balance || 0
  );

  const savingsRate =
    totalIncome > 0
      ? ((totalIncome - totalExpenses) /
          totalIncome) *
        100
      : 0;

  const categoryChartData =
    categorySpending.map((item) => ({
      name: item.category,
      value: Number(item.total),
    }));

  const monthlyChartData =
    monthlySpending.map((item) => ({
      month: item.month,
      spending: Number(item.total),
    }));

  const behaviourMonthlyData =
    (spendingBehaviour?.monthly_trend || []).map(
      (item) => ({
        month: item.month,
        spending: Number(item.spending || 0),
      })
    );

 const weekdayWeekendData = [
    {
      name: "Weekdays",
      spending: Number(
        spendingBehaviour?.weekday_weekend?.weekday_spending || 0
      ),
    },
    {
      name: "Weekends",
      spending: Number(
        spendingBehaviour?.weekday_weekend?.weekend_spending || 0
      ),
    },
  ];

  const formatDate = (date) => {
    if (!date) return "";

    return new Date(
      `${date}T00:00:00`
    ).toLocaleDateString("en-IN");
  };

  const getTrendLabel = (trend) => {
    if (!trend) return "No data";

    if (trend === "increasing") {
      return "Increasing";
    }

    if (trend === "decreasing") {
      return "Decreasing";
    }

    return "Stable";
  };

  return (
    <div className="dashboard">

      {/* Header */}

      <header className="dashboard-header">

        <div>
          <h1>Financial Overview</h1>

          <p>
            Welcome back! Here's your financial summary.
          </p>
        </div>

        <div className="dashboard-actions">

          <div className="dashboard-month-selector">

            <button
              type="button"
              className="month-nav-button"
              onClick={() => changeMonth(-1)}
              title="Previous month"
            >
              ‹
            </button>

            <div className="dashboard-month-display">
              <span className="dashboard-month-label">
                {formattedSelectedMonth}
              </span>

              <input
                id="dashboard-month"
                type="month"
                value={selectedMonth}
                onChange={(e) =>
                  setSelectedMonth(e.target.value)
                }
                aria-label="Select month"
              />
            </div>

            <button
              type="button"
              className="month-nav-button"
              onClick={() => changeMonth(1)}
              disabled={selectedMonth >= currentMonth}
              title="Next month"
            >
              ›
            </button>

            {selectedMonth !== currentMonth && (
              <button
                type="button"
                className="current-month-button"
                onClick={goToCurrentMonth}
              >
                Current
              </button>
            )}

          </div>

          <button
            className="quick-action-button"
            onClick={() => {
              window.location.href =
                "/transactions";
            }}
          >
            + Add Transaction
          </button>

          <button
            className="quick-action-button secondary"
            onClick={() => {
              window.location.href =
                "/import-statement";
            }}
          >
            Import Statement
          </button>

          <button
            className="quick-action-button secondary"
            onClick={() => {
              window.location.href =
                "/budgets";
            }}
          >
            + Create Budget
          </button>

        </div>

      </header>

      {!hasMonthData && (
        <div className="dashboard-empty-state">
          <div className="dashboard-empty-icon">
            ₹
          </div>

          <h3>
            No financial data for {formattedSelectedMonth}
          </h3>

          <p>
            Add a transaction or import a bank statement
            to see your financial analysis for this month.
          </p>

          <div className="dashboard-empty-actions">

            <button
              className="quick-action-button"
              onClick={() => {
                window.location.href =
                  "/transactions";
              }}
            >
              + Add Transaction
            </button>

            <button
              className="quick-action-button secondary"
              onClick={() => {
                window.location.href =
                  "/import-statement";
              }}
            >
              Import Statement
            </button>

          </div>
        </div>
      )}


      {/* Summary Cards */}

      <section className="summary-grid">

        <div className="summary-card income-card">

          <div className="card-icon">
            ₹
          </div>

          <div>
            <h3>Total Income</h3>

            <p>
              ₹
              {totalIncome.toFixed(2)}
            </p>
          </div>

        </div>

        <div className="summary-card expense-card">

          <div className="card-icon">
            ↓
          </div>

          <div>
            <h3>Total Expenses</h3>

            <p>
              ₹
              {totalExpenses.toFixed(2)}
            </p>
          </div>

        </div>

        <div className="summary-card balance-card">

          <div className="card-icon">
            =
          </div>

          <div>
            <h3>Current Balance</h3>

            <p>
              ₹
              {balance.toFixed(2)}
            </p>
          </div>

        </div>

        <div className="summary-card savings-rate-card">

          <div className="card-icon">
            %
          </div>

          <div>
            <h3>Savings Rate</h3>

            <p>
              {Math.max(
                savingsRate,
                0
              ).toFixed(1)}
              %
            </p>
          </div>

        </div>

      </section>

      <div className="spending-behaviour-section">

        <div className="section-header">
          <div>
            <h2>Spending Behaviour</h2>
            <p>
              Analysis of your spending patterns over the last 6 months.
            </p>
          </div>
        </div>

        <div className="behaviour-summary-grid">

          <div className="behaviour-card">

            <div className="behaviour-card-label">
              Overall Spending Trend
            </div>

            <div className="behaviour-card-value">
              {getTrendLabel(
                spendingBehaviour?.overall_trend
              )}
            </div>

            <div className="behaviour-card-description">
              Based on your historical expense transactions.
            </div>

          </div>

        </div>

        <div className="behaviour-chart-card">

          <div className="behaviour-chart-header">
            <div>
              <h3>Monthly Spending Trend</h3>
              <p>
                Your expense pattern over the last 6 months.
              </p>
            </div>
          </div>

          {behaviourMonthlyData.length > 0 ? (

            <ResponsiveContainer
              width="100%"
              height={300}
            >
              <LineChart
                data={behaviourMonthlyData}
                margin={{
                  top: 10,
                  right: 20,
                  left: 10,
                  bottom: 10,
                }}
              >

                <CartesianGrid strokeDasharray="3 3" />

                <XAxis
                  dataKey="month"
                />

                <YAxis />

                <Tooltip />

                <Legend />

                <Line
                  type="monotone"
                  dataKey="spending"
                  name="Spending"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />

              </LineChart>
            </ResponsiveContainer>

          ) : (

            <div className="behaviour-no-data">
              Not enough historical spending data available.
            </div>

          )}

        </div>

        {/* Weekday vs Weekend Spending */}

        <div className="behaviour-chart-card">

          <div className="behaviour-chart-header">
            <div>
              <h3>Weekday vs Weekend Spending</h3>
              <p>
                Compare your spending patterns between weekdays and weekends.
              </p>
            </div>
          </div>

          <ResponsiveContainer
            width="100%"
            height={300}
          >
            <BarChart
              data={weekdayWeekendData}
              margin={{
                top: 10,
                right: 20,
                left: 10,
                bottom: 10,
              }}
            >

              <CartesianGrid strokeDasharray="3 3" />

              <XAxis
                dataKey="name"
              />

              <YAxis />

              <Tooltip />

              <Legend />

              <Bar
                dataKey="spending"
                name="Spending"
              />

            </BarChart>
          </ResponsiveContainer>

        </div>

      </div>

      {/* Financial Health Score */}

      <section className="dashboard-section health-score-section">

        <div className="health-score-header">

          <div>
            <h2>Financial Health Score</h2>

            <p>
              Your overall financial health based on
              spending, savings and budgeting.
            </p>
          </div>

          <div className="health-score-circle">

            <div className="health-score-number">
              {healthScore?.score ?? 0}
            </div>

            <span>/ 100</span>

          </div>

        </div>

        <div className="health-score-content">

          <div
            className={`health-rating ${
              (healthScore?.rating || "")
                .toLowerCase()
                .replaceAll(" ", "-")
            }`}
          >
            {healthScore?.rating || "Calculating..."}
          </div>

          <div className="health-score-bar">

            <div
              className="health-score-fill"
              style={{
                width: `${healthScore?.score || 0}%`,
              }}
            ></div>

          </div>

          <div className="health-components">

            <div>
              <span>Savings</span>
              <strong>
                {healthScore?.component_scores?.savings || 0}/40
              </strong>
            </div>

            <div>
              <span>Expenses</span>
              <strong>
                {healthScore?.component_scores?.expenses || 0}/25
              </strong>
            </div>

            <div>
              <span>Budget</span>
              <strong>
                {healthScore?.component_scores?.budget || 0}/20
              </strong>
            </div>

            <div>
              <span>Goals</span>
              <strong>
                {healthScore?.component_scores?.savings_goals || 0}/15
              </strong>
            </div>

          </div>

        </div>

      </section>

      {/* AI Financial Insights */}

      <section className="dashboard-section ai-insights-section">

        <div className="section-header">

          <div>
            <h2>🤖 PennyWise Insights</h2>

            <p>
              Personalized recommendations based on your financial activity
            </p>
          </div>

          <div className="insight-rate">
            Savings Rate:{" "}
            <strong>
              {Number(
                summary?.total_income || 0
              ) > 0
                ? (
                    (
                      (
                        Number(summary?.total_income || 0) -
                        Number(summary?.total_expenses || 0)
                      ) /
                      Number(summary?.total_income || 0)
                    ) *
                    100
                  ).toFixed(1)
                : "0.0"}
              %
            </strong>
          </div>

        </div>

        {financialInsights.length === 0 ? (

          <div className="empty-state">
            <p>
              Add more financial data to receive personalized insights.
            </p>
          </div>

        ) : (

          <div className="insights-list">

            {financialInsights.map(
              (insight, index) => (

                <div
                  className={`insight-card ${insight.type}`}
                  key={index}
                >

                  <div className="insight-icon">

                    {insight.type === "positive" && "✓"}

                    {insight.type === "suggestion" && "💡"}

                    {insight.type === "warning" && "!"}

                    {insight.type === "info" && "i"}

                  </div>

                  <div className="insight-content">

                    <h3>
                      {insight.title}
                    </h3>

                    <p>
                      {insight.message}
                    </p>

                  </div>

                </div>

              )
            )}

          </div>

        )}

      </section>

      {/* Charts */}

      <section className="charts-grid">

        {/* Category Chart */}

        <div className="dashboard-section chart-card">

          <h2>Spending by Category</h2>

          {categoryChartData.length === 0 ? (
            <div className="empty-state">
              <p>
                No expense data available.
              </p>
            </div>
          ) : (
            <div className="chart-container">

              <ResponsiveContainer
                width="100%"
                height={300}
              >
                <PieChart>

                  <Pie
                    data={categoryChartData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label
                  >
                    {categoryChartData.map(
                      (_, index) => (
                        <Cell
                          key={`cell-${index}`}
                        />
                      )
                    )}
                  </Pie>

                  <Tooltip
                    formatter={(value) =>
                      `₹${Number(
                        value
                      ).toFixed(2)}`
                    }
                  />

                  <Legend />

                </PieChart>
              </ResponsiveContainer>

            </div>
          )}

        </div>

        {/* Monthly Chart */}

        <div className="dashboard-section chart-card">

          <h2>Monthly Spending</h2>

          {monthlyChartData.length === 0 ? (
            <div className="empty-state">
              <p>
                No monthly spending data available.
              </p>
            </div>
          ) : (
            <div className="chart-container">

              <ResponsiveContainer
                width="100%"
                height={300}
              >
                <LineChart
                  data={monthlyChartData}
                >

                  <CartesianGrid
                    strokeDasharray="3 3"
                  />

                  <XAxis
                    dataKey="month"
                  />

                  <YAxis />

                  <Tooltip
                    formatter={(value) =>
                      `₹${Number(
                        value
                      ).toFixed(2)}`
                    }
                  />

                  <Line
                    type="monotone"
                    dataKey="spending"
                    strokeWidth={3}
                  />

                </LineChart>

              </ResponsiveContainer>

            </div>
          )}

        </div>

      </section>

      {/* Recent Transactions */}

      <section className="dashboard-section">

        <div className="section-header">

          <div>
            <h2>Recent Transactions</h2>

            <p>
              Your latest financial activity
            </p>
          </div>

          <button
            className="view-all-button"
            onClick={() => {
              window.location.href =
                "/transactions";
            }}
          >
            View All
          </button>

        </div>

        {recentTransactions.length === 0 ? (

          <div className="empty-state">
            <p>
              No transactions available.
            </p>
          </div>

        ) : (

          <div className="recent-transactions">

            {recentTransactions.map(
              (transaction) => (

                <div
                  className="recent-transaction"
                  key={transaction.id}
                >

                  <div className="recent-transaction-main">

                    <div
                      className={`recent-transaction-icon ${transaction.type}`}
                    >
                      {transaction.type ===
                      "income"
                        ? "+"
                        : "-"}
                    </div>

                    <div>

                      <h3>
                        {transaction.merchant ||
                          transaction.description ||
                          "Transaction"}
                      </h3>

                      <p>
                        {formatDate(
                          transaction.date
                        )}

                        {" • "}

                        {transaction.category ||
                          "Uncategorized"}

                        {" • "}

                        {transaction.payment_method ||
                          "Unknown"}
                      </p>

                    </div>

                  </div>

                  <strong
                    className={`recent-transaction-amount ${transaction.type}`}
                  >
                    {transaction.type ===
                    "income"
                      ? "+"
                      : "-"}
                    ₹
                    {Number(
                      transaction.amount
                    ).toFixed(2)}
                  </strong>

                </div>

              )
            )}

          </div>

        )}

      </section>

      {/* Budget Section */}

      <section className="dashboard-section">

        <div className="section-header">

          <h2>Budget Tracking</h2>

          <button
            className="view-all-button"
            onClick={() => {
              window.location.href =
                "/budgets";
            }}
          >
            Manage Budgets
          </button>

        </div>

        {budgetUsage.length === 0 ? (

          <div className="empty-state">
            <p>
              No budgets created yet.
            </p>
          </div>

        ) : (

          <div className="budget-list">

            {budgetUsage.map((item) => {

              const percentage = Math.min(
                Number(
                  item.percentage_used
                ),
                100
              );

              return (
                <div
                  className="budget-item"
                  key={item.budget_id}
                >

                  <div className="budget-top">

                    <div>
                      <h3>
                        {item.category}
                      </h3>

                      <span>
                        {item.month}
                      </span>
                    </div>

                    <strong>
                      {item.percentage_used}%
                    </strong>

                  </div>

                  <div className="progress-bar">

                    <div
                      className="progress-fill"
                      style={{
                        width:
                          `${percentage}%`,
                      }}
                    ></div>

                  </div>

                  <div className="budget-details">

                    <span>
                      Spent ₹
                      {Number(
                        item.spent
                      ).toFixed(2)}
                    </span>

                    <span>
                      Budget ₹
                      {Number(
                        item.budget_amount
                      ).toFixed(2)}
                    </span>

                    <span>
                      Remaining ₹
                      {Number(
                        item.remaining
                      ).toFixed(2)}
                    </span>

                  </div>

                </div>
              );
            })}

          </div>
        )}

      </section>

      {/* Savings Goals */}

      <section className="dashboard-section">

        <div className="section-header">

          <h2>Savings Goals</h2>

          <button
            className="view-all-button"
            onClick={() => {
              window.location.href =
                "/savings-goals";
            }}
          >
            Manage Goals
          </button>

        </div>

        {savingsProgress.length === 0 ? (

          <div className="empty-state">
            <p>
              No savings goals created yet.
            </p>
          </div>

        ) : (

          <div className="savings-list">

            {savingsProgress.map(
              (goal) => {

                const percentage =
                  Math.min(
                    Number(
                      goal.percentage_completed
                    ),
                    100
                  );

                return (
                  <div
                    className="savings-item"
                    key={goal.goal_id}
                  >

                    <div className="savings-top">

                      <div>
                        <h3>
                          {goal.goal_name}
                        </h3>

                        <span>
                          Target ₹
                          {Number(
                            goal.target_amount
                          ).toFixed(2)}
                        </span>
                      </div>

                      <strong>
                        {
                          goal.percentage_completed
                        }%
                      </strong>

                    </div>

                    <div className="progress-bar">

                      <div
                        className="savings-progress-fill"
                        style={{
                          width:
                            `${percentage}%`,
                        }}
                      ></div>

                    </div>

                    <div className="savings-details">

                      <span>
                        Saved ₹
                        {Number(
                          goal.current_amount
                        ).toFixed(2)}
                      </span>

                      <span>
                        Remaining ₹
                        {Number(
                          goal.remaining_amount
                        ).toFixed(2)}
                      </span>

                    </div>

                  </div>
                );
              }
            )}

          </div>
        )}

      </section>

    </div>
  );
}

export default Dashboard;