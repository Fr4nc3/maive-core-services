import { useState } from "react";
import { api, type Student, type Session, type BotResponse } from "../api/client";

const PLANETS = ["mars", "jupiter", "europa", "moon"];
const SECTIONS = ["intro", "crater_lab", "orbit_observatory", "atmosphere_lab"];

function LearnerPage() {
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

  async function handleStart() {
    setError(null);
    setBusy(true);
    try {
      const s = await api.identifyStudent({
        platform: "web",
        platform_user_id: platformUserId,
        display_name: displayName || platformUserId,
        condition,
      });
      setStudent(s);
      const sess = await api.createSession({ student_id: s.id, condition });
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
        payload: { question },
      });
      const reply = await api.askBot({
        session_id: session.id,
        student_id: student.id,
        planet,
        section,
        question,
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
      <h1>Learner (web reference client)</h1>
      <p style={{ color: "#475569" }}>
        Web-flat fallback for testing the unified bot endpoint. Mirrors the
        contract used by the Unity / Spatial.io / VRChat clients.
      </p>

      {!session ? (
        <section style={card}>
          <h2>1. Identify</h2>
          <label style={lbl}>Platform user id</label>
          <input
            style={inp}
            value={platformUserId}
            onChange={(e) => setPlatformUserId(e.target.value)}
            placeholder="e.g. web_demo_001"
          />
          <label style={lbl}>Display name</label>
          <input
            style={inp}
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder="optional"
          />
          <label style={lbl}>Condition</label>
          <select
            style={inp}
            value={condition}
            onChange={(e) => setCondition(e.target.value as "control" | "treatment")}
          >
            <option value="control">control (static bot)</option>
            <option value="treatment">treatment (AI multi-agent)</option>
          </select>
          <button
            style={btn}
            disabled={!platformUserId || busy}
            onClick={handleStart}
          >
            Start session
          </button>
        </section>
      ) : (
        <section style={card}>
          <h2>2. Ask the bot</h2>
          <p>
            <strong>Student:</strong> {student?.display_name} (
            {student?.platform_user_id}) — <strong>condition:</strong>{" "}
            {session.condition} — <strong>session:</strong>{" "}
            <code>{session.id.slice(0, 8)}…</code>
          </p>
          <label style={lbl}>Planet</label>
          <select style={inp} value={planet} onChange={(e) => setPlanet(e.target.value)}>
            {PLANETS.map((p) => (
              <option key={p}>{p}</option>
            ))}
          </select>
          <label style={lbl}>Section</label>
          <select style={inp} value={section} onChange={(e) => setSection(e.target.value)}>
            {SECTIONS.map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
          <label style={lbl}>Question</label>
          <textarea
            style={{ ...inp, minHeight: 80 }}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Why does Mars have seasons?"
          />
          <button style={btn} disabled={!question || busy} onClick={handleAsk}>
            Ask bot
          </button>

          {botReply && (
            <div style={{ ...card, marginTop: "1rem", background: "#f1f5f9" }}>
              <strong>Source:</strong> {botReply.source}
              <p style={{ marginTop: "0.5rem" }}>{botReply.answer}</p>
            </div>
          )}
        </section>
      )}

      {error && <p style={{ color: "#b91c1c" }}>Error: {error}</p>}
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
