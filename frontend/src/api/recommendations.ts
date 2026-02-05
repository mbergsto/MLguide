import { apiPost } from "./http";
import type {
  RecommendationRequest,
  RecommendationRow,
  RecommendationDetailsResponse,
} from "./types";

export const recommendationsApi = {
  recommend: (req: RecommendationRequest) =>
    apiPost<RecommendationRow[]>("/recommendations", req),

  details: (req: RecommendationRequest & { approach_iri: string }) =>
    apiPost<RecommendationDetailsResponse>("/recommendations/details", req),
};
