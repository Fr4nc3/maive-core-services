import { useEffect, useState } from "react";
import { api, type Student } from "../api/client";
import { useLanguage } from "../i18n/LanguageContext";

function StudentsPage() {
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { t } = useLanguage();

  useEffect(() => {
    api
      .listStudents()
      .then(setStudents)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>{t("students.loading")}</p>;
  if (error)
    return (
      <p style={{ color: "red" }}>
        {t("common.error")}: {error}
      </p>
    );

  return (
    <div>
      <h1>{t("students.title")}</h1>
      <table
        style={{
          width: "100%",
          marginTop: "1rem",
          borderCollapse: "collapse",
        }}
      >
        <thead>
          <tr style={{ borderBottom: "2px solid #e2e8f0", textAlign: "left" }}>
            <th style={{ padding: "0.5rem" }}>{t("students.col.platform")}</th>
            <th style={{ padding: "0.5rem" }}>{t("students.col.platformUserId")}</th>
            <th style={{ padding: "0.5rem" }}>{t("students.col.displayName")}</th>
            <th style={{ padding: "0.5rem" }}>{t("students.col.language")}</th>
            <th style={{ padding: "0.5rem" }}>{t("students.col.created")}</th>
          </tr>
        </thead>
        <tbody>
          {students.map((s) => (
            <tr key={s.id} style={{ borderBottom: "1px solid #e2e8f0" }}>
              <td style={{ padding: "0.5rem" }}>{s.platform}</td>
              <td style={{ padding: "0.5rem" }}>{s.platform_user_id}</td>
              <td style={{ padding: "0.5rem" }}>{s.display_name || "—"}</td>
              <td style={{ padding: "0.5rem" }}>{s.preferred_language || "en"}</td>
              <td style={{ padding: "0.5rem" }}>
                {new Date(s.created_at).toLocaleDateString()}
              </td>
            </tr>
          ))}
          {students.length === 0 && (
            <tr>
              <td colSpan={5} style={{ padding: "1rem", color: "#94a3b8" }}>
                {t("students.empty")}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default StudentsPage;
