// Static UI strings for the MAIVE web frontend.
// Per DEC-014: default locale is "en"; "es" is a neutral Spanish.
// Authoring discipline: keys are added in EN first, then mirrored in ES by
// Francia (the PhD owner) — never auto-translated.

export type Lang = "en" | "es";

export const LANGS: Lang[] = ["en", "es"];

export const LANG_LABEL: Record<Lang, string> = {
  en: "English",
  es: "Español",
};

type Dict = Record<string, string>;

const en: Dict = {
  // Layout
  "nav.dashboard": "Dashboard",
  "nav.users": "Users",
  "nav.sessions": "Sessions",
  "nav.assessments": "Assessments",
  "nav.learner": "Learner (web)",
  "nav.language": "Language",

  // Users page
  "users.title": "Users",
  "users.col.platform": "Platform",
  "users.col.platformUserId": "Platform User ID",
  "users.col.displayName": "Display Name",
  "users.col.language": "Language",
  "users.col.created": "Created",
  "users.empty": "No users found.",
  "users.loading": "Loading users...",
  "common.error": "Error",

  // Sessions page
  "sessions.title": "Sessions",
  "sessions.placeholder":
    "VR learning sessions will be listed here once connected to the backend.",

  // Learner page
  "learner.title": "Learner (web reference client)",
  "learner.subtitle":
    "Web-flat fallback for testing the unified bot endpoint. Mirrors the contract used by the Unity / Spatial.io / VRChat clients.",
  "learner.identify.title": "1. Identify",
  "learner.identify.platformUserId": "Platform user id",
  "learner.identify.displayName": "Display name",
  "learner.identify.condition": "Condition",
  "learner.identify.language": "Preferred language",
  "learner.identify.start": "Start session",
  "learner.identify.optional": "optional",
  "learner.condition.control": "control (static bot)",
  "learner.condition.treatment": "treatment (AI multi-agent)",
  "learner.ask.title": "2. Ask the bot",
  "learner.ask.planet": "Planet",
  "learner.ask.section": "Section",
  "learner.ask.question": "Question",
  "learner.ask.placeholder": "Why does Mars have seasons?",
  "learner.ask.submit": "Ask bot",
  "learner.ask.source": "Source",
  "learner.ask.languageEcho": "Language",
  "learner.ask.fallback": "(content unavailable in selected language; fallback used)",

  // Stella Astra (mentor character)
  "stella.name": "Stella Astra",
  "stella.state.idle": "ready",
  "stella.state.thinking": "thinking…",
  "stella.state.talking": "speaking",
  "stella.state.celebrating": "celebrating",
  "stella.greeting": "Hi! I'm Stella Astra. Ask me anything about the planet you're exploring.",
  "stella.thinking": "Let me think about that…",
};

const es: Dict = {
  // Layout
  "nav.dashboard": "Panel",
  "nav.users": "Usuarios",
  "nav.sessions": "Sesiones",
  "nav.assessments": "Evaluaciones",
  "nav.learner": "Estudiante (web)",
  "nav.language": "Idioma",

  // Users page
  "users.title": "Usuarios",
  "users.col.platform": "Plataforma",
  "users.col.platformUserId": "ID de usuario en la plataforma",
  "users.col.displayName": "Nombre para mostrar",
  "users.col.language": "Idioma",
  "users.col.created": "Creado",
  "users.empty": "No se encontraron usuarios.",
  "users.loading": "Cargando usuarios...",
  "common.error": "Error",

  // Sessions page
  "sessions.title": "Sesiones",
  "sessions.placeholder":
    "Las sesiones de aprendizaje en RV aparecerán aquí cuando se conecten al backend.",

  // Learner page
  "learner.title": "Estudiante (cliente web de referencia)",
  "learner.subtitle":
    "Cliente web plano para probar el endpoint unificado del bot. Refleja el contrato usado por los clientes Unity / Spatial.io / VRChat.",
  "learner.identify.title": "1. Identificarse",
  "learner.identify.platformUserId": "ID de usuario en la plataforma",
  "learner.identify.displayName": "Nombre para mostrar",
  "learner.identify.condition": "Condición",
  "learner.identify.language": "Idioma preferido",
  "learner.identify.start": "Iniciar sesión",
  "learner.identify.optional": "opcional",
  "learner.condition.control": "control (bot estático)",
  "learner.condition.treatment": "tratamiento (multi-agente IA)",
  "learner.ask.title": "2. Preguntar al bot",
  "learner.ask.planet": "Planeta",
  "learner.ask.section": "Sección",
  "learner.ask.question": "Pregunta",
  "learner.ask.placeholder": "¿Por qué Marte tiene estaciones?",
  "learner.ask.submit": "Preguntar",
  "learner.ask.source": "Fuente",
  "learner.ask.languageEcho": "Idioma",
  "learner.ask.fallback":
    "(contenido no disponible en el idioma seleccionado; se usó alternativa)",

  // Stella Astra (personaje mentor)
  "stella.name": "Stella Astra",
  "stella.state.idle": "lista",
  "stella.state.thinking": "pensando…",
  "stella.state.talking": "hablando",
  "stella.state.celebrating": "celebrando",
  "stella.greeting":
    "¡Hola! Soy Stella Astra. Pregúntame lo que quieras sobre el planeta que estás explorando.",
  "stella.thinking": "Déjame pensarlo…",
};

export const MESSAGES: Record<Lang, Dict> = { en, es };
