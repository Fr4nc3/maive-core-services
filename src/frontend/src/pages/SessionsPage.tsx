import { useLanguage } from "../i18n/LanguageContext";

function SessionsPage() {
  const { t } = useLanguage();
  return (
    <div>
      <h1>{t("sessions.title")}</h1>
      <p style={{ marginTop: "1rem", color: "#64748b" }}>
        {t("sessions.placeholder")}
      </p>
    </div>
  );
}

export default SessionsPage;
