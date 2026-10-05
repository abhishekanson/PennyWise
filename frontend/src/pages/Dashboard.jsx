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
} from "recharts";

import API from "../api";

function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [categorySpending, setCategorySpending] = useState([]);
  const [monthlySpending, setMonthlySpending] = useState([]);
  const [budgetUsage, setBudgetUsage] = useState([]);
  const [savingsProgress, setSavingsProgress] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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
        ] = await Promise.all([
          API.get("/analysis/summary"),
          API.get("/analysis/category-spending"),
          API.get("/analysis/monthly-spending"),
          API.get("/analysis/budget-usage"),
          API.get("/analysis/savings-progress"),
        ]);

        setSummary(summaryResponse.data);
        setCategorySpending(categoryResponse.data);
        setMonthlySpending(monthlyResponse.data);
        setBudgetUsage(budgetResponse.data);
        setSavingsProgress(savingsResponse.data);
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
  }, []);


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

  const categoryChartData = categorySpending.map((item) => ({
    name: item.category,
    value: Number(item.total),
  }));

  const monthlyChartData = monthlySpending.map((item) => ({
    month: item.month,
    spending: Number(item.total),
  }));

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
                <button
                className="quick-action-button"
                onClick={() => {
                    window.location.href = "/transactions";
                }}
                >
                + Add Transaction
                </button>

                <button
                className="quick-action-button secondary"
                onClick={() => {
                    window.location.href = "/budgets";
                }}
                >
                + Create Budget
                </button>
            </div>
        </header>

      {/* Summary Cards */}
      <section className="summary-grid">

        <div className="summary-card income-card">
          <div className="card-icon">₹</div>

          <div>
            <h3>Total Income</h3>

            <p>
              ₹{Number(summary?.total_income || 0).toFixed(2)}
            </p>
          </div>
        </div>

        <div className="summary-card expense-card">
          <div className="card-icon">↓</div>

          <div>
            <h3>Total Expenses</h3>

            <p>
              ₹{Number(summary?.total_expenses || 0).toFixed(2)}
            </p>
          </div>
        </div>

        <div className="summary-card balance-card">
          <div className="card-icon">=</div>

          <div>
            <h3>Current Balance</h3>

            <p>
              ₹{Number(summary?.balance || 0).toFixed(2)}
            </p>
          </div>
        </div>

      </section>

      {/* Charts */}
      <section className="charts-grid">

        {/* Category Chart */}
        <div className="dashboard-section chart-card">

          <h2>Spending by Category</h2>

          {categoryChartData.length === 0 ? (
            <div className="empty-state">
              <p>No expense data available.</p>
            </div>
          ) : (
            <div className="chart-container">

              <ResponsiveContainer width="100%" height={300}>
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
                    {categoryChartData.map((_, index) => (
                      <Cell
                        key={`cell-${index}`}
                      />
                    ))}
                  </Pie>

                  <Tooltip
                    formatter={(value) =>
                      `₹${Number(value).toFixed(2)}`
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
              <p>No monthly spending data available.</p>
            </div>
          ) : (
            <div className="chart-container">

              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={monthlyChartData}>

                  <CartesianGrid strokeDasharray="3 3" />

                  <XAxis dataKey="month" />

                  <YAxis />

                  <Tooltip
                    formatter={(value) =>
                      `₹${Number(value).toFixed(2)}`
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

      {/* Budget Section */}
      <section className="dashboard-section">

        <div className="section-header">
          <h2>Budget Tracking</h2>
        </div>

        {budgetUsage.length === 0 ? (
          <div className="empty-state">
            <p>No budgets created yet.</p>
          </div>
        ) : (
          <div className="budget-list">

            {budgetUsage.map((item) => {

              const percentage = Math.min(
                Number(item.percentage_used),
                100
              );

              return (
                <div
                  className="budget-item"
                  key={item.budget_id}
                >

                  <div className="budget-top">

                    <div>
                      <h3>{item.category}</h3>

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
                        width: `${percentage}%`,
                      }}
                    ></div>
                  </div>

                  <div className="budget-details">

                    <span>
                      Spent ₹
                      {Number(item.spent).toFixed(2)}
                    </span>

                    <span>
                      Budget ₹
                      {Number(item.budget_amount).toFixed(2)}
                    </span>

                    <span>
                      Remaining ₹
                      {Number(item.remaining).toFixed(2)}
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
        </div>

        {savingsProgress.length === 0 ? (
          <div className="empty-state">
            <p>No savings goals created yet.</p>
          </div>
        ) : (
          <div className="savings-list">

            {savingsProgress.map((goal) => {

              const percentage = Math.min(
                Number(goal.percentage_completed),
                100
              );

              return (
                <div
                  className="savings-item"
                  key={goal.goal_id}
                >

                  <div className="savings-top">

                    <div>
                      <h3>{goal.goal_name}</h3>

                      <span>
                        Target ₹
                        {Number(
                          goal.target_amount
                        ).toFixed(2)}
                      </span>
                    </div>

                    <strong>
                      {goal.percentage_completed}%
                    </strong>

                  </div>

                  <div className="progress-bar">
                    <div
                      className="savings-progress-fill"
                      style={{
                        width: `${percentage}%`,
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
            })}

          </div>
        )}

      </section>

    </div>
  );
}

export default Dashboard;