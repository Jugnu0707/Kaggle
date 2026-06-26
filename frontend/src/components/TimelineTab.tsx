import { useMemo, useState } from "react";
import { Badge, ConfidenceBadge, EmptyState, LoadingSpinner } from "./ui";
import { exportIncidentTimeline, type TimelineEvent, type TimelineEventType } from "../services/timelineService";
import { formatDate } from "../utils/format";

const EVENT_TYPES: TimelineEventType[] = [
  "Alert",
  "Process Execution",
  "Authentication",
  "Network",
  "File",
  "Registry",
  "PowerShell",
  "EDR",
  "Firewall",
  "User Action",
  "AI Assessment",
];

const eventTypeIcons: Record<TimelineEventType, string> = {
  Alert: "⚠️",
  "Process Execution": "⚙️",
  Authentication: "🔐",
  Network: "🌐",
  File: "📄",
  Registry: "🗂️",
  PowerShell: "💻",
  EDR: "🛡️",
  Firewall: "🧱",
  "User Action": "👤",
  "AI Assessment": "🤖",
};

const severityNodeStyles: Record<string, string> = {
  Critical: "border-red-500 bg-red-500",
  High: "border-orange-500 bg-orange-500",
  Medium: "border-yellow-500 bg-yellow-400",
  Low: "border-blue-500 bg-blue-500",
};

interface TimelineTabProps {
  incidentId: string;
  timeline: TimelineEvent[] | null;
  summary: string | null;
  loading: boolean;
  error: string | null;
}

export function TimelineTab({
  incidentId,
  timeline,
  summary,
  loading,
  error,
}: TimelineTabProps) {
  const [search, setSearch] = useState("");
  const [eventTypeFilter, setEventTypeFilter] = useState<TimelineEventType | "all">("all");
  const [expandedSequences, setExpandedSequences] = useState<Set<number>>(new Set());

  const filteredEvents = useMemo(() => {
    if (!timeline) {
      return [];
    }

    const normalizedSearch = search.trim().toLowerCase();
    return timeline.filter((event) => {
      const matchesType = eventTypeFilter === "all" || event.event_type === eventTypeFilter;
      if (!matchesType) {
        return false;
      }
      if (!normalizedSearch) {
        return true;
      }
      return (
        event.description.toLowerCase().includes(normalizedSearch) ||
        event.source.toLowerCase().includes(normalizedSearch) ||
        event.event_type.toLowerCase().includes(normalizedSearch) ||
        (event.evidence_reference?.toLowerCase().includes(normalizedSearch) ?? false)
      );
    });
  }, [eventTypeFilter, search, timeline]);

  const toggleExpanded = (sequence: number) => {
    setExpandedSequences((current) => {
      const next = new Set(current);
      if (next.has(sequence)) {
        next.delete(sequence);
      } else {
        next.add(sequence);
      }
      return next;
    });
  };

  const downloadBlob = (blob: Blob, filename: string) => {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleExport = async (format: "json" | "markdown") => {
    const blob = await exportIncidentTimeline(incidentId, format);
    downloadBlob(blob, `timeline-${incidentId}.${format === "json" ? "json" : "md"}`);
  };

  if (loading) {
    return <LoadingSpinner label="Loading investigation timeline..." />;
  }

  if (error) {
    return <EmptyState title="Timeline unavailable" description={error} />;
  }

  if (!timeline || timeline.length === 0) {
    return (
      <EmptyState
        title="No timeline events"
        description="Upload logs and run agent analysis to reconstruct the investigation timeline."
      />
    );
  }

  return (
    <section className="space-y-6">
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">
              Investigation Timeline
            </h3>
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">{summary}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => void handleExport("json")}
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-900"
            >
              Export JSON
            </button>
            <button
              type="button"
              onClick={() => void handleExport("markdown")}
              className="rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700"
            >
              Export Markdown
            </button>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-[minmax(0,1fr)_220px]">
          <label className="block">
            <span className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Search
            </span>
            <input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search description, source, or evidence"
              className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
            />
          </label>
          <label className="block">
            <span className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Event Type
            </span>
            <select
              value={eventTypeFilter}
              onChange={(event) =>
                setEventTypeFilter(event.target.value as TimelineEventType | "all")
              }
              className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
            >
              <option value="all">All event types</option>
              {EVENT_TYPES.map((eventType) => (
                <option key={eventType} value={eventType}>
                  {eventType}
                </option>
              ))}
            </select>
          </label>
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
        <div className="mb-4 text-sm text-slate-600 dark:text-slate-300">
          Showing {filteredEvents.length} of {timeline.length} events
        </div>

        {filteredEvents.length === 0 ? (
          <EmptyState
            title="No matching events"
            description="Adjust your search or event type filter to view timeline events."
          />
        ) : (
          <ol className="relative space-y-0">
            {filteredEvents.map((event, index) => {
              const expanded = expandedSequences.has(event.sequence);
              const nodeStyle =
                severityNodeStyles[event.severity] ?? "border-slate-400 bg-slate-400";

              return (
                <li key={`${event.sequence}-${event.timestamp}`} className="relative flex gap-4 pb-8">
                  {index < filteredEvents.length - 1 && (
                    <span
                      className="absolute left-[15px] top-8 h-[calc(100%-1rem)] w-px bg-slate-200 dark:bg-slate-800"
                      aria-hidden="true"
                    />
                  )}
                  <div
                    className={`relative z-10 mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 text-sm ${nodeStyle}`}
                    title={event.event_type}
                  >
                    <span className="text-white drop-shadow">{eventTypeIcons[event.event_type]}</span>
                  </div>
                  <div className="min-w-0 flex-1 rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-900/60">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
                          #{event.sequence}
                        </span>
                        <Badge label={event.severity} />
                        <span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs font-medium text-slate-700 dark:bg-slate-800 dark:text-slate-200">
                          {event.event_type}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                        {event.timestamp_uncertain && (
                          <span title="Timestamp uncertain">⚠️ uncertain</span>
                        )}
                        <time>{formatDate(event.timestamp)}</time>
                      </div>
                    </div>

                    <p className="mt-3 text-sm leading-6 text-slate-800 dark:text-slate-100">
                      {event.description}
                    </p>

                    <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-slate-600 dark:text-slate-300">
                      <span>Source: {event.source}</span>
                      <ConfidenceBadge value={event.confidence} />
                    </div>

                    <button
                      type="button"
                      onClick={() => toggleExpanded(event.sequence)}
                      className="mt-3 text-xs font-medium text-indigo-600 hover:underline dark:text-indigo-400"
                    >
                      {expanded ? "Hide details" : "Show details"}
                    </button>

                    {expanded && (
                      <dl className="mt-3 grid gap-2 rounded-lg border border-slate-200 bg-white p-3 text-xs dark:border-slate-700 dark:bg-slate-950">
                        <div>
                          <dt className="font-medium text-slate-500 dark:text-slate-400">
                            Evidence Reference
                          </dt>
                          <dd className="mt-1 font-mono text-slate-800 dark:text-slate-100">
                            {event.evidence_reference ?? "Not available"}
                          </dd>
                        </div>
                        <div>
                          <dt className="font-medium text-slate-500 dark:text-slate-400">
                            Event ID
                          </dt>
                          <dd className="mt-1 font-mono text-slate-800 dark:text-slate-100">
                            {event.id ?? "Generated at request time"}
                          </dd>
                        </div>
                      </dl>
                    )}
                  </div>
                </li>
              );
            })}
          </ol>
        )}
      </section>
    </section>
  );
}
