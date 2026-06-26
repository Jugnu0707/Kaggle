import { EmptyState } from "../components/ui";

export function ReportsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">Reports</h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Executive and technical reporting will be available in a future sprint
        </p>
      </div>
      <EmptyState
        title="Reports coming soon"
        description="Report generation is not part of Sprint 1. This section is reserved for future release."
      />
    </div>
  );
}
