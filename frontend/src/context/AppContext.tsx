import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { HealthData } from "../types/api";
import { fetchHealth } from "../services/incidentService";

export type BackendStatus = "loading" | "healthy" | "unavailable";

interface AppContextValue {
  backendStatus: BackendStatus;
  health: HealthData | null;
  refreshBackendStatus: () => Promise<void>;
}

const AppContext = createContext<AppContextValue | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [backendStatus, setBackendStatus] = useState<BackendStatus>("loading");
  const [health, setHealth] = useState<HealthData | null>(null);

  const refreshBackendStatus = useCallback(async () => {
    setBackendStatus("loading");
    try {
      const data = await fetchHealth();
      setHealth(data);
      setBackendStatus("healthy");
    } catch {
      setHealth(null);
      setBackendStatus("unavailable");
    }
  }, []);

  useEffect(() => {
    void refreshBackendStatus();
    const interval = window.setInterval(() => {
      void refreshBackendStatus();
    }, 30000);
    return () => window.clearInterval(interval);
  }, [refreshBackendStatus]);

  const value = useMemo(
    () => ({ backendStatus, health, refreshBackendStatus }),
    [backendStatus, health, refreshBackendStatus],
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppContext(): AppContextValue {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useAppContext must be used within AppProvider");
  }
  return context;
}
