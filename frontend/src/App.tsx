import { useEffect, useState } from "react";

type ReportSummary = {
  report_id: string;
  filename: string;
  created_at: string;
};

type ReportListResponse = {
  reports: ReportSummary[];
};

type ReportDetailResponse = {
  report_id: string;
  filename: string;
  content: string;
  created_at: string;
};

type QueryResponse = {
  report_id: string;
  query: string;
  report_md: string;
};

function App() {
  const [query, setQuery] = useState("summarize the current meta");
  const [reports, setReports] = useState<ReportSummary[]>([]);
  const [report, setReport] = useState("");
  const [status, setStatus] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function loadReports() {
    const response = await fetch("/reports");

    if (!response.ok) {
      throw new Error("Failed to load saved reports.");
    }

    const data: ReportListResponse = await response.json();
    setReports(data.reports);
  }

  async function loadReport(reportId: string) {
    setStatus(`Loading ${reportId}...`);

    const response = await fetch(`/reports/${reportId}`);

    if (!response.ok) {
      throw new Error("Failed to load report.");
    }

    const data: ReportDetailResponse = await response.json();

    setReport(data.content);
    setStatus(`Loaded ${data.report_id}`);
  }

  async function generateReport() {
    const trimmedQuery = query.trim();

    if (!trimmedQuery) {
      setStatus("Please enter a query.");
      return;
    }

    setIsLoading(true);
    setStatus("Generating report...");
    setReport("");

    try {
      const response = await fetch("/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: trimmedQuery }),
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || "Failed to generate report.");
      }

      const data: QueryResponse = await response.json();

      setReport(data.report_md);
      setStatus(`Generated ${data.report_id}`);
      await loadReports();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Something went wrong.";
      setStatus(message);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadReports().catch((error) => {
      const message = error instanceof Error ? error.message : "Failed to load reports.";
      setStatus(message);
    });
  }, []);

  return (
    <main className="min-h-screen bg-slate-100 px-6 py-10 text-slate-950">
      <section className="mx-auto grid max-w-6xl gap-6 lg:grid-cols-[280px_1fr]">
        <aside className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold">Saved Reports</h2>

          <div className="mt-4 space-y-2">
            {reports.length === 0 ? (
              <p className="text-sm text-slate-500">No saved reports yet.</p>
            ) : (
              reports.map((item) => (
                <button
                  key={item.report_id}
                  onClick={() => loadReport(item.report_id)}
                  className="w-full rounded-xl border border-slate-200 px-3 py-2 text-left text-sm hover:bg-slate-50"
                >
                  <div className="font-medium">{item.report_id}</div>
                  <div className="text-xs text-slate-500">
                    {new Date(item.created_at).toLocaleString()}
                  </div>
                </button>
              ))
            )}
          </div>
        </aside>

        <section className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="mb-8">
            <h1 className="text-3xl font-semibold tracking-tight">
              MLBB Meta Drafter
            </h1>
            <p className="mt-2 text-sm text-slate-600">
              Enter a meta query and display the generated report.
            </p>
          </div>

          <div className="mb-5">
            <label
              htmlFor="queryInput"
              className="mb-2 block text-sm font-medium text-slate-800"
            >
              Query
            </label>

            <div className="flex flex-col gap-3 sm:flex-row">
              <input
                id="queryInput"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    generateReport();
                  }
                }}
                placeholder="e.g. summarize the current meta"
                className="min-w-0 flex-1 rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
              />

              <button
                onClick={generateReport}
                disabled={isLoading}
                className="rounded-xl bg-slate-950 px-5 py-3 text-sm font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isLoading ? "Generating..." : "Generate Report"}
              </button>
            </div>
          </div>

          {status && (
            <p className="mb-4 rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-700">
              {status}
            </p>
          )}

          <section
            className="min-h-96 whitespace-pre-wrap rounded-xl border border-slate-200 bg-slate-50 p-5 font-mono text-sm leading-6 text-slate-900"
            aria-label="Report output"
          >
            {report ? report : "No report generated yet."}
          </section>
        </section>
      </section>
    </main>
  );
}

export default App;