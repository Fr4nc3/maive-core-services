import { Outlet, Link } from "react-router-dom";

function Layout() {
  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <nav
        style={{
          width: 220,
          padding: "1.5rem 1rem",
          background: "#1e293b",
          color: "#fff",
        }}
      >
        <h2 style={{ marginBottom: "1.5rem", fontSize: "1.25rem" }}>MAIVE</h2>
        <ul style={{ listStyle: "none" }}>
          <li style={{ marginBottom: "0.75rem" }}>
            <Link to="/" style={{ color: "#cbd5e1" }}>
              Dashboard
            </Link>
          </li>
          <li style={{ marginBottom: "0.75rem" }}>
            <Link to="/students" style={{ color: "#cbd5e1" }}>
              Students
            </Link>
          </li>
          <li style={{ marginBottom: "0.75rem" }}>
            <Link to="/sessions" style={{ color: "#cbd5e1" }}>
              Sessions
            </Link>
          </li>
          <li style={{ marginBottom: "0.75rem" }}>
            <Link to="/assessments" style={{ color: "#cbd5e1" }}>
              Assessments
            </Link>
          </li>
          <li style={{ marginBottom: "0.75rem" }}>
            <Link to="/learner" style={{ color: "#cbd5e1" }}>
              Learner (web)
            </Link>
          </li>
        </ul>
      </nav>
      <main style={{ flex: 1, padding: "2rem" }}>
        <Outlet />
      </main>
    </div>
  );
}

export default Layout;
