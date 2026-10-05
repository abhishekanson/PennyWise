import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api";
function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  useEffect(() => {
  const token = localStorage.getItem("token");

  if (token) {
    navigate("/dashboard", {
      replace: true,
    });
  }
}, [navigate]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await API.post("/auth/login", {
        email: email,
        password: password,
      });

      localStorage.setItem(
        "token",
        response.data.access_token
      );

      navigate("/dashboard");

    } catch (error) {
      setError(
        error.response?.data?.detail ||
        "Login failed"
      );
    }
  };

  return (
    <div className="login-container">

      <div className="login-card">

        <h1>PennyWise</h1>

        <p>AI Personal Finance Advisor</p>

        <form onSubmit={handleLogin}>

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button type="submit">
            Login
          </button>

        </form>

        {error && (
          <p className="error">
            {error}
          </p>
        )}

      </div>

    </div>
  );
}

export default Login;