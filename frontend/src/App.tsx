import { useState } from "react";

type QueryResponse = {
  report_id?: string;
  query?: string;
  report_md?: string;
  report_markdown?: string;
};

type StreamEvent = {
  step?: string;
  message?: string;
  done?: boolean;
  error?: string | null;
  data?: QueryResponse;
};

async function parseQueryResponse(response: Response): Promise<QueryResponse> {
  const rawText = await response.text();

  if (!response.ok) {
    try {
      const errorBody = JSON.parse(rawText);
      throw new Error(errorBody.detail || "Failed to generate report.");
    } catch {
      throw new Error(rawText || "Failed to generate report.");
    }
  }

  const trimmed = rawText.trim();

  if (trimmed.startsWith("data:")) {
    const events: StreamEvent[] = trimmed
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line.startsWith("data:"))
      .map((line) => JSON.parse(line.replace(/^data:\s*/, "")));

    const doneEvent =
      events.find((event) => event.done && event.data) ||
      events[events.length - 1];

    if (doneEvent.error) {
      throw new Error(doneEvent.error);
    }

    if (doneEvent.data) {
      return doneEvent.data;
    }

    throw new Error("No report data returned.");
  }

  return JSON.parse(trimmed);
}

function App() {
  const [query, setQuery] = useState("summarize the current meta");
  const [report, setReport] = useState("");
  const [status, setStatus] = useState("");
  const [isLoading, setIsLoading] = useState(false);

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
        body: JSON.stringify({
          query: trimmedQuery,
        }),
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || "Failed to generate report.");
      }

      const data = await parseQueryResponse(response);

      setStatus(data.report_id ? `Generated ${data.report_id}` : "Report generated.");
      setReport(data.report_md || data.report_markdown || "");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Something went wrong.";
      setStatus(message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-100 px-6 py-10 text-slate-950">
      <section className="mx-auto max-w-5xl rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
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
    </main>
  );
}

export default App;