import { apiGet } from "./http";
import type { Option } from "./types";

export const metaApi = {
  phases: () => apiGet<Option[]>("/meta/phases"),
  clusters: () => apiGet<Option[]>("/meta/clusters"),
  paradigms: () => apiGet<Option[]>("/meta/paradigms"),
  tasks: () => apiGet<Option[]>("/meta/tasks"),
  datasetTypes: () => apiGet<Option[]>("/meta/enums/dataset-types"),
  conditions: () => apiGet<Option[]>("/meta/enums/conditions"),
  performance: () => apiGet<Option[]>("/meta/enums/performance"),
};
