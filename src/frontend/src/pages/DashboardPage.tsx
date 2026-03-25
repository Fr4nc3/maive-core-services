function DashboardPage() {
  return (
    <div>
      <h1>MAIVE Dashboard</h1>
      <p style={{ marginTop: "1rem", color: "#64748b" }}>
        Welcome to the MAIVE Core Services dashboard. Use the sidebar to
        navigate to Students, Sessions, or Assessments.
      </p>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "1rem",
          marginTop: "2rem",
        }}
      >
        <StatCard label="Students" value="—" />
        <StatCard label="Active Sessions" value="—" />
        <StatCard label="Assessments" value="—" />
        <StatCard label="Telemetry Events" value="—" />
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div
      style={{
        padding: "1.5rem",
        background: "#fff",
        borderRadius: 8,
        boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
      }}
    >
      <div style={{ fontSize: "0.875rem", color: "#64748b" }}>{label}</div>
      <div style={{ fontSize: "2rem", fontWeight: 700 }}>{value}</div>
    </div>
  );
}

export default DashboardPage;
