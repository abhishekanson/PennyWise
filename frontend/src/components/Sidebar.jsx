import { NavLink, useNavigate } from "react-router-dom";

function Sidebar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login", {
      replace: true,
    });
  };

  const navClass = ({ isActive }) =>
    `sidebar-link ${isActive ? "active" : ""}`;

  return (
    <aside className="sidebar">

      <div className="sidebar-logo">
        <div className="logo-mark">P</div>

        <div>
          <h2>PennyWise</h2>
          <p>AI Personal Finance Advisor</p>
        </div>
      </div>

      <nav className="sidebar-nav">

        <div className="sidebar-section-title">
          MAIN
        </div>

        <NavLink
          to="/dashboard"
          className={navClass}
        >
          <span className="sidebar-icon">⌂</span>
          <span>Dashboard</span>
        </NavLink>

        <NavLink
          to="/transactions"
          className={navClass}
        >
          <span className="sidebar-icon">₹</span>
          <span>Transactions</span>
        </NavLink>

        <NavLink
          to="/import-statement"
          className={navClass}
        >
          <span className="sidebar-icon">↑</span>
          <span>Import Statement</span>
        </NavLink>

        <NavLink
          to="/budgets"
          className={navClass}
        >
          <span className="sidebar-icon">▣</span>
          <span>Budgets</span>
        </NavLink>

        <NavLink
          to="/savings-goals"
          className={navClass}
        >
          <span className="sidebar-icon">★</span>
          <span>Savings Goals</span>
        </NavLink>

      </nav>

      <div className="sidebar-bottom">

        <div className="sidebar-user">
          <div className="user-avatar">
            U
          </div>

          <div className="user-info">
            <strong>User</strong>
            <span>Personal Account</span>
          </div>
        </div>

        <button
          className="sidebar-logout"
          onClick={handleLogout}
        >
          <span className="sidebar-icon">↪</span>
          <span>Logout</span>
        </button>

      </div>

    </aside>
  );
}

export default Sidebar;