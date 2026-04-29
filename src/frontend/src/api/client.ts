const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  // Users
  listUsers: () => request<User[]>("/api/users"),
  getUser: (id: string) => request<User>(`/api/users/${id}`),
  createUser: (data: CreateUserPayload) =>
    request<User>("/api/users", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  identifyUser: (data: IdentifyUserPayload) =>
    request<User>("/api/users/identify", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Sessions
  listSessions: () => request<Session[]>("/api/sessions"),
  getSession: (id: string) => request<Session>(`/api/sessions/${id}`),
  createSession: (data: CreateSessionPayload) =>
    request<Session>("/api/sessions", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Assessments
  getAssessment: (id: string) =>
    request<Assessment>(`/api/assessments/${id}`),
  createAssessment: (data: CreateAssessmentPayload) =>
    request<Assessment>("/api/assessments", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Telemetry
  getSessionTelemetry: (sessionId: string) =>
    request<TelemetryEvent[]>(`/api/telemetry/${sessionId}`),
  logTelemetry: (data: LogTelemetryPayload) =>
    request<TelemetryEvent>("/api/telemetry", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Bot (unified — routes by session.condition)
  askBot: (data: AskBotPayload) =>
    request<BotResponse>("/api/bot/ask", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Health
  health: () => request<{ status: string }>("/health"),
  healthDetailed: () =>
    request<{ status: string; cosmos: { ok: boolean }; llm: { ok: boolean; provider: string; model: string } }>(
      "/api/health"
    ),
};

// ---- Types ----
export interface User {
  id: string;
  platform: string;
  platform_user_id: string;
  display_name: string;
  // DEC-014: stable per-user language preference ("en" | "es").
  preferred_language: string;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface CreateUserPayload {
  platform: string;
  platform_user_id: string;
  display_name?: string;
  preferred_language?: string;
}

export interface Session {
  id: string;
  user_id: string;
  condition: string;
  // DEC-014: per-session effective language ("en" | "es").
  language: string;
  started_at: string;
  ended_at: string | null;
  status: string;
  metadata: Record<string, unknown>;
}

export interface CreateSessionPayload {
  user_id: string;
  condition?: string;
  // DEC-014: optional per-session override; if omitted backend falls back to
  // user.preferred_language, then "en".
  language?: string;
}

export interface Assessment {
  id: string;
  user_id: string;
  session_id: string | null;
  assessment_type: string;
  score: number;
  max_score: number;
  normalized_gain: number | null;
  submitted_at: string;
  metadata: Record<string, unknown>;
}

export interface CreateAssessmentPayload {
  user_id: string;
  session_id?: string;
  assessment_type?: string;
  score?: number;
  max_score?: number;
}

export interface TelemetryEvent {
  id: string;
  session_id: string;
  user_id: string;
  event_type: string;
  timestamp: string;
  duration_ms: number | null;
  section: string;
  content: string;
  help_text: string;
  bot_type: string;
  payload: Record<string, unknown>;
}

export interface IdentifyUserPayload {
  platform: string;
  platform_user_id: string;
  display_name?: string;
  condition?: string;
  // DEC-014: passed on first contact so the user row stores the chosen UI language.
  preferred_language?: string;
}

export interface LogTelemetryPayload {
  session_id: string;
  user_id: string;
  event_type: string;
  section?: string;
  content?: string;
  help_text?: string;
  bot_type?: string;
  duration_ms?: number;
  payload?: Record<string, unknown>;
}

export interface AskBotPayload {
  session_id: string;
  user_id: string;
  planet: string;
  section?: string;
  question: string;
  // DEC-014: optional per-call override; backend resolves
  // body.language → session.language → user.preferred_language → "en".
  language?: string;
}

export interface BotResponse {
  source: "static" | "ai";
  answer: string;
  // DEC-014: language actually used by the backend for this response.
  language?: string;
  language_fallback?: boolean;
  metadata?: Record<string, unknown>;
}
