import type { ReactNode } from "react";

const severityStyles: Record<string, string> = {
  Critical: "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-200",
  High: "bg-orange-100 text-orange-800 dark:bg-orange-950 dark:text-orange-200",
  Medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-950 dark:text-yellow-200",
  Low: "bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-200",
  New: "bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200",
  Investigating: "bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-200",
  Resolved: "bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-200",
  Closed: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
  Completed: "bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-200",
  Deleted: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  Failed: "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-200",
};

const confidenceStyles: Record<string, string> = {
  High: "bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-200",
  Medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-950 dark:text-yellow-200",
  Low: "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300",
};

interface BadgeProps {
  label: string;
  tone?: keyof typeof severityStyles;
}

export function Badge({ label, tone }: BadgeProps) {
  const style = severityStyles[tone ?? label] ?? severityStyles.New;

  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${style}`}>
      {label}
    </span>
  );
}

export function ConfidenceBadge({ value }: { value: number }) {
  const tone = value >= 90 ? "High" : value >= 75 ? "Medium" : "Low";
  const style = confidenceStyles[tone];

  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${style}`}>
      {value}% · {tone}
    </span>
  );
}

const sourceStyles: Record<string, string> = {
  AI: "bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-200",
  FALLBACK: "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300",
};

export function SourceBadge({ source }: { source: "AI" | "FALLBACK" }) {
  const style = sourceStyles[source];
  const label = source === "AI" ? "🤖 AI" : "⚙️ Fallback Engine";

  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${style}`}>
      {label}
    </span>
  );
}

const validationStyles: Record<string, string> = {
  approved: "bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-200",
  warning: "bg-orange-100 text-orange-800 dark:bg-orange-950 dark:text-orange-200",
  rejected: "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-200",
};

export function ValidationBadge({ status }: { status: "approved" | "warning" | "rejected" }) {
  const style = validationStyles[status] ?? validationStyles.approved;
  const label = status.charAt(0).toUpperCase() + status.slice(1);

  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${style}`}>
      {label}
    </span>
  );
}

const reputationStyles: Record<string, string> = {
  Malicious: "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-200",
  Suspicious: "bg-orange-100 text-orange-800 dark:bg-orange-950 dark:text-orange-200",
  Unknown: "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300",
  Safe: "bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-200",
  Informational: "bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-200",
};

export function ReputationBadge({ reputation }: { reputation: string }) {
  const style = reputationStyles[reputation] ?? reputationStyles.Unknown;

  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${style}`}>
      {reputation}
    </span>
  );
}

interface StatisticCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
}

export function StatisticCard({ title, value, subtitle }: StatisticCardProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{title}</p>
      <p className="mt-2 text-3xl font-semibold text-slate-900 dark:text-slate-100">{value}</p>
      {subtitle && <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{subtitle}</p>}
    </div>
  );
}

export function LoadingSpinner({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-slate-500 dark:text-slate-400">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-slate-300 border-t-slate-700 dark:border-slate-700 dark:border-t-slate-200" />
      <p className="mt-3 text-sm">{label}</p>
    </div>
  );
}

interface EmptyStateProps {
  title: string;
  description: string;
  action?: ReactNode;
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-6 py-12 text-center dark:border-slate-700 dark:bg-slate-900/50">
      <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">{title}</h3>
      <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">{description}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export function ErrorState({
  title = "Something went wrong",
  message,
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="rounded-xl border border-red-200 bg-red-50 px-6 py-8 text-center dark:border-red-900 dark:bg-red-950/30">
      <h3 className="text-lg font-medium text-red-800 dark:text-red-200">{title}</h3>
      <p className="mt-2 text-sm text-red-700 dark:text-red-300">{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-4 rounded-lg bg-red-700 px-4 py-2 text-sm font-medium text-white hover:bg-red-800"
        >
          Try Again
        </button>
      )}
    </div>
  );
}
