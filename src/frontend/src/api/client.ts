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
  // Students
  listStudents: () => request<Student[]>("/api/students"),
  getStudent: (id: string) => request<Student>(`/api/students/${id}`),
  createStudent: (data: CreateStudentPayload) =>
    request<Student>("/api/students", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  identifyStudent: (data: IdentifyStudentPayload) =>
    request<Student>("/api/students/identify", {
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
export interface Student {
  id: string;
  platform: string;
  platform_user_id: string;
  display_name: string;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface CreateStudentPayload {
  platform: string;
  platform_user_id: string;
  display_name?: string;
}

export interface Session {
  id: string;
  student_id: string;
  condition: string;
  started_at: string;
  ended_at: string | null;
  status: string;
  metadata: Record<string, unknown>;
}

export interface CreateSessionPayload {
  student_id: string;
  condition?: string;
}

export interface Assessment {
  id: string;
  student_id: string;
  session_id: string | null;
  assessment_type: string;
  score: number;
  max_score: number;
  normalized_gain: number | null;
  submitted_at: string;
  metadata: Record<string, unknown>;
}

export interface CreateAssessmentPayload {
  student_id: string;
  session_id?: string;
  assessment_type?: string;
  score?: number;
  max_score?: number;
}

export interface TelemetryEvent {
  id: string;
  session_id: string;
  student_id: string;
  event_type: string;
  timestamp: string;
  duration_ms: number | null;
  section: string;
  content: string;
  help_text: string;
  bot_type: string;
  payload: Record<string, unknown>;
}

export interface IdentifyStudentPayload {
  platform: string;
  platform_user_id: string;
  display_name?: string;
  condition?: string;
}

export interface LogTelemetryPayload {
  session_id: string;
  student_id: string;
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
  student_id: string;
  planet: string;
  section?: string;
  question: string;
}

export interface BotResponse {
  source: "static" | "ai";
  answer: string;
  metadata?: Record<string, unknown>;
}
