import { useEffect, useState } from "react";
import API from "../api";

function SavingsGoals() {
  const emptyForm = {
    goal_name: "",
    target_amount: "",
    current_amount: "",
    target_date: "",
  };

  const [goals, setGoals] = useState([]);
  const [form, setForm] = useState(emptyForm);

  const [editingId, setEditingId] = useState(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const fetchGoals = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await API.get("/savings-goals/");
      setGoals(response.data);
    } catch (error) {
      console.error(error);

      if (error.response?.status === 401) {
        localStorage.removeItem("token");
        window.location.href = "/login";
      } else {
        setError(
          error.response?.data?.detail ||
            "Failed to load savings goals"
        );
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGoals();
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
      const goalData = {
        goal_name: form.goal_name,
        target_amount: Number(form.target_amount),
        current_amount: Number(form.current_amount || 0),
        target_date: form.target_date || null,
      };

      if (editingId) {
        await API.put(
          `/savings-goals/${editingId}`,
          goalData
        );

        setSuccess(
          "Savings goal updated successfully."
        );
      } else {
        await API.post(
          "/savings-goals/",
          goalData
        );

        setSuccess(
          "Savings goal created successfully."
        );
      }

      setForm(emptyForm);
      setEditingId(null);

      await fetchGoals();
    } catch (error) {
      console.error(error);

      setError(
        error.response?.data?.detail ||
          "Failed to save savings goal"
      );
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (goal) => {
    setEditingId(goal.id);

    setForm({
      goal_name: goal.goal_name,
      target_amount: goal.target_amount,
      current_amount: goal.current_amount,
      target_date: goal.target_date || "",
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
      "Are you sure you want to delete this savings goal?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");
      setSuccess("");

      await API.delete(
        `/savings-goals/${id}`
      );

      setSuccess(
        "Savings goal deleted successfully."
      );

      if (editingId === id) {
        handleCancelEdit();
      }

      await fetchGoals();
    } catch (error) {
      console.error(error);

      setError(
        error.response?.data?.detail ||
          "Failed to delete savings goal"
      );
    }
  };

  return (
    <div className="savings-goals-page">
      <div className="page-header">
        <div>
          <h1>Savings Goals</h1>
          <p>
            Plan, track and achieve your financial goals
          </p>
        </div>

      </div>

      <section className="savings-form-card">
        <div className="form-title">
          <div>
            <h2>
              {editingId
                ? "Edit Savings Goal"
                : "Create Savings Goal"}
            </h2>

            <p>
              {editingId
                ? "Update your savings goal details."
                : "Set a target and start planning your savings."}
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
          className="savings-form"
          onSubmit={handleSubmit}
        >
          <div className="form-row">
            <div className="form-group">
              <label>Goal Name</label>

              <input
                type="text"
                name="goal_name"
                value={form.goal_name}
                onChange={handleChange}
                placeholder="e.g. New Laptop"
                required
              />
            </div>

            <div className="form-group">
              <label>Target Amount</label>

              <input
                type="number"
                name="target_amount"
                value={form.target_amount}
                onChange={handleChange}
                placeholder="Enter target amount"
                min="0.01"
                step="0.01"
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Current Savings</label>

              <input
                type="number"
                name="current_amount"
                value={form.current_amount}
                onChange={handleChange}
                placeholder="Enter current savings"
                min="0"
                step="0.01"
              />
            </div>

            <div className="form-group">
              <label>Target Date</label>

              <input
                type="date"
                name="target_date"
                value={form.target_date}
                onChange={handleChange}
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
                ? "Update Goal"
                : "Create Goal"}
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

      <section className="savings-list-card">
        <div className="savings-list-header">
          <div>
            <h2>Your Savings Goals</h2>

            <p>
              {goals.length} goal
              {goals.length !== 1 ? "s" : ""}
            </p>
          </div>

          <button
            className="refresh-button"
            onClick={fetchGoals}
          >
            Refresh
          </button>
        </div>

        {loading ? (
          <div className="savings-empty">
            <p>Loading savings goals...</p>
          </div>
        ) : goals.length === 0 ? (
          <div className="savings-empty">
            <p>No savings goals created yet.</p>

            <span>
              Create your first goal above.
            </span>
          </div>
        ) : (
          <div className="savings-goal-cards">
            {goals.map((goal) => {
              const target = Number(
                goal.target_amount
              );

              const current = Number(
                goal.current_amount
              );

              const percentage =
                target > 0
                  ? Math.min(
                      (current / target) * 100,
                      100
                    )
                  : 0;

              const remaining = Math.max(
                target - current,
                0
              );

              return (
                <div
                  className="savings-goal-card"
                  key={goal.id}
                >
                  <div className="savings-goal-header">
                    <div>
                      <h3>{goal.goal_name}</h3>

                      {goal.target_date && (
                        <span>
                          Target: {goal.target_date}
                        </span>
                      )}
                    </div>

                    <strong>
                      {percentage.toFixed(1)}%
                    </strong>
                  </div>

                  <div className="savings-progress-bar">
                    <div
                      className="savings-goal-progress-fill"
                      style={{
                        width: `${percentage}%`,
                      }}
                    ></div>
                  </div>

                  <div className="savings-goal-details">
                    <span>
                      Saved ₹
                      {current.toFixed(2)}
                    </span>

                    <span>
                      Target ₹
                      {target.toFixed(2)}
                    </span>

                    <span>
                      Remaining ₹
                      {remaining.toFixed(2)}
                    </span>
                  </div>

                  <div className="savings-goal-actions">
                    <button
                      className="edit-button"
                      onClick={() =>
                        handleEdit(goal)
                      }
                    >
                      Edit
                    </button>

                    <button
                      className="delete-button"
                      onClick={() =>
                        handleDelete(goal.id)
                      }
                    >
                      Delete
                    </button>
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

export default SavingsGoals;