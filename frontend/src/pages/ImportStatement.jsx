import { useState } from "react";
import API from "../api";

function ImportStatement() {
  const [importType, setImportType] = useState("pdf");
  const [file, setFile] = useState(null);

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [result, setResult] = useState(null);
  const [transactions, setTransactions] = useState([]);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    setFile(selectedFile);
    setMessage("");
    setError("");
    setResult(null);
    setTransactions([]);
  };

  const handleImport = async () => {
    if (!file) {
      setError("Please select a file first.");
      return;
    }

    setLoading(true);
    setMessage("");
    setError("");
    setResult(null);
    setTransactions([]);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const endpoint =
        importType === "pdf"
          ? "/imports/pdf"
          : "/imports/csv";

      const response = await API.post(
        endpoint,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setResult(response.data);

      setMessage(
        response.data.message ||
        "Import completed successfully."
      );

      // Load transactions after import
      const transactionsResponse =
        await API.get("/transactions/");

      setTransactions(
        transactionsResponse.data
      );

      setFile(null);

      // Reset file input
      const fileInput =
        document.getElementById(
          "statement-file"
        );

      if (fileInput) {
        fileInput.value = "";
      }

    } catch (err) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
        "Import failed. Please try again."
      );

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">

      <div className="page-header">
        <div>
          <h1>Import Statement</h1>

          <p>
            Import transactions from a bank statement
            using PDF or CSV.
          </p>
        </div>
      </div>

      {/* Import type selector */}

      <div className="import-type-selector">

        <button
          className={
            importType === "pdf"
              ? "import-type-button active"
              : "import-type-button"
          }
          onClick={() => {
            setImportType("pdf");
            setFile(null);
            setResult(null);
            setError("");
            setMessage("");
          }}
        >
          PDF Statement
        </button>

        <button
          className={
            importType === "csv"
              ? "import-type-button active"
              : "import-type-button"
          }
          onClick={() => {
            setImportType("csv");
            setFile(null);
            setResult(null);
            setError("");
            setMessage("");
          }}
        >
          CSV Statement
        </button>

      </div>

      {/* Upload card */}

      <div className="import-card">

        <h2>
          {importType === "pdf"
            ? "Upload Bank Statement PDF"
            : "Upload Transaction CSV"}
        </h2>

        <p className="import-description">
          {importType === "pdf"
            ? "Upload a scanned or digital bank statement. PennyWise will extract transactions using OCR."
            : "Upload a CSV file containing your transaction records."}
        </p>

        <input
          id="statement-file"
          type="file"
          accept={
            importType === "pdf"
              ? ".pdf"
              : ".csv"
          }
          onChange={handleFileChange}
        />

        {file && (
          <div className="selected-file">
            <strong>Selected file:</strong>{" "}
            {file.name}
          </div>
        )}

        <button
          className="import-button"
          onClick={handleImport}
          disabled={loading || !file}
        >
          {loading
            ? "Importing..."
            : `Import ${importType.toUpperCase()}`}
        </button>

      </div>

      {/* Success message */}

      {message && (
        <div className="import-success">
          {message}
        </div>
      )}

      {/* Error message */}

      {error && (
        <div className="import-error">
          {error}
        </div>
      )}

      {/* Import result */}

      {result && (
        <div className="import-result">

          <h2>Import Summary</h2>

          <div className="import-summary-grid">

            <div className="import-summary-card">
              <span>Detected</span>
              <strong>
                {result.transactions_detected ?? "-"}
              </strong>
            </div>

            <div className="import-summary-card">
              <span>Imported</span>
              <strong>
                {result.imported ?? "-"}
              </strong>
            </div>

            <div className="import-summary-card">
              <span>Skipped</span>
              <strong>
                {result.skipped ?? "-"}
              </strong>
            </div>

            <div className="import-summary-card">
              <span>Errors</span>
              <strong>
                {result.errors?.length ?? 0}
              </strong>
            </div>

          </div>

          {result.errors &&
            result.errors.length > 0 && (
              <div className="import-errors">

                <h3>Import Errors</h3>

                {result.errors.map(
                  (item, index) => (
                    <div
                      key={index}
                      className="import-error-item"
                    >
                      Row {item.row}:{" "}
                      {item.error}
                    </div>
                  )
                )}

              </div>
            )}

        </div>
      )}

      {/* Transactions */}

      {transactions.length > 0 && (
        <div className="import-transactions">

          <div className="section-header">
            <h2>Transactions</h2>

            <span className="transactions-detected">
              {transactions.length} transactions
            </span>
          </div>

          <div className="transaction-table-wrapper">

            <table className="transaction-table">

              <thead>
                <tr>
                  <th>Date</th>
                  <th>Description</th>
                  <th>Merchant</th>
                  <th>Category</th>
                  <th>Payment</th>
                  <th>Type</th>
                  <th>Amount</th>
                </tr>
              </thead>

              <tbody>

                {transactions.map(
                  (transaction) => (
                    <tr key={transaction.id}>

                      <td>
                        {transaction.date}
                      </td>

                      <td>
                        {transaction.description ||
                          "-"}
                      </td>

                      <td>
                        {transaction.merchant ||
                          "-"}
                      </td>

                      <td>
                        {transaction.category ||
                          "-"}
                      </td>

                      <td>
                        {transaction.payment_method ||
                          "-"}
                      </td>

                      <td>
                        <span
                          className={
                            transaction.type ===
                            "income"
                              ? "transaction-income"
                              : "transaction-expense"
                          }
                        >
                          {transaction.type}
                        </span>
                      </td>

                      <td>
                        ₹
                        {Number(
                          transaction.amount
                        ).toFixed(2)}
                      </td>

                    </tr>
                  )
                )}

              </tbody>

            </table>

          </div>

        </div>
      )}

    </div>
  );
}

export default ImportStatement;