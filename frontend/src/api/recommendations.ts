import { apiPost } from "./http";
import type { RecommendationRequest, RecommendationRow } from "./types";

export const recommendationsApi = {
  recommend: (req: RecommendationRequest) =>
    apiPost<RecommendationRow[]>("/recommendations", req),
};
