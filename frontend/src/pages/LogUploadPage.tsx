import { useCallback, useEffect, useState } from "react";
import { DataTable } from "../components/DataTable";
import { FileUpload } from "../components/FileUpload";
import { Badge, LoadingSpinner } from "../components/ui";
import { useAppContext } from "../context/AppContext";
import { listLogFiles, uploadLogFile } from "../services/logService";
import type { LogFileMetadata } from "../types/api";
import { formatDate, formatFileSize } from "../utils/format";

const EMPTY_LOGS_MESSAGE = "No log files uploaded yet. Upload a log file to get started.";

export function LogUploadPage() {
  const { backendStatus } = useAppContext();
  const [logs, setLogs] = useState<LogFileMetadata[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const loadLogs = useCallback(async () => {
    if (backendStatus !== "healthy") {
      setLogs([]);
      setTotalPages(1);
      setLoading(false);
      return;
    }

    setLoading(true);
    try {
      const data = await listLogFiles(page, 10);
      setLogs(data.items);
      setTotalPages(data.total_pages || 1);
    } catch {
      setLogs([]);
      setTotalPages(1);
    } finally {
      setLoading(false);
    }
  }, [backendStatus, page]);

  useEffect(() => {
    void loadLogs();
  }, [loadLogs]);

  const handleUpload = async (file: File, onProgress: (progress: number) => void) => {
    await uploadLogFile(file, onProgress);
    await loadLogs();
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">Log Uploads</h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Securely upload and manage investigation log files
        </p>
      </div>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
        <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">Upload Log File</h3>
        <div className="mt-4">
          <FileUpload
            onUpload={handleUpload}
            disabled={backendStatus !== "healthy"}
          />
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-950">
        <div className="border-b border-slate-200 px-4 py-4 dark:border-slate-800">
          <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">Uploaded Logs</h3>
        </div>

        {loading && backendStatus === "healthy" ? (
          <LoadingSpinner label="Loading uploaded logs..." />
        ) : (
          <>
            <DataTable
              data={logs}
              emptyMessage={EMPTY_LOGS_MESSAGE}
              columns={[
                {
                  key: "filename",
                  header: "Filename",
                  render: (row) => row.original_filename,
                },
                {
                  key: "size",
                  header: "Size",
                  render: (row) => formatFileSize(row.file_size_bytes),
                },
                {
                  key: "uploaded_at",
                  header: "Upload Date",
                  render: (row) => formatDate(row.uploaded_at),
                },
                {
                  key: "status",
                  header: "Status",
                  render: (row) => <Badge label={row.upload_status} />,
                },
              ]}
            />
            <div className="flex items-center justify-between border-t border-slate-200 px-4 py-3 dark:border-slate-800">
              <button
                type="button"
                disabled={page <= 1 || backendStatus !== "healthy"}
                onClick={() => setPage((current) => current - 1)}
                className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm disabled:opacity-50 dark:border-slate-700"
              >
                Previous
              </button>
              <span className="text-sm text-slate-500 dark:text-slate-400">
                Page {page} of {totalPages}
              </span>
              <button
                type="button"
                disabled={page >= totalPages || backendStatus !== "healthy"}
                onClick={() => setPage((current) => current + 1)}
                className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm disabled:opacity-50 dark:border-slate-700"
              >
                Next
              </button>
            </div>
          </>
        )}
      </section>
    </div>
  );
}
