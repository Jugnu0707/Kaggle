import axios, { type AxiosError } from "axios";

const configuredApiUrl = import.meta.env.VITE_API_URL?.trim();

export const API_BASE_URL =
  import.meta.env.DEV && !configuredApiUrl ? "" : (configuredApiUrl ?? "http://localhost:8000");

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    Accept: "application/json",
  },
});

let activeRequests = 0;
let setGlobalLoading: ((loading: boolean) => void) | null = null;

export function registerLoadingHandler(handler: (loading: boolean) => void): void {
  setGlobalLoading = handler;
}

function updateLoadingState(): void {
  setGlobalLoading?.(activeRequests > 0);
}

apiClient.interceptors.request.use((config) => {
  activeRequests += 1;
  updateLoadingState();
  return config;
});

apiClient.interceptors.response.use(
  (response) => {
    activeRequests = Math.max(0, activeRequests - 1);
    updateLoadingState();
    return response;
  },
  (error) => {
    activeRequests = Math.max(0, activeRequests - 1);
    updateLoadingState();
    return Promise.reject(error);
  },
);

interface ApiErrorBody {
  message?: string;
  success?: boolean;
}

export function isBackendUnavailableError(error: unknown): boolean {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiErrorBody>;
    if (!axiosError.response) {
      return true;
    }
    return axiosError.response.status >= 500;
  }

  if (error instanceof Error) {
    return /backend unavailable|network error|failed to fetch/i.test(error.message);
  }

  return false;
}

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiErrorBody>;
    if (axiosError.response?.data?.message) {
      return axiosError.response.data.message;
    }
    if (!axiosError.response || axiosError.message === "Network Error") {
      return "Backend unavailable. Please check that the API server is running.";
    }
    if (axiosError.response.status === 404) {
      return "The requested resource was not found.";
    }
    return axiosError.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "An unexpected error occurred.";
}
