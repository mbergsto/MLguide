import { useState } from "react";
import { useMeta } from "../features/meta/useMeta";
import { recommendationsApi } from "../api/recommendations";
import type { RecommendationRequest, RecommendationRow } from "../api/types";
import { RecommendationForm } from "../features/recommendations/RecommendationForm";
import { RecommendationResults } from "../features/recommendations/RecommendationResults";

export function MainPage() {
  const { data: meta, loading, error } = useMeta();
  const [submitting, setSubmitting] = useState(false);
  const [rows, setRows] = useState<RecommendationRow[]>([]);
  const [runError, setRunError] = useState<string | null>(null);

  async function onSubmit(req: RecommendationRequest) {
    setSubmitting(true);
    setRunError(null);

    try {
      const res = await recommendationsApi.recommend({
        problem_text: req.problem_text ?? null,
        phase_iri: req.phase_iri,
        cluster_iri: req.cluster_iri,
        paradigm_iri: req.paradigm_iri,
        task_iri: req.task_iri ?? null,
        conditions: req.conditions,
        performance_prefs: req.performance_prefs,
      });
      setRows(res);
    } catch (e: unknown) {
      const errorMessage =
        e instanceof Error ? e.message : "Failed to run recommendations";
      setRunError(errorMessage);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div
      style={{
        maxWidth: 1100,
        margin: "0 auto",
        padding: 18,
        display: "grid",
        gap: 16,
      }}
    >
      <header style={{ display: "grid", gap: 4 }}>
        <h1 style={{ margin: 0 }}>ML Method Recommender (MVP)</h1>
        <div style={{ color: "#666", fontSize: 14 }}>
          Uses phase/cluster/paradigm + ontology constraints to rank methods
          from articles.
        </div>
      </header>

      {loading ? <div>Loading metadata...</div> : null}
      {error ? (
        <div style={{ color: "crimson" }}>Meta load error: {error}</div>
      ) : null}

      {!loading && !error ? (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1.2fr 0.8fr",
            gap: 18,
          }}
        >
          <div
            style={{ border: "1px solid #eee", borderRadius: 14, padding: 14 }}
          >
            <RecommendationForm
              meta={meta}
              onSubmit={onSubmit}
              submitting={submitting}
            />
          </div>

          <div
            style={{ border: "1px solid #eee", borderRadius: 14, padding: 14 }}
          >
            <div style={{ fontWeight: 700, marginBottom: 10 }}>Results</div>
            {runError ? (
              <div style={{ color: "crimson", marginBottom: 10 }}>
                {runError}
              </div>
            ) : null}
            <RecommendationResults rows={rows} />
          </div>
        </div>
      ) : null}
    </div>
  );
}
