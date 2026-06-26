import type { APIResponse, DashboardStats } from "../types/api";
import { apiClient } from "./apiClient";

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const response = await apiClient.get<APIResponse<DashboardStats>>("/api/v1/dashboard/stats");
  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.message || "Failed to load dashboard statistics");
  }
  return response.data.data;
}
