import { Outlet, Link } from "react-router-dom";
import { useLanguage } from "../i18n/LanguageContext";
import { LANGS, LANG_LABEL, type Lang } from "../i18n/messages";

function Layout() {
  const { lang, setLang, t } = useLanguage();

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
              {t("nav.dashboard")}
            </Link>
          </li>
          <li style={{ marginBottom: "0.75rem" }}>
            <Link to="/users" style={{ color: "#cbd5e1" }}>
              {t("nav.users")}
            </Link>
          </li>
          <li style={{ marginBottom: "0.75rem" }}>
            <Link to="/sessions" style={{ color: "#cbd5e1" }}>
              {t("nav.sessions")}
            </Link>
          </li>
          <li style={{ marginBottom: "0.75rem" }}>
            <Link to="/assessments" style={{ color: "#cbd5e1" }}>
              {t("nav.assessments")}
            </Link>
          </li>
          <li style={{ marginBottom: "0.75rem" }}>
            <Link to="/learner" style={{ color: "#cbd5e1" }}>
              {t("nav.learner")}
            </Link>
          </li>
        </ul>
        <div style={{ marginTop: "2rem" }}>
          <label
            htmlFor="lang-select"
            style={{ display: "block", fontSize: "0.8rem", color: "#94a3b8" }}
          >
            {t("nav.language")}
          </label>
          <select
            id="lang-select"
            value={lang}
            onChange={(e) => setLang(e.target.value as Lang)}
            style={{
              marginTop: "0.25rem",
              width: "100%",
              padding: "0.4rem",
              borderRadius: 4,
              border: "1px solid #475569",
              background: "#0f172a",
              color: "#f1f5f9",
            }}
          >
            {LANGS.map((l) => (
              <option key={l} value={l}>
                {LANG_LABEL[l]}
              </option>
            ))}
          </select>
        </div>
      </nav>
      <main style={{ flex: 1, padding: "2rem" }}>
        <Outlet />
      </main>
    </div>
  );
}

export default Layout;
