import { EmptyState } from "../components/ui";

export function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">Settings</h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Application configuration and preferences
        </p>
      </div>
      <EmptyState
        title="Settings placeholder"
        description="Authentication and advanced configuration are out of scope for Sprint 1."
      />
    </div>
  );
}
