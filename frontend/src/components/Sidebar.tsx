import { NavLink } from "react-router-dom";

const navItems = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/incidents", label: "Incidents" },
  { to: "/logs", label: "Log Uploads" },
  { to: "/reports", label: "Reports" },
  { to: "/settings", label: "Settings" },
];

export function Sidebar() {
  return (
    <aside className="flex w-64 shrink-0 flex-col border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950">
      <div className="border-b border-slate-200 px-6 py-5 dark:border-slate-800">
        <p className="text-xs font-semibold uppercase tracking-widest text-indigo-600 dark:text-indigo-400">
          Oz AI
        </p>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Security Operations</p>
      </div>
      <nav className="flex-1 space-y-1 p-4">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              `block rounded-lg px-3 py-2 text-sm font-medium transition ${
                isActive
                  ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-950/50 dark:text-indigo-300"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-900 dark:hover:text-white"
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
