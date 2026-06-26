import { Outlet } from "react-router-dom";
import { BackendUnavailableBanner } from "../components/BackendUnavailableBanner";
import { Navbar } from "../components/Navbar";
import { Sidebar } from "../components/Sidebar";

export function DashboardLayout() {
  return (
    <div className="flex min-h-screen bg-slate-100 dark:bg-slate-900">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Navbar />
        <BackendUnavailableBanner />
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
