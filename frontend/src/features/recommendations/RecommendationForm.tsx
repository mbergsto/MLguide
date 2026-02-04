import { useMemo, useState } from "react";
import type { Option, RecommendationRequest } from "../../api/types";
import { Select } from "../../components/Select";
import { MultiSelect } from "../../components/MultiSelect";
import { TextArea } from "../../components/TextArea";

type Props = {
  meta: {
    phases: Option[];
    clusters: Option[];
    paradigms: Option[];
    tasks: Option[];
    datasetTypes: Option[];
    conditions: Option[];
    performance: Option[];
  };
  onSubmit: (req: RecommendationRequest) => void;
  submitting: boolean;
};

export function RecommendationForm({ meta, onSubmit, submitting }: Props) {
  const [problemText, setProblemText] = useState("");

  const [phaseIri, setPhaseIri] = useState("");
  const [clusterIri, setClusterIri] = useState("");
  const [paradigmIri, setParadigmIri] = useState("");

  const [taskIri, setTaskIri] = useState("");
  const [datasetTypeIri, setDatasetTypeIri] = useState("");

  const [conditions, setConditions] = useState<string[]>([]);
  const [performancePrefs, setPerformancePrefs] = useState<string[]>([]);

  const canSubmit = useMemo(() => {
    return !!phaseIri && !!clusterIri && !!paradigmIri && !submitting;
  }, [phaseIri, clusterIri, paradigmIri, submitting]);

  function submit() {
    if (!canSubmit) return;

    onSubmit({
      problem_text: problemText || null,
      phase_iri: phaseIri,
      cluster_iri: clusterIri,
      paradigm_iri: paradigmIri,
      task_iri: taskIri || null,
      dataset_type_iri: datasetTypeIri || null,
      conditions,
      performance_prefs: performancePrefs,
    });
  }

  return (
    <div style={{ display: "grid", gap: 14 }}>
      <TextArea
        label="Problem description"
        value={problemText}
        onChange={setProblemText}
        placeholder="Describe the production problem briefly (optional for MVP)"
      />

      <div
        style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}
      >
        <Select
          label="Lifecycle phase"
          value={phaseIri}
          options={meta.phases}
          onChange={setPhaseIri}
        />
        <Select
          label="Application cluster"
          value={clusterIri}
          options={meta.clusters}
          onChange={setClusterIri}
        />
        <Select
          label="Learning paradigm"
          value={paradigmIri}
          options={meta.paradigms}
          onChange={setParadigmIri}
        />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <Select
          label="ML task (optional)"
          value={taskIri}
          options={meta.tasks}
          onChange={setTaskIri}
          placeholder="No task filter"
        />
        <Select
          label="Dataset type (optional)"
          value={datasetTypeIri}
          options={meta.datasetTypes}
          onChange={setDatasetTypeIri}
          placeholder="Not used in scoring yet"
        />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <MultiSelect
          label="Conditions"
          values={conditions}
          options={meta.conditions}
          onChange={setConditions}
        />
        <MultiSelect
          label="Performance preferences"
          values={performancePrefs}
          options={meta.performance}
          onChange={setPerformancePrefs}
        />
      </div>

      <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
        <button
          onClick={submit}
          disabled={!canSubmit}
          style={{
            padding: "10px 14px",
            borderRadius: 10,
            border: "1px solid #222",
            background: canSubmit ? "#222" : "#888",
            color: "white",
            cursor: canSubmit ? "pointer" : "not-allowed",
          }}
        >
          {submitting ? "Running..." : "Recommend methods"}
        </button>

        {!phaseIri || !clusterIri || !paradigmIri ? (
          <span style={{ fontSize: 13, color: "#666" }}>
            Select phase, cluster, and paradigm to run recommendations.
          </span>
        ) : null}
      </div>
    </div>
  );
}
