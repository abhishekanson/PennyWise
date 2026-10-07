import { useEffect, useMemo, useState } from "react";
import API from "../api";

function Transactions() {
  const emptyForm = {
    amount: "",
    type: "expense",
    description: "",
    merchant: "",
    category: "",
    date: "",
    payment_method: "",
  };

  const [transactions, setTransactions] = useState([]);
  const [form, setForm] = useState(emptyForm);

  const [editingId, setEditingId] = useState(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [categorizing, setCategorizing] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Filters
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [paymentFilter, setPaymentFilter] = useState("all");
  const [sourceFilter, setSourceFilter] = useState("all");

  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [minAmount, setMinAmount] = useState("");
  const [maxAmount, setMaxAmount] = useState("");
  const [sortBy, setSortBy] = useState("date_desc");

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await API.get("/transactions/");

      setTransactions(response.data);
    } catch (error) {
      console.error(error);

      if (error.response?.status === 401) {
        localStorage.removeItem("token");
        window.location.href = "/login";
      } else {
        setError(
          error.response?.data?.detail ||
            "Failed to load transactions"
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAICategorization = async () => {
    if (!form.description && !form.merchant) {
      setError(
        "Enter a description or merchant first."
      );
      return;
    }

    try {
      setCategorizing(true);
      setError("");
      setSuccess("");

      const text = [
        form.description,
        form.merchant,
      ]
        .filter(Boolean)
        .join(" ");

      const response = await API.post(
        "/ai/categorize",
        {
          description: text,
        }
      );

      setForm({
        ...form,
        category: response.data.category,
      });

      setSuccess(
        `AI suggested: ${response.data.category} (${response.data.confidence}% confidence)`
      );
    } catch (error) {
      console.error(error);

      setError(
        error.response?.data?.detail ||
          "AI categorization failed"
      );
    } finally {
      setCategorizing(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
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
      const transactionData = {
        amount: Number(form.amount),
        type: form.type,
        description: form.description || null,
        merchant: form.merchant || null,
        category: form.category || null,
        date: form.date,
        payment_method: form.payment_method || null,
      };

      if (editingId) {
        await API.put(
          `/transactions/${editingId}`,
          transactionData
        );

        setSuccess(
          "Transaction updated successfully."
        );
      } else {
        await API.post(
          "/transactions/",
          transactionData
        );

        setSuccess(
          "Transaction added successfully."
        );
      }

      setForm(emptyForm);
      setEditingId(null);

      await fetchTransactions();
    } catch (error) {
      console.error(error);

      setError(
        error.response?.data?.detail ||
          "Failed to save transaction"
      );
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (transaction) => {
    setEditingId(transaction.id);

    setForm({
      amount: transaction.amount,
      type: transaction.type,
      description: transaction.description || "",
      merchant: transaction.merchant || "",
      category: transaction.category || "",
      date: transaction.date,
      payment_method:
        transaction.payment_method || "",
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
      "Are you sure you want to delete this transaction?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");
      setSuccess("");

      await API.delete(
        `/transactions/${id}`
      );

      setSuccess(
        "Transaction deleted successfully."
      );

      if (editingId === id) {
        handleCancelEdit();
      }

      await fetchTransactions();
    } catch (error) {
      console.error(error);

      setError(
        error.response?.data?.detail ||
          "Failed to delete transaction"
      );
    }
  };

  const formatDate = (date) => {
    if (!date) return "";

    return new Date(
      `${date}T00:00:00`
    ).toLocaleDateString("en-IN");
  };

  // Get unique categories
  const categories = useMemo(() => {
    return [
      ...new Set(
        transactions
          .map((transaction) => transaction.category)
          .filter(Boolean)
      ),
    ].sort();
  }, [transactions]);

  // Get unique payment methods
  const paymentMethods = useMemo(() => {
    return [
      ...new Set(
        transactions
          .map(
            (transaction) =>
              transaction.payment_method
          )
          .filter(Boolean)
      ),
    ].sort();
  }, [transactions]);

  // Filter transactions
  const filteredTransactions = useMemo(() => {
    const searchText = search
      .trim()
      .toLowerCase();

    const minimumAmount =
      minAmount === ""
        ? null
        : Number(minAmount);

    const maximumAmount =
      maxAmount === ""
        ? null
        : Number(maxAmount);

    const filtered = transactions.filter(
      (transaction) => {
        const matchesSearch =
          !searchText ||
          [
            transaction.description,
            transaction.merchant,
            transaction.category,
            transaction.payment_method,
          ]
            .filter(Boolean)
            .some((value) =>
              value
                .toLowerCase()
                .includes(searchText)
            );

        const matchesType =
          typeFilter === "all" ||
          transaction.type === typeFilter;

        const matchesCategory =
          categoryFilter === "all" ||
          transaction.category === categoryFilter;

        const matchesPayment =
          paymentFilter === "all" ||
          transaction.payment_method === paymentFilter;

        const matchesSource =
          sourceFilter === "all" ||
          transaction.source === sourceFilter;

        const matchesFromDate =
          !fromDate ||
          transaction.date >= fromDate;

        const matchesToDate =
          !toDate ||
          transaction.date <= toDate;

        const amount = Number(
          transaction.amount || 0
        );

        const matchesMinAmount =
          minimumAmount === null ||
          amount >= minimumAmount;

        const matchesMaxAmount =
          maximumAmount === null ||
          amount <= maximumAmount;

        return (
          matchesSearch &&
          matchesType &&
          matchesCategory &&
          matchesPayment &&
          matchesSource &&
          matchesFromDate &&
          matchesToDate &&
          matchesMinAmount &&
          matchesMaxAmount
        );
      }
    );

    return filtered.sort((a, b) => {
      if (sortBy === "date_desc") {
        return (
          new Date(b.date) -
          new Date(a.date)
        );
      }

      if (sortBy === "date_asc") {
        return (
          new Date(a.date) -
          new Date(b.date)
        );
      }

      if (sortBy === "amount_desc") {
        return (
          Number(b.amount || 0) -
          Number(a.amount || 0)
        );
      }

      if (sortBy === "amount_asc") {
        return (
          Number(a.amount || 0) -
          Number(b.amount || 0)
        );
      }

      if (sortBy === "description_asc") {
        return (
          (a.description || "")
            .toLowerCase()
            .localeCompare(
              (b.description || "").toLowerCase()
            )
        );
      }

      if (sortBy === "description_desc") {
          return (
            (b.description || "")
              .toLowerCase()
              .localeCompare(
                (a.description || "").toLowerCase()
              )
          );
        }

        if (sortBy === "income_first") {
          if (
            a.type === "income" &&
            b.type !== "income"
          ) {
            return -1;
          }

          if (
            a.type !== "income" &&
            b.type === "income"
          ) {
            return 1;
          }

          return 0;
        }

        if (sortBy === "expense_first") {
          if (
            a.type === "expense" &&
            b.type !== "expense"
          ) {
            return -1;
          }

          if (
            a.type !== "expense" &&
            b.type === "expense"
          ) {
            return 1;
          }

          return 0;
        }

        return 0;
    });
  }, [
    transactions,
    search,
    typeFilter,
    categoryFilter,
    paymentFilter,
    sourceFilter,
    fromDate,
    toDate,
    minAmount,
    maxAmount,
    sortBy,
  ]);

  const filteredTotals = useMemo(() => {
    const income = filteredTransactions
      .filter(
        (transaction) =>
          transaction.type === "income"
      )
      .reduce(
        (total, transaction) =>
          total + Number(transaction.amount || 0),
        0
      );

    const expenses = filteredTransactions
      .filter(
        (transaction) =>
          transaction.type === "expense"
      )
      .reduce(
        (total, transaction) =>
          total + Number(transaction.amount || 0),
        0
      );

    return {
      income,
      expenses,
      net: income - expenses,
    };
  }, [filteredTransactions]);

  const clearFilters = () => {
    setSearch("");
    setTypeFilter("all");
    setCategoryFilter("all");
    setPaymentFilter("all");
    setSourceFilter("all");
    setFromDate("");
    setToDate("");
    setMinAmount("");
    setMaxAmount("");
    setSortBy("date_desc");
  };

  return (
    <div className="transactions-page">

      {/* Header */}

      <div className="page-header">

        <div>
          <h1>Transactions</h1>

          <p>
            Manage your income and expenses
          </p>
        </div>

      </div>

      {/* Add / Edit Form */}

      <section className="transaction-form-card">

        <div className="form-title">

          <div>
            <h2>
              {editingId
                ? "Edit Transaction"
                : "Add Transaction"}
            </h2>

            <p>
              {editingId
                ? "Update the transaction details below."
                : "Record your income or expense."}
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
          className="transaction-form"
          onSubmit={handleSubmit}
        >

          <div className="form-row">

            <div className="form-group">

              <label>Type</label>

              <select
                name="type"
                value={form.type}
                onChange={handleChange}
              >
                <option value="expense">
                  Expense
                </option>

                <option value="income">
                  Income
                </option>
              </select>

            </div>

            <div className="form-group">

              <label>Amount</label>

              <input
                type="number"
                name="amount"
                value={form.amount}
                onChange={handleChange}
                placeholder="Enter amount"
                min="0.01"
                step="0.01"
                required
              />

            </div>

            <div className="form-group">

              <label>Date</label>

              <input
                type="date"
                name="date"
                value={form.date}
                onChange={handleChange}
                required
              />

            </div>

          </div>

          <div className="form-row">

            <div className="form-group">

              <label>Category</label>

              <select
                name="category"
                value={form.category}
                onChange={handleChange}
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

                <option value="Salary">
                  Salary
                </option>
              </select>

              <button
                type="button"
                className="ai-category-button"
                onClick={handleAICategorization}
                disabled={categorizing}
              >
                {categorizing
                  ? "Analyzing..."
                  : "✨ Suggest Category with AI"}
              </button>

            </div>

            <div className="form-group">

              <label>Merchant</label>

              <input
                type="text"
                name="merchant"
                value={form.merchant}
                onChange={handleChange}
                placeholder="e.g. Amazon"
              />

            </div>

            <div className="form-group">

              <label>Payment Method</label>

              <select
                name="payment_method"
                value={form.payment_method}
                onChange={handleChange}
              >
                <option value="">
                  Select method
                </option>

                <option value="Cash">
                  Cash
                </option>

                <option value="UPI">
                  UPI
                </option>

                <option value="Debit Card">
                  Debit Card
                </option>

                <option value="Credit Card">
                  Credit Card
                </option>

                <option value="Bank Transfer">
                  Bank Transfer
                </option>

              </select>

            </div>

          </div>

          <div className="form-group">

            <label>Description</label>

            <textarea
              name="description"
              value={form.description}
              onChange={handleChange}
              placeholder="Optional description"
              rows="3"
            />

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
                ? "Update Transaction"
                : "Add Transaction"}
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

      <div className="transaction-filter-summary">

        <div className="filter-summary-card income">

          <div className="filter-summary-label">
            Filtered Income
          </div>

          <div className="filter-summary-value">
            +₹
            {filteredTotals.income.toLocaleString(
              "en-IN",
              {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              }
            )}
          </div>

        </div>


        <div className="filter-summary-card expense">

          <div className="filter-summary-label">
            Filtered Expenses
          </div>

          <div className="filter-summary-value">
            -₹
            {filteredTotals.expenses.toLocaleString(
              "en-IN",
              {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              }
            )}
          </div>

        </div>


        <div
          className={`filter-summary-card ${
            filteredTotals.net >= 0
              ? "net-positive"
              : "net-negative"
          }`}
        >

          <div className="filter-summary-label">
            Net Amount
          </div>

          <div className="filter-summary-value">
            {filteredTotals.net >= 0
              ? "+"
              : "-"}
            ₹
            {Math.abs(
              filteredTotals.net
            ).toLocaleString(
              "en-IN",
              {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              }
            )}
          </div>

        </div>

      </div>

      {/* Transaction History */}

      <section className="transaction-list-card">

        <div className="transaction-list-header">

          <div>
            <h2>Transaction History</h2>

            <p>
              Showing{" "}
              {filteredTransactions.length} of{" "}
              {transactions.length} transactions
            </p>
          </div>

          <button
            className="refresh-button"
            onClick={fetchTransactions}
          >
            Refresh
          </button>

        </div>

        {/* Filters */}

        <div className="transaction-filters">

          <div className="filter-group search-filter">

            <label>Search</label>

            <input
              type="text"
              value={search}
              onChange={(e) =>
                setSearch(e.target.value)
              }
              placeholder="Search merchant or description..."
            />

          </div>

          <div className="filter-group">

            <label>Type</label>

            <select
              value={typeFilter}
              onChange={(e) =>
                setTypeFilter(e.target.value)
              }
            >
              <option value="all">
                All Types
              </option>

              <option value="income">
                Income
              </option>

              <option value="expense">
                Expense
              </option>

            </select>

          </div>

          <div className="filter-group">

            <label>Category</label>

            <select
              value={categoryFilter}
              onChange={(e) =>
                setCategoryFilter(
                  e.target.value
                )
              }
            >
              <option value="all">
                All Categories
              </option>

              {categories.map(
                (category) => (
                  <option
                    key={category}
                    value={category}
                  >
                    {category}
                  </option>
                )
              )}

            </select>

          </div>

          <div className="filter-group">

            <label>Payment</label>

            <select
              value={paymentFilter}
              onChange={(e) =>
                setPaymentFilter(
                  e.target.value
                )
              }
            >
              <option value="all">
                All Methods
              </option>

              {paymentMethods.map(
                (method) => (
                  <option
                    key={method}
                    value={method}
                  >
                    {method}
                  </option>
                )
              )}

            </select>

          </div>

          <div className="filter-group">

            <label>Source</label>

            <select
              value={sourceFilter}
              onChange={(e) =>
                setSourceFilter(
                  e.target.value
                )
              }
            >
              <option value="all">
                All Sources
              </option>

              <option value="manual">
                Manual
              </option>

              <option value="csv">
                CSV
              </option>

              <option value="pdf">
                PDF
              </option>

            </select>

          </div>

          <div className="filter-group">

            <label>Sort By</label>

            <select
              value={sortBy}
              onChange={(e) =>
                setSortBy(e.target.value)
              }
            >
              <option value="income_first">
                Income — First
              </option>

              <option value="expense_first">
                Expenses — First
              </option>
              
              <option value="date_desc">
                Date — Newest First
              </option>

              <option value="date_asc">
                Date — Oldest First
              </option>

              <option value="amount_desc">
                Amount — Highest First
              </option>

              <option value="amount_asc">
                Amount — Lowest First
              </option>

              <option value="description_asc">
                Description — A to Z
              </option>

              <option value="description_desc">
                Description — Z to A
              </option>
            </select>

          </div>
          
          <div className="filter-group">

            <label>From Date</label>

            <input
              type="date"
              value={fromDate}
              onChange={(e) =>
                setFromDate(e.target.value)
              }
            />

          </div>

          <div className="filter-group">

            <label>To Date</label>

            <input
              type="date"
              value={toDate}
              onChange={(e) =>
                setToDate(e.target.value)
              }
            />

          </div>

          <div className="filter-group">

            <label>Min Amount</label>

            <input
              type="number"
              min="0"
              step="0.01"
              value={minAmount}
              onChange={(e) =>
                setMinAmount(e.target.value)
              }
              placeholder="₹0"
            />

          </div>

          <div className="filter-group">

            <label>Max Amount</label>

            <input
              type="number"
              min="0"
              step="0.01"
              value={maxAmount}
              onChange={(e) =>
                setMaxAmount(e.target.value)
              }
              placeholder="₹0"
            />

          </div>

          <button
            type="button"
            className="clear-filters-button"
            onClick={clearFilters}
          >
            Clear Filters
          </button>

        </div>

        {loading ? (

          <div className="transaction-empty">
            <p>Loading transactions...</p>
          </div>

        ) : transactions.length === 0 ? (

          <div className="transaction-empty">

            <p>No transactions yet.</p>

            <span>
              Add your first income or expense above.
            </span>

          </div>

        ) : filteredTransactions.length === 0 ? (

          <div className="transaction-empty">

            <p>No matching transactions.</p>

            <span>
              Try changing or clearing the filters.
            </span>

          </div>

        ) : (

          <div className="transaction-table-wrapper">

            <table className="transaction-table">

              <thead>

                <tr>
                  <th>Date</th>
                  <th>Type</th>
                  <th>Category</th>
                  <th>Description</th>
                  <th>Payment</th>
                  <th>Source</th>
                  <th>Amount</th>
                  <th>Actions</th>
                </tr>

              </thead>

              <tbody>

                {filteredTransactions.map(
                  (transaction) => (

                    <tr
                      key={transaction.id}
                    >

                      <td>
                        {formatDate(
                          transaction.date
                        )}
                      </td>

                      <td>

                        <span
                          className={`transaction-type ${
                            transaction.type
                          }`}
                        >
                          {transaction.type}
                        </span>

                      </td>

                      <td>
                        {transaction.category ||
                          "Uncategorized"}
                      </td>

                      <td>
                        {transaction.description ||
                          transaction.merchant ||
                          "-"}
                      </td>

                      <td>
                        {transaction.payment_method ||
                          "-"}
                      </td>

                      <td>
                        <span
                          className={`transaction-source ${
                            transaction.source ||
                            "manual"
                          }`}
                        >
                          {transaction.source ||
                            "manual"}
                        </span>
                      </td>

                      <td
                        className={`transaction-amount ${
                          transaction.type
                        }`}
                      >

                        {transaction.type ===
                        "income"
                          ? "+"
                          : "-"}

                        ₹
                        {Number(
                          transaction.amount
                        ).toFixed(2)}

                      </td>

                      <td>

                        <div className="action-buttons">

                          <button
                            className="edit-button"
                            onClick={() =>
                              handleEdit(
                                transaction
                              )
                            }
                          >
                            Edit
                          </button>

                          <button
                            className="delete-button"
                            onClick={() =>
                              handleDelete(
                                transaction.id
                              )
                            }
                          >
                            Delete
                          </button>

                        </div>

                      </td>

                    </tr>

                  )
                )}

              </tbody>

            </table>

          </div>

        )}

      </section>

    </div>
  );
}

export default Transactions;