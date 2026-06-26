import type { APIResponse, LogFileList, LogUploadResult } from "../types/api";
import { apiClient } from "./apiClient";

const MAX_UPLOAD_SIZE_BYTES = 52_428_800;
const ALLOWED_EXTENSIONS = [".log", ".txt", ".csv", ".json", ".evtx"];

export function validateLogFile(file: File): string | null {
  const extension = file.name.includes(".")
    ? file.name.slice(file.name.lastIndexOf(".")).toLowerCase()
    : "";

  if (!ALLOWED_EXTENSIONS.includes(extension)) {
    return "Unsupported file type. Allowed: .log, .txt, .csv, .json, .evtx";
  }

  if (file.size > MAX_UPLOAD_SIZE_BYTES) {
    return "File exceeds the maximum allowed size of 50 MB";
  }

  if (file.size === 0) {
    return "File is empty";
  }

  return null;
}

export async function uploadLogFile(
  file: File,
  onProgress?: (progress: number) => void,
  incidentId?: string,
): Promise<LogUploadResult> {
  const validationError = validateLogFile(file);
  if (validationError) {
    throw new Error(validationError);
  }

  const formData = new FormData();
  formData.append("file", file);
  if (incidentId) {
    formData.append("incident_id", incidentId);
  }

  const response = await apiClient.post<APIResponse<LogUploadResult>>(
    "/api/v1/logs/upload",
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (event) => {
        if (!event.total) {
          return;
        }
        onProgress?.(Math.round((event.loaded / event.total) * 100));
      },
    },
  );

  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.message || "Upload failed");
  }

  return response.data.data;
}

export async function listLogFiles(page = 1, pageSize = 10): Promise<LogFileList> {
  const response = await apiClient.get<APIResponse<LogFileList>>("/api/v1/logs", {
    params: { page, page_size: pageSize },
  });
  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.message || "Failed to load log files");
  }
  return response.data.data;
}
