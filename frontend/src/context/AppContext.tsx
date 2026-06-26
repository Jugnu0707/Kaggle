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
export type ToastVariant = "success" | "error" | "info";

export interface ToastMessage {
  id: string;
  title: string;
  message: string;
  variant: ToastVariant;
}

interface AppContextValue {
  backendStatus: BackendStatus;
  health: HealthData | null;
  refreshBackendStatus: () => Promise<void>;
  isLoading: boolean;
  setLoading: (loading: boolean) => void;
  toasts: ToastMessage[];
  showToast: (toast: Omit<ToastMessage, "id">) => void;
  dismissToast: (id: string) => void;
}

const AppContext = createContext<AppContextValue | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [backendStatus, setBackendStatus] = useState<BackendStatus>("loading");
  const [health, setHealth] = useState<HealthData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

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

  const setLoading = useCallback((loading: boolean) => {
    setIsLoading(loading);
  }, []);

  const dismissToast = useCallback((id: string) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
  }, []);

  const showToast = useCallback((toast: Omit<ToastMessage, "id">) => {
    const id = crypto.randomUUID();
    setToasts((current) => [...current, { ...toast, id }]);
    window.setTimeout(() => {
      dismissToast(id);
    }, 4000);
  }, [dismissToast]);

  useEffect(() => {
    void refreshBackendStatus();
    const interval = window.setInterval(() => {
      void refreshBackendStatus();
    }, 30000);
    return () => window.clearInterval(interval);
  }, [refreshBackendStatus]);

  const value = useMemo(
    () => ({
      backendStatus,
      health,
      refreshBackendStatus,
      isLoading,
      setLoading,
      toasts,
      showToast,
      dismissToast,
    }),
    [
      backendStatus,
      health,
      refreshBackendStatus,
      isLoading,
      setLoading,
      toasts,
      showToast,
      dismissToast,
    ],
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
