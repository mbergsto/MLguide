import { useNavigate } from "react-router-dom";
import type { RecommendationRow, RecommendationRequest } from "../../api/types";

type Props = {
  rows: RecommendationRow[];
  lastRequest: RecommendationRequest | null;
};

function n(v: unknown): number {
  return typeof v === "number" && Number.isFinite(v) ? v : 0;
}

export function RecommendationResults({ rows, lastRequest }: Props) {
  const navigate = useNavigate();

  if (!rows.length)
    return <div style={{ color: "#666", fontSize: 14 }}>No results yet.</div>;

  return (
    <div style={{ width: "100%", display: "grid", gap: 10 }}>
      {rows.map((r, idx) => {
        const title =
          r.methodLabel ||
          r.approachLabel ||
          r.approach ||
          r.method ||
          `Result ${idx + 1}`;

        const approach = r.approach;
        const canOpen =
          typeof approach === "string" &&
          approach.length > 0 &&
          !!lastRequest;

        return (
          <div
            key={`${r.method ?? ""}-${r.approach ?? ""}-${idx}`}
            role={canOpen ? "button" : undefined}
            tabIndex={canOpen ? 0 : undefined}
            onClick={() => {
              if (!canOpen) return;
              navigate(`/recommendations/${encodeURIComponent(approach!)}`, {
                state: { req: lastRequest },
              });
            }}
            onKeyDown={(e) => {
              if (!canOpen) return;
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                navigate(
                  `/recommendations/${encodeURIComponent(approach!)}`,
                  {
                    state: { req: lastRequest },
                  },
                );
              }
            }}
            style={{
              border: "1px solid #ddd",
              borderRadius: 12,
              padding: 12,
              cursor: canOpen ? "pointer" : "default",
            }}
          >
            <div style={{ fontWeight: 700 }}>{title}</div>
            <div
              style={{
                fontSize: 13,
                color: "#555",
                marginTop: 6,
                display: "grid",
                gap: 4,
              }}
            >
              <div>Supporting articles: {n(r.supportingArticles)}</div>
              <div>Task matches: {n(r.taskMatch)}</div>
              <div>Condition matches: {n(r.possibleIfMatches)}</div>
              <div>Performance matches: {n(r.performanceMatches)}</div>
              {!canOpen ? (
                <div style={{ color: "#888", marginTop: 4 }}>
                  Run recommendations to open details.
                </div>
              ) : null}
            </div>
          </div>
        );
      })}
    </div>
  );
}
