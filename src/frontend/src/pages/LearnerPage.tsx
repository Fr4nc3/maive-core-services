import { useState } from "react";
import { api, type Student, type Session, type BotResponse } from "../api/client";
import { useLanguage } from "../i18n/LanguageContext";
import { LANGS, LANG_LABEL, type Lang } from "../i18n/messages";
import StellaAstra, { type StellaState } from "../components/StellaAstra";

const PLANETS = ["mars", "jupiter", "europa", "moon"];
const SECTIONS = ["intro", "crater_lab", "orbit_observatory", "atmosphere_lab"];

function LearnerPage() {
  const { lang, setLang, t } = useLanguage();

  // Identity
  const [platformUserId, setPlatformUserId] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [condition, setCondition] = useState<"control" | "treatment">("treatment");
  const [student, setStudent] = useState<Student | null>(null);
  const [session, setSession] = useState<Session | null>(null);

  // Bot
  const [planet, setPlanet] = useState(PLANETS[0]);
  const [section, setSection] = useState(SECTIONS[0]);
  const [question, setQuestion] = useState("");
  const [botReply, setBotReply] = useState<BotResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Stella Astra animation state machine.
  // - busy           → thinking
  // - botReply set   → talking (placeholder; designer can swap to celebrating
  //                    when an assessment milestone fires)
  // - otherwise      → idle
  const stellaState: StellaState = busy
    ? "thinking"
    : botReply
    ? "talking"
    : "idle";
  const stellaMessage = busy
    ? t("stella.thinking")
    : botReply?.answer ?? t("stella.greeting");

  async function handleStart() {
    setError(null);
    setBusy(true);
    try {
      // DEC-014: thread the chosen UI language through identify + create-session
      // so the backend stores it on Student and resolves it on Session.
      const s = await api.identifyStudent({
        platform: "web",
        platform_user_id: platformUserId,
        display_name: displayName || platformUserId,
        condition,
        preferred_language: lang,
      });
      setStudent(s);
      const sess = await api.createSession({
        student_id: s.id,
        condition,
        language: lang,
      });
      setSession(sess);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function handleAsk() {
    if (!session || !student) return;
    setError(null);
    setBusy(true);
    try {
      // Log the help-request telemetry first.
      await api.logTelemetry({
        session_id: session.id,
        student_id: student.id,
        event_type: "help_request",
        section,
        content: planet,
        bot_type: condition === "control" ? "static" : "ai",
        payload: { question, language: lang },
      });
      const reply = await api.askBot({
        session_id: session.id,
        student_id: student.id,
        planet,
        section,
        question,
        language: lang,
      });
      setBotReply(reply);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ maxWidth: 720 }}>
      <h1>{t("learner.title")}</h1>
      <p style={{ color: "#475569" }}>{t("learner.subtitle")}</p>

      <StellaAstra state={stellaState} message={stellaMessage} />

      {!session ? (
        <section style={card}>
          <h2>{t("learner.identify.title")}</h2>
          <label style={lbl}>{t("learner.identify.platformUserId")}</label>
          <input
            style={inp}
            value={platformUserId}
            onChange={(e) => setPlatformUserId(e.target.value)}
            placeholder="e.g. web_demo_001"
          />
          <label style={lbl}>{t("learner.identify.displayName")}</label>
          <input
            style={inp}
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder={t("learner.identify.optional")}
          />
          <label style={lbl}>{t("learner.identify.condition")}</label>
          <select
            style={inp}
            value={condition}
            onChange={(e) => setCondition(e.target.value as "control" | "treatment")}
          >
            <option value="control">{t("learner.condition.control")}</option>
            <option value="treatment">{t("learner.condition.treatment")}</option>
          </select>
          <label style={lbl}>{t("learner.identify.language")}</label>
          <select
            style={inp}
            value={lang}
            onChange={(e) => setLang(e.target.value as Lang)}
          >
            {LANGS.map((l) => (
              <option key={l} value={l}>
                {LANG_LABEL[l]}
              </option>
            ))}
          </select>
          <button
            style={btn}
            disabled={!platformUserId || busy}
            onClick={handleStart}
          >
            {t("learner.identify.start")}
          </button>
        </section>
      ) : (
        <section style={card}>
          <h2>{t("learner.ask.title")}</h2>
          <p>
            <strong>{student?.display_name}</strong> ({student?.platform_user_id}) —{" "}
            <strong>{session.condition}</strong> —{" "}
            <code>{session.id.slice(0, 8)}…</code> —{" "}
            <strong>{t("learner.ask.languageEcho")}:</strong> {session.language}
          </p>
          <label style={lbl}>{t("learner.ask.planet")}</label>
          <select style={inp} value={planet} onChange={(e) => setPlanet(e.target.value)}>
            {PLANETS.map((p) => (
              <option key={p}>{p}</option>
            ))}
          </select>
          <label style={lbl}>{t("learner.ask.section")}</label>
          <select style={inp} value={section} onChange={(e) => setSection(e.target.value)}>
            {SECTIONS.map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
          <label style={lbl}>{t("learner.ask.question")}</label>
          <textarea
            style={{ ...inp, minHeight: 80 }}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder={t("learner.ask.placeholder")}
          />
          <button style={btn} disabled={!question || busy} onClick={handleAsk}>
            {t("learner.ask.submit")}
          </button>

          {botReply && (
            <div style={{ ...card, marginTop: "1rem", background: "#f1f5f9" }}>
              <strong>{t("learner.ask.source")}:</strong> {botReply.source}
              {botReply.language && (
                <>
                  {" — "}
                  <strong>{t("learner.ask.languageEcho")}:</strong>{" "}
                  {botReply.language}
                  {botReply.language_fallback && (
                    <em style={{ marginLeft: "0.5rem", color: "#b45309" }}>
                      {t("learner.ask.fallback")}
                    </em>
                  )}
                </>
              )}
              <p style={{ marginTop: "0.5rem" }}>{botReply.answer}</p>
            </div>
          )}
        </section>
      )}

      {error && (
        <p style={{ color: "#b91c1c" }}>
          {t("common.error")}: {error}
        </p>
      )}
    </div>
  );
}

const card: React.CSSProperties = {
  border: "1px solid #cbd5e1",
  borderRadius: 8,
  padding: "1.25rem",
  marginBottom: "1rem",
  background: "#fff",
};
const lbl: React.CSSProperties = {
  display: "block",
  fontSize: "0.85rem",
  marginTop: "0.75rem",
  color: "#334155",
};
const inp: React.CSSProperties = {
  width: "100%",
  padding: "0.5rem",
  border: "1px solid #cbd5e1",
  borderRadius: 4,
  marginTop: "0.25rem",
  fontSize: "1rem",
};
const btn: React.CSSProperties = {
  marginTop: "1rem",
  padding: "0.5rem 1rem",
  background: "#1e293b",
  color: "#fff",
  border: "none",
  borderRadius: 4,
  cursor: "pointer",
};

export default LearnerPage;
