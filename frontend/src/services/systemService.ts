import type { APIResponse, MCPStatusData } from "../types/api";
import { apiClient } from "./apiClient";

export async function fetchMcpStatus(): Promise<MCPStatusData> {
  const response = await apiClient.get<APIResponse<MCPStatusData>>("/api/v1/system/mcp");
  const body = response.data;

  if (body?.success && body.data) {
    return body.data;
  }

  throw new Error("Failed to load MCP status");
}
