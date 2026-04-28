import { useEffect, useState } from "react";
import { useLanguage } from "../i18n/LanguageContext";

export type StellaState = "idle" | "thinking" | "talking" | "celebrating";

interface StellaAstraProps {
  /** Current animation state. */
  state?: StellaState;
  /** Optional speech-bubble text (already translated by caller). */
  message?: string;
  /** Pixel size of the avatar (square). Default 96. */
  size?: number;
}

// Asset resolution:
// 1. Try `/stella/<state>.gif` (real animated asset, dropped by designer).
// 2. On error, fall back to `/stella/<state>.svg` (animated placeholder
//    shipped in `public/stella/`).
// See `public/stella/README.md`.
function assetForState(state: StellaState, useFallback: boolean): string {
  const ext = useFallback ? "svg" : "gif";
  return `/stella/${state}.${ext}`;
}

/**
 * Stella Astra — the MAIVE mentor character.
 *
 * Renders a small animated avatar plus an optional speech bubble.
 * Falls back to animated SVG placeholders until real GIFs are authored.
 */
function StellaAstra({ state = "idle", message, size = 96 }: StellaAstraProps) {
  const { t } = useLanguage();
  const [useFallback, setUseFallback] = useState(false);

  // Reset the GIF→SVG fallback when the state changes so each new asset
  // gets its own chance to load.
  useEffect(() => {
    setUseFallback(false);
  }, [state]);

  return (
    <div
      style={{
        display: "flex",
        alignItems: "flex-start",
        gap: "0.75rem",
        marginBottom: "1rem",
      }}
    >
      <img
        src={assetForState(state, useFallback)}
        alt={`${t("stella.name")} — ${t(`stella.state.${state}`)}`}
        title={t("stella.name")}
        width={size}
        height={size}
        onError={() => setUseFallback(true)}
        style={{
          borderRadius: "50%",
          background: "#0f172a",
          border: "2px solid #334155",
          flexShrink: 0,
        }}
      />
      <div>
        <div style={{ fontSize: "0.95rem", fontWeight: 600, color: "#1e293b" }}>
          {t("stella.name")}
          <span
            style={{
              marginLeft: "0.5rem",
              fontSize: "0.75rem",
              fontWeight: 400,
              color: "#64748b",
            }}
          >
            {t(`stella.state.${state}`)}
          </span>
        </div>
        {message && (
          <div
            style={{
              marginTop: "0.4rem",
              padding: "0.5rem 0.75rem",
              background: "#f1f5f9",
              borderRadius: 8,
              fontSize: "0.9rem",
              color: "#0f172a",
              maxWidth: 480,
            }}
          >
            {message}
          </div>
        )}
      </div>
    </div>
  );
}

export default StellaAstra;
