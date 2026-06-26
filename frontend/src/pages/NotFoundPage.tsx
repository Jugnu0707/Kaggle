import { Link } from "react-router-dom";
import { EmptyState } from "../components/ui";

export function NotFoundPage() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <EmptyState
        title="Page not found"
        description="The page you requested does not exist or may have been moved."
        action={
          <Link
            to="/"
            className="inline-flex rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
          >
            Return to dashboard
          </Link>
        }
      />
    </div>
  );
}
