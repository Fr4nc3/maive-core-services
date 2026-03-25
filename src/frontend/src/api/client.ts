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
  listStudents: () => request<Student[]>("/api/v1/students"),
  getStudent: (id: string) => request<Student>(`/api/v1/students/${id}`),
  createStudent: (data: CreateStudentPayload) =>
    request<Student>("/api/v1/students", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Sessions
  listSessions: () => request<Session[]>("/api/v1/sessions"),
  getSession: (id: string) => request<Session>(`/api/v1/sessions/${id}`),
  createSession: (data: CreateSessionPayload) =>
    request<Session>("/api/v1/sessions", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Assessments
  getAssessment: (id: string) =>
    request<Assessment>(`/api/v1/assessments/${id}`),
  createAssessment: (data: CreateAssessmentPayload) =>
    request<Assessment>("/api/v1/assessments", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Telemetry
  getSessionTelemetry: (sessionId: string) =>
    request<TelemetryEvent[]>(`/api/v1/telemetry/${sessionId}`),

  // Health
  health: () => request<{ status: string }>("/health"),
};

// ---- Types ----
export interface Student {
  id: string;
  email: string;
  display_name: string;
  group: string;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface CreateStudentPayload {
  email: string;
  display_name: string;
  group?: string;
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
  position: Record<string, unknown>;
  payload: Record<string, unknown>;
}
