export type Option = { iri: string; label: string };

export type RecommendationRequest = {
  problem_text?: string | null;
  phase_iri: string;
  cluster_iri: string;
  paradigm_iri: string;
  task_iri?: string | null;
  conditions: string[];
  performance_prefs: string[];
  // dataset_type_iri is currently not used by backend scoring
  dataset_type_iri?: string | null;
};

export type RecommendationRow = {
  method?: string;
  methodLabel?: string;
  approach?: string;
  approachLabel?: string;
  supportingArticles?: number;
  possibleIfMatches?: number;
  performanceMatches?: number;
  taskMatches?: number;
};
