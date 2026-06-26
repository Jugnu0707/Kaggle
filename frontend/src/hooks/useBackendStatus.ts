import { useEffect, useState } from "react";
import { fetchHealth, type HealthResponse } from "../services/api";

type BackendStatus = "loading" | "healthy" | "unavailable";

export function useBackendStatus(): {
  status: BackendStatus;
  health: HealthResponse | null;
} {
  const [status, setStatus] = useState<BackendStatus>("loading");
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    let active = true;

    fetchHealth()
      .then((data) => {
        if (active) {
          setHealth(data);
          setStatus("healthy");
        }
      })
      .catch(() => {
        if (active) {
          setHealth(null);
          setStatus("unavailable");
        }
      });

    return () => {
      active = false;
    };
  }, []);

  return { status, health };
}
