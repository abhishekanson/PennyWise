import { useEffect, useState } from "react";
import API from "../api";

function Budgets() {
  const emptyForm = {
    category: "",
    amount: "",
    month: "",
  };

  const [budgets, setBudgets] = useState([]);
  const [form, setForm] = useState(emptyForm);

  const [editingId, setEditingId] = useState(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const fetchBudgets = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await API.get("/budgets/");

      setBudgets(response.data);
    } catch (error) {
      console.error(error);

      if (error.response?.status === 401) {
        localStorage.removeItem("token");
        window.location.href = "/login";
      } else {
        setError(
          error.response?.data?.detail ||
            "Failed to load budgets"
        );
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBudgets();
  }, []);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");
    setSaving(true);

    try {
      const budgetData = {
        category: form.category,
        amount: Number(form.amount),
        month: form.month,
      };

      if (editingId) {
        await API.put(
          `/budgets/${editingId}`,
          budgetData
        );

        setSuccess(
          "Budget updated successfully."
        );
      } else {
        await API.post(
          "/budgets/",
          budgetData
        );

        setSuccess(
          "Budget created successfully."
        );
      }

      setForm(emptyForm);
      setEditingId(null);

      await fetchBudgets();

    } catch (error) {
      console.error(error);

      setError(
        error.response?.data?.detail ||
          "Failed to save budget"
      );
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (budget) => {
    setEditingId(budget.id);

    setForm({
      category: budget.category,
      amount: budget.amount,
      month: budget.month,
    });

    setError("");
    setSuccess("");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setForm(emptyForm);

    setError("");
    setSuccess("");
  };

  const handleDelete = async (id) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this budget?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");
      setSuccess("");

      await API.delete(
        `/budgets/${id}`
      );

      setSuccess(
        "Budget deleted successfully."
      );

      if (editingId === id) {
        handleCancelEdit();
      }

      await fetchBudgets();

    } catch (error) {
      console.error(error);

      setError(
        error.response?.data?.detail ||
          "Failed to delete budget"
      );
    }
  };

  return (
    <div className="budgets-page">

      {/* Header */}

      <div className="page-header">

        <div>
          <h1>Budgets</h1>

          <p>
            Plan and manage your monthly spending
          </p>
        </div>

      </div>

      {/* Form */}

      <section className="budget-form-card">

        <div className="form-title">

          <div>
            <h2>
              {editingId
                ? "Edit Budget"
                : "Create Budget"}
            </h2>

            <p>
              {editingId
                ? "Update your budget details."
                : "Set a spending limit for a category."}
            </p>
          </div>

          {editingId && (
            <button
              type="button"
              className="cancel-edit-button"
              onClick={handleCancelEdit}
            >
              Cancel Edit
            </button>
          )}

        </div>

        <form
          className="budget-form"
          onSubmit={handleSubmit}
        >

          <div className="form-row">

            <div className="form-group">

              <label>Category</label>

              <select
                name="category"
                value={form.category}
                onChange={handleChange}
                required
              >
                <option value="">
                  Select category
                </option>

                <option value="Food">
                  Food
                </option>

                <option value="Transport">
                  Transport
                </option>

                <option value="Shopping">
                  Shopping
                </option>

                <option value="Bills">
                  Bills
                </option>

                <option value="Entertainment">
                  Entertainment
                </option>

                <option value="Education">
                  Education
                </option>

                <option value="Health">
                  Health
                </option>

                <option value="Travel">
                  Travel
                </option>

                <option value="Other">
                  Other
                </option>

              </select>

            </div>

            <div className="form-group">

              <label>Budget Amount</label>

              <input
                type="number"
                name="amount"
                value={form.amount}
                onChange={handleChange}
                placeholder="Enter budget amount"
                min="0.01"
                step="0.01"
                required
              />

            </div>

            <div className="form-group">

              <label>Month</label>

              <input
                type="month"
                name="month"
                value={form.month}
                onChange={handleChange}
                required
              />

            </div>

          </div>

          <div className="form-actions">

            <button
              type="submit"
              className="add-transaction-button"
              disabled={saving}
            >
              {saving
                ? "Saving..."
                : editingId
                ? "Update Budget"
                : "Create Budget"}
            </button>

            {editingId && (
              <button
                type="button"
                className="secondary-button"
                onClick={handleCancelEdit}
              >
                Cancel
              </button>
            )}

          </div>

        </form>

        {success && (
          <p className="success-message">
            {success}
          </p>
        )}

        {error && (
          <p className="error-message">
            {error}
          </p>
        )}

      </section>

      {/* Budget List */}

      <section className="budget-list-card">

        <div className="budget-list-header">

          <div>
            <h2>Your Budgets</h2>

            <p>
              {budgets.length} budget
              {budgets.length !== 1
                ? "s"
                : ""}
            </p>
          </div>

          <button
            className="refresh-button"
            onClick={fetchBudgets}
          >
            Refresh
          </button>

        </div>

        {loading ? (

          <div className="budget-empty">
            <p>Loading budgets...</p>
          </div>

        ) : budgets.length === 0 ? (

          <div className="budget-empty">
            <p>No budgets created yet.</p>

            <span>
              Create your first budget above.
            </span>
          </div>

        ) : (

          <div className="budget-cards">

            {budgets.map((budget) => (

              <div
                className="budget-card"
                key={budget.id}
              >

                <div className="budget-card-header">

                  <div>

                    <h3>
                      {budget.category}
                    </h3>

                    <span>
                      {budget.month}
                    </span>

                  </div>

                  <strong>
                    ₹
                    {Number(
                      budget.amount
                    ).toFixed(2)}
                  </strong>

                </div>

                <div className="budget-card-actions">

                  <button
                    className="edit-button"
                    onClick={() =>
                      handleEdit(budget)
                    }
                  >
                    Edit
                  </button>

                  <button
                    className="delete-button"
                    onClick={() =>
                      handleDelete(
                        budget.id
                      )
                    }
                  >
                    Delete
                  </button>

                </div>

              </div>

            ))}

          </div>

        )}

      </section>

    </div>
  );
}

export default Budgets;