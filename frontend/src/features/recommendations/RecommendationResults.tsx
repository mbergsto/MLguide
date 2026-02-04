import type { RecommendationRow } from "../../api/types";

type Props = {
  rows: RecommendationRow[];
};

function n(v: unknown): number {
  return typeof v === "number" && Number.isFinite(v) ? v : 0;
}

export function RecommendationResults({ rows }: Props) {
  if (!rows.length) {
    return <div style={{ color: "#666", fontSize: 14 }}>No results yet.</div>;
  }

  return (
    <div style={{ display: "grid", gap: 10 }}>
      {rows.map((r, idx) => {
        const title =
          r.methodLabel ||
          r.approachLabel ||
          r.approach ||
          r.method ||
          `Result ${idx + 1}`;
        return (
          <div
            key={`${r.method ?? ""}-${r.approach ?? ""}-${idx}`}
            style={{ border: "1px solid #ddd", borderRadius: 12, padding: 12 }}
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
              <div>Task matches: {n(r.taskMatches)}</div>
              <div>Condition matches: {n(r.possibleIfMatches)}</div>
              <div>Performance matches: {n(r.performanceMatches)}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
