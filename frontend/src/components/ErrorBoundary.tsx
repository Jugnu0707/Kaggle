import { Component, type ErrorInfo, type ReactNode } from "react";
import { ErrorState } from "./ui";

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  message: string;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, message: "" };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, message: error.message };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error("Unhandled UI error:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-slate-100 p-6 dark:bg-slate-900">
          <div className="max-w-lg w-full">
            <ErrorState
              title="Something went wrong"
              message={this.state.message || "An unexpected error occurred in the dashboard."}
              onRetry={() => this.setState({ hasError: false, message: "" })}
            />
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
