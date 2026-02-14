import { useEffect, useState } from "react";
import type { Option } from "../../api/types";
import { metaApi } from "../../api/meta";

type MetaState = {
  phases: Option[];
  clusters: Option[];
  paradigms: Option[];
  tasks: Option[];
  datasetTypes: Option[];
  conditions: Option[];
  performance: Option[];
};

const empty: MetaState = {
  phases: [],
  clusters: [],
  paradigms: [],
  tasks: [],
  datasetTypes: [],
  conditions: [],
  performance: [],
};

export function useMeta() {
  const [data, setData] = useState<MetaState>(empty);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const [
          phases,
          clusters,
          paradigms,
          tasks,
          datasetTypes,
          conditions,
          performance,
        ] = await Promise.all([
          metaApi.phases(),
          metaApi.clusters(),
          metaApi.paradigms(),
          metaApi.tasks(),
          metaApi.datasetTypes(),
          metaApi.conditions(),
          metaApi.performance(),
        ]);

        if (!cancelled) {
          setData({
            phases,
            clusters,
            paradigms,
            tasks,
            datasetTypes,
            conditions,
            performance,
          });
        }
      } catch (e: unknown) {
        if (cancelled) return;

        if (e instanceof Error) {
          setError(e.message);
        } else {
          setError("Failed to load meta data");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return { data, loading, error };
}
