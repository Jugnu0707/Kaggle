import { useCallback, useRef, useState, type ChangeEvent, type DragEvent } from "react";
import { useAppContext } from "../context/AppContext";
import { getErrorMessage } from "../services/apiClient";
import { validateLogFile } from "../services/logService";

interface FileUploadProps {
  onUpload: (file: File, onProgress: (progress: number) => void) => Promise<void>;
  disabled?: boolean;
}

export function FileUpload({ onUpload, disabled = false }: FileUploadProps) {
  const { showToast } = useAppContext();
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFile = useCallback(
    (file: File | undefined) => {
      if (!file) {
        return;
      }
      const validationError = validateLogFile(file);
      if (validationError) {
        setError(validationError);
        setSelectedFile(null);
        showToast({
          title: "Invalid file",
          message: validationError,
          variant: "error",
        });
        return;
      }
      setSelectedFile(file);
      setError(null);
    },
    [showToast],
  );

  const onDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
    if (disabled || uploading) {
      return;
    }
    handleFile(event.dataTransfer.files[0]);
  };

  const onBrowse = (event: ChangeEvent<HTMLInputElement>) => {
    handleFile(event.target.files?.[0]);
    event.target.value = "";
  };

  const startUpload = async () => {
    if (!selectedFile || uploading || disabled) {
      return;
    }

    setUploading(true);
    setProgress(0);
    setError(null);

    try {
      await onUpload(selectedFile, setProgress);
      showToast({
        title: "Upload complete",
        message: `${selectedFile.name} uploaded successfully.`,
        variant: "success",
      });
      setSelectedFile(null);
      setProgress(100);
    } catch (uploadError) {
      const message = getErrorMessage(uploadError);
      setError(message);
      showToast({
        title: "Upload failed",
        message,
        variant: "error",
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        className={`rounded-xl border-2 border-dashed px-6 py-10 text-center transition ${
          isDragging
            ? "border-indigo-500 bg-indigo-50 dark:bg-indigo-950/20"
            : "border-slate-300 bg-slate-50 dark:border-slate-700 dark:bg-slate-900/50"
        } ${disabled ? "opacity-60" : ""}`}
      >
        <p className="text-sm font-medium text-slate-700 dark:text-slate-200">
          Drag and drop a log file here
        </p>
        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
          .log, .txt, .csv, .json, .evtx up to 50 MB
        </p>
        <button
          type="button"
          disabled={disabled || uploading}
          onClick={() => inputRef.current?.click()}
          className="mt-4 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60 dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-white"
        >
          Browse Files
        </button>
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept=".log,.txt,.csv,.json,.evtx"
          onChange={onBrowse}
        />
      </div>

      {selectedFile && (
        <div className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm dark:border-slate-800 dark:bg-slate-900">
          <p className="font-medium text-slate-900 dark:text-slate-100">{selectedFile.name}</p>
          <p className="text-slate-500 dark:text-slate-400">
            {(selectedFile.size / 1024).toFixed(1)} KB selected
          </p>
          <button
            type="button"
            disabled={uploading || disabled}
            onClick={() => void startUpload()}
            className="mt-3 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {uploading ? "Uploading..." : "Upload File"}
          </button>
        </div>
      )}

      {uploading && (
        <div>
          <div className="mb-1 flex justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>Upload progress</span>
            <span>{progress}%</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
            <div
              className="h-full rounded-full bg-indigo-600 transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-300">
          {error}
        </div>
      )}
    </div>
  );
}
