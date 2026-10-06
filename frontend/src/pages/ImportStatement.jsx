import { useState } from "react";
import { Link } from "react-router-dom";
import API from "../api";

function ImportStatement() {
  const [file, setFile] = useState(null);

  const [fileType, setFileType] = useState("csv");

  const [uploading, setUploading] = useState(false);

  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];

    setFile(selectedFile || null);
    setResult(null);
    setError("");
  };

  const handleUpload = async (e) => {
    e.preventDefault();

    if (!file) {
      setError(
        `Please select a ${fileType.toUpperCase()} file.`
      );
      return;
    }

    setUploading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();

      formData.append(
        "file",
        file
      );

      const endpoint =
        fileType === "csv"
          ? "/imports/csv"
          : "/imports/pdf";

      const response = await API.post(
        endpoint,
        formData
      );

      setResult(response.data);

      setFile(null);

      e.target.reset();

    } catch (error) {
      console.error(error);

      if (error.response?.status === 401) {
        localStorage.removeItem("token");

        window.location.href = "/login";
      } else {
        setError(
          error.response?.data?.detail ||
          "Failed to import statement"
        );
      }

    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="import-page">

      <div className="page-header">

        <div>
          <h1>
            Import Bank Statement
          </h1>

          <p>
            Upload a CSV or PDF bank statement
            to automatically add your transactions.
          </p>
        </div>

        <Link
          to="/transactions"
          className="back-button"
        >
          Transactions
        </Link>

      </div>


      {/* File type selection */}

      <div className="import-type-selector">

        <button
          type="button"
          className={
            fileType === "csv"
              ? "import-type-button active"
              : "import-type-button"
          }
          onClick={() => {
            setFileType("csv");
            setFile(null);
            setResult(null);
            setError("");
          }}
        >
          CSV Statement
        </button>

        <button
          type="button"
          className={
            fileType === "pdf"
              ? "import-type-button active"
              : "import-type-button"
          }
          onClick={() => {
            setFileType("pdf");
            setFile(null);
            setResult(null);
            setError("");
          }}
        >
          PDF Statement
        </button>

      </div>


      <section className="import-card">

        <div className="import-icon">
          ↑
        </div>

        <h2>
          Upload {fileType.toUpperCase()} Statement
        </h2>

        <p className="import-description">
          PennyWise will analyze the statement,
          automatically categorize expenses using AI
          and detect duplicate transactions.
        </p>


        <form
          onSubmit={handleUpload}
          className="import-form"
        >

          <div className="file-upload-area">

            <input
              type="file"
              accept={
                fileType === "csv"
                  ? ".csv"
                  : ".pdf"
              }
              onChange={handleFileChange}
              id="statement-file"
            />

            <label htmlFor="statement-file">

              {file
                ? file.name
                : `Choose a ${fileType.toUpperCase()} file`}

            </label>

          </div>


          <button
            type="submit"
            className="import-button"
            disabled={uploading}
          >

            {uploading
              ? "Importing..."
              : "Import Statement"}

          </button>

        </form>


        {error && (
          <div className="import-error">
            {error}
          </div>
        )}


        {result && (
          <div className="import-result">

            <h3>
              Import Completed
            </h3>

            <div className="import-stats">

              <div>
                <strong>
                  {result.imported ?? 0}
                </strong>

                <span>
                  Imported
                </span>
              </div>


              <div>
                <strong>
                  {result.skipped ?? 0}
                </strong>

                <span>
                  Duplicates Skipped
                </span>
              </div>


              <div>
                <strong>
                  {result.errors?.length ?? 0}
                </strong>

                <span>
                  Errors
                </span>
              </div>

            </div>


            {result.transactions_detected !==
              undefined && (

              <p className="transactions-detected">

                Transactions detected:{" "}
                <strong>
                  {result.transactions_detected}
                </strong>

              </p>

            )}


            {result.errors?.length > 0 && (

              <div className="import-error-list">

                {result.errors.map(
                  (item, index) => (

                    <p key={index}>
                      Row {item.row}:{" "}
                      {item.error}
                    </p>

                  )
                )}

              </div>

            )}

          </div>
        )}

      </section>


      <section className="import-info-card">

        <h2>
          Supported Formats
        </h2>

        <p>
          CSV statements should contain:
        </p>

        <div className="csv-columns">

          <span>date</span>
          <span>description</span>
          <span>amount</span>
          <span>type</span>
          <span>merchant</span>
          <span>payment_method</span>

        </div>


        <p>
          PDF statements must currently be
          text-based PDFs. Scanned/image-only
          statements are not supported yet.
        </p>

      </section>

    </div>
  );
}

export default ImportStatement;