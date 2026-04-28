import { useEffect, useState } from "react";
import { api, type Student } from "../api/client";

function StudentsPage() {
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listStudents()
      .then(setStudents)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading students...</p>;
  if (error) return <p style={{ color: "red" }}>Error: {error}</p>;

  return (
    <div>
      <h1>Students</h1>
      <table
        style={{
          width: "100%",
          marginTop: "1rem",
          borderCollapse: "collapse",
        }}
      >
        <thead>
          <tr style={{ borderBottom: "2px solid #e2e8f0", textAlign: "left" }}>
            <th style={{ padding: "0.5rem" }}>Platform</th>
            <th style={{ padding: "0.5rem" }}>Platform User ID</th>
            <th style={{ padding: "0.5rem" }}>Display Name</th>
            <th style={{ padding: "0.5rem" }}>Created</th>
          </tr>
        </thead>
        <tbody>
          {students.map((s) => (
            <tr key={s.id} style={{ borderBottom: "1px solid #e2e8f0" }}>
              <td style={{ padding: "0.5rem" }}>{s.platform}</td>
              <td style={{ padding: "0.5rem" }}>{s.platform_user_id}</td>
              <td style={{ padding: "0.5rem" }}>{s.display_name || "—"}</td>
              <td style={{ padding: "0.5rem" }}>
                {new Date(s.created_at).toLocaleDateString()}
              </td>
            </tr>
          ))}
          {students.length === 0 && (
            <tr>
              <td colSpan={4} style={{ padding: "1rem", color: "#94a3b8" }}>
                No students found.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default StudentsPage;
