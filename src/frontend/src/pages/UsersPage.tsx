import { useEffect, useState } from "react";
import { api, type User } from "../api/client";
import { useLanguage } from "../i18n/LanguageContext";

function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { t } = useLanguage();

  useEffect(() => {
    api
      .listUsers()
      .then(setUsers)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>{t("users.loading")}</p>;
  if (error)
    return (
      <p style={{ color: "red" }}>
        {t("common.error")}: {error}
      </p>
    );

  return (
    <div>
      <h1>{t("users.title")}</h1>
      <table
        style={{
          width: "100%",
          marginTop: "1rem",
          borderCollapse: "collapse",
        }}
      >
        <thead>
          <tr style={{ borderBottom: "2px solid #e2e8f0", textAlign: "left" }}>
            <th style={{ padding: "0.5rem" }}>{t("users.col.platform")}</th>
            <th style={{ padding: "0.5rem" }}>{t("users.col.platformUserId")}</th>
            <th style={{ padding: "0.5rem" }}>{t("users.col.displayName")}</th>
            <th style={{ padding: "0.5rem" }}>{t("users.col.language")}</th>
            <th style={{ padding: "0.5rem" }}>{t("users.col.created")}</th>
          </tr>
        </thead>
        <tbody>
          {users.map((s) => (
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
          {users.length === 0 && (
            <tr>
              <td colSpan={5} style={{ padding: "1rem", color: "#94a3b8" }}>
                {t("users.empty")}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default UsersPage;
