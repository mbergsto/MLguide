import { useEffect, useMemo, useState } from "react";
import { useLocation, useParams, Link } from "react-router-dom";
import { recommendationsApi } from "../api/recommendations";
import type { RecommendationRequest } from "../api/types";

type MatchItem = { iri: string; label: string };
type ArticleItem = { article?: string; doi: string; label?: string };

type DetailsResponse = {
  approachIri: string;
  articles: ArticleItem[];
  matches: {
    conditions: MatchItem[];
    performance: MatchItem[];
    tasks: MatchItem[];
  };
};

function doiUrl(doi: string) {
  return `https://doi.org/${doi}`;
}

export function RecommendationDetailsPage() {
  const { approachIri: approachIriParam } = useParams();
  const location = useLocation();

  type DetailsLocationState = {
    req?: RecommendationRequest;
  };

  const state = location.state as DetailsLocationState | null;
  const req = state?.req;

  const approachIri = useMemo(() => {
    if (!approachIriParam) return null;
    try {
      return decodeURIComponent(approachIriParam);
    } catch {
      return approachIriParam;
    }
  }, [approachIriParam]);

  const [data, setData] = useState<DetailsResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (!approachIri || !req) return;

    let cancelled = false;

    (async () => {
      try {
        setErr(null);
        setData(null);
        const res = await recommendationsApi.details({
          ...req,
          approach_iri: approachIri,
        });
        if (!cancelled) setData(res);
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : "Failed to load details";
        if (!cancelled) setErr(msg);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [approachIri, req]);

  if (!approachIri)
    return <div style={{ color: "crimson" }}>Missing approach IRI.</div>;

  if (!req) {
    return (
      <div style={{ display: "grid", gap: 10 }}>
        <div style={{ color: "crimson" }}>
          Missing context. Open details by clicking a result after running
          recommendations.
        </div>
        <Link to="/">Back</Link>
      </div>
    );
  }

  if (err) return <div style={{ color: "crimson" }}>{err}</div>;
  if (!data) return <div>Loading...</div>;

  return (
    <div
      style={{
        maxWidth: 1200,
        width: "100%",
        margin: "0 auto",
        padding: 18,
        display: "grid",
        gap: 14,
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: 12,
          alignItems: "center",
        }}
      >
        <h2 style={{ margin: 0 }}>Recommendation details</h2>
        <Link to="/">Back</Link>
      </div>

      <div style={{ border: "1px solid #eee", borderRadius: 14, padding: 14 }}>
        <div style={{ fontWeight: 700, marginBottom: 8 }}>
          Supporting articles
        </div>
        <div style={{ display: "grid", gap: 6 }}>
          {data.articles.map((a, i) => (
            <div key={`${a.doi}-${i}`}>
              <a href={doiUrl(a.doi)} target="_blank" rel="noreferrer">
                {a.doi}
              </a>
              {a.label ? (
                <span style={{ color: "#666" }}> — {a.label}</span>
              ) : null}
            </div>
          ))}
        </div>
      </div>

      <div style={{ border: "1px solid #eee", borderRadius: 14, padding: 14 }}>
        <div style={{ fontWeight: 700, marginBottom: 10 }}>Matches</div>

        <div style={{ display: "grid", gap: 12 }}>
          <div>
            <div style={{ fontWeight: 600 }}>Tasks</div>
            <ul style={{ margin: "6px 0 0 18px" }}>
              {data.matches.tasks.map((m) => (
                <li key={m.iri}>{m.label}</li>
              ))}
            </ul>
          </div>

          <div>
            <div style={{ fontWeight: 600 }}>Conditions</div>
            <ul style={{ margin: "6px 0 0 18px" }}>
              {data.matches.conditions.map((m) => (
                <li key={m.iri}>{m.label}</li>
              ))}
            </ul>
          </div>

          <div>
            <div style={{ fontWeight: 600 }}>Performance</div>
            <ul style={{ margin: "6px 0 0 18px" }}>
              {data.matches.performance.map((m) => (
                <li key={m.iri}>{m.label}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
