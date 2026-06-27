import { useEffect } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { GlobalLoadingIndicator } from "./components/GlobalLoadingIndicator";
import { ToastContainer } from "./components/ToastContainer";
import { AppProvider, useAppContext } from "./context/AppContext";
import { DashboardLayout } from "./layouts/DashboardLayout";
import { DashboardPage } from "./pages/DashboardPage";
import { EvaluationPage } from "./pages/EvaluationPage";
import { IncidentDetailPage } from "./pages/IncidentDetailPage";
import { IncidentsPage } from "./pages/IncidentsPage";
import { InvestigationRunnerPage } from "./pages/InvestigationRunnerPage";
import { LogUploadPage } from "./pages/LogUploadPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { ReportsPage } from "./pages/ReportsPage";
import { SettingsPage } from "./pages/SettingsPage";
import { registerLoadingHandler } from "./services/apiClient";

function AppShell() {
  const { setLoading } = useAppContext();

  useEffect(() => {
    registerLoadingHandler(setLoading);
  }, [setLoading]);

  return (
    <>
      <GlobalLoadingIndicator />
      <ToastContainer />
      <Routes>
        <Route element={<DashboardLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="incidents" element={<IncidentsPage />} />
          <Route path="incidents/:id/investigate" element={<InvestigationRunnerPage />} />
          <Route path="incidents/:id" element={<IncidentDetailPage />} />
          <Route path="logs" element={<LogUploadPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="evaluation" element={<EvaluationPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <AppProvider>
        <BrowserRouter>
          <AppShell />
        </BrowserRouter>
      </AppProvider>
    </ErrorBoundary>
  );
}
