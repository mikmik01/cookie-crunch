import { useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

type HeroRecommendation = {
  hero: string;
  lane?: string | null;
  tier?: string | null;
  win_rate?: number | null;
  pick_rate?: number | null;
  ban_rate?: number | null;
};

type RoleSummary = {
  lane: string;
  heroes: HeroRecommendation[];
};

type QueryResponse = {
  report_id: string;
  query: string;
  plan: Record<string, unknown>;
  recommendations: HeroRecommendation[];
  role_summary: RoleSummary[];
  generated_at: string;
};

function Spinner() {
  return (
    <span
      className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"
      aria-hidden="true"
    />
  );
}

function formatPercent(value?: number | null) {
  if (value === null || value === undefined) {
    return "-";
  }

  return `${value.toFixed(2)}%`;
}

function HeroMetric({
  label,
  value,
}: {
  label: string;
  value?: number | null;
}) {
  return (
    <div className="rounded-lg bg-slate-50 px-3 py-2">
      <p className="text-[11px] uppercase tracking-wide text-slate-500">
        {label}
      </p>
      <p className="mt-1 text-sm font-semibold text-slate-950">
        {formatPercent(value)}
      </p>
    </div>
  );
}

function App() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function generateReport() {
    const trimmedQuery = query.trim();

    try {
      const response = await fetch(`${API_BASE_URL}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: trimmedQuery }),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.detail || "Failed to generate recommendations.");
      }

      setResult(data as QueryResponse);
    } catch (error) {
    } finally {
      setIsLoading(false);
    }
  }

  const recommendations = result?.recommendations?.slice(0, 5) ?? [];

  return (
    <main
      className="min-h-screen px-3 py-5 text-slate-950 sm:px-6 sm:py-8 lg:px-8"
      style={{
        backgroundColor: "#fdecef",
        backgroundImage:
          "linear-gradient(rgba(255, 247, 251, 0.68), rgba(255, 247, 251, 0.68)), url('/strawberry.jpg')",
        backgroundRepeat: "repeat",
        backgroundSize: "360px auto",
        backgroundPosition: "center top",
      }}
    >
      <section className="mx-auto w-full max-w-6xl">
        <header className="mb-5 sm:mb-7">
          <h1 className="font-cute mt-2 text-[3.2rem] leading-none text-[#ff4f9a] sm:text-[4rem]">
            Find the strongest heroes!!
          </h1>

          <p className="font-cute mt-2 max-w-2xl text-sm leading-6 text-slate-600">
            Ask for current MLBB hero recommendations by lane, role, win rate,
            pick rate, or ban rate.
          </p>
        </header>

        <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-6">
          <label
            htmlFor="queryInput"
            className="font-cute mb-2 block text-sm font-medium text-slate-800"
          >
            Ask away~
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
              placeholder="e.g. best roamers"
              className="min-h-12 min-w-0 flex-1 rounded-xl border border-slate-300 bg-white px-4 py-3 text-base outline-none transition placeholder:text-slate-400 focus:border-slate-950 focus:ring-2 focus:ring-slate-200 sm:text-sm"
            />

            <button
              onClick={generateReport}
              disabled={isLoading}
              className="font-cute min-h-12 rounded-xl bg-slate-950 px-5 py-3 text-sm font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <Spinner />
                  Generating...
                </span>
              ) : (
                "Generate"
              )}
            </button>
          </div>
        </section>

        <section
          className="mt-5 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:mt-6 sm:p-6"
          aria-label="Recommendation output"
        >
          {!result ? (
            <div className="font-cute flex min-h-64 items-center justify-center rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 text-center text-sm text-slate-500">
              No recommendations generated yet.
            </div>
          ) : (
            <div className="space-y-8">
              <div>
                <div className="mb-4 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
                  <div>
                    <h2 className="font-cute text-3xl tracking-wide text-pink-700">
                      Recommendations
                    </h2>
                  </div>

                  <p className="text-xs text-slate-500">
                    {new Date(result.generated_at).toLocaleString()}
                  </p>
                </div>

                {recommendations.length === 0 ? (
                  <div className="rounded-xl border border-slate-200 bg-slate-50 p-5 text-sm text-slate-500">
                    No heroes matched this query.
                  </div>
                ) : (
                  <>
                    <div className="space-y-3 md:hidden">
                      {recommendations.map((hero, index) => (
                        <article
                          key={`${hero.hero}-${hero.lane}-${index}`}
                          className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
                        >
                          <div className="flex items-start justify-between gap-3">
                            <div>
                              <h3 className="text-base font-semibold">
                                {hero.hero}
                              </h3>
                              <p className="mt-1 text-sm text-slate-500">
                                {hero.lane || "-"}
                              </p>
                            </div>

                            <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">
                              {hero.tier || "-"}
                            </span>
                          </div>

                          <div className="mt-4 grid grid-cols-3 gap-2">
                            <HeroMetric
                              label="Win"
                              value={hero.win_rate}
                            />
                            <HeroMetric
                              label="Pick"
                              value={hero.pick_rate}
                            />
                            <HeroMetric
                              label="Ban"
                              value={hero.ban_rate}
                            />
                          </div>
                        </article>
                      ))}
                    </div>

                    <div className="hidden overflow-hidden rounded-xl border border-slate-200 md:block">
                      <div className="overflow-x-auto">
                        <table className="w-full border-collapse bg-white text-left text-sm">
                          <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                            <tr>
                              <th className="px-4 py-3">Hero</th>
                              <th className="px-4 py-3">Lane</th>
                              <th className="px-4 py-3">Tier</th>
                              <th className="px-4 py-3 text-right">
                                Win Rate
                              </th>
                              <th className="px-4 py-3 text-right">
                                Pick Rate
                              </th>
                              <th className="px-4 py-3 text-right">
                                Ban Rate
                              </th>
                            </tr>
                          </thead>

                          <tbody>
                            {recommendations.map((hero, index) => (
                              <tr
                                key={`${hero.hero}-${hero.lane}-${index}`}
                                className="border-t border-slate-100 hover:bg-slate-50"
                              >
                                <td className="px-4 py-3 font-medium text-slate-950">
                                  {hero.hero}
                                </td>
                                <td className="px-4 py-3 text-slate-700">
                                  {hero.lane || "-"}
                                </td>
                                <td className="px-4 py-3">
                                  <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-medium text-slate-700">
                                    {hero.tier || "-"}
                                  </span>
                                </td>
                                <td className="px-4 py-3 text-right tabular-nums">
                                  {formatPercent(hero.win_rate)}
                                </td>
                                <td className="px-4 py-3 text-right tabular-nums">
                                  {formatPercent(hero.pick_rate)}
                                </td>
                                <td className="px-4 py-3 text-right tabular-nums">
                                  {formatPercent(hero.ban_rate)}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </>
                )}
              </div>

              {result.role_summary.length > 0 && (
                <div>
                  <h2 className="font-cute mb-4 text-3xl tracking-wide text-pink-700">
                    Strongest Heroes by Lane
                  </h2>

                  <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                    {result.role_summary.map((group) => (
                      <div
                        key={group.lane}
                        className="rounded-xl border border-slate-200 bg-slate-50 p-4"
                      >
                        <div className="mb-3 flex items-center justify-between">
                          <h3 className="font-cute text-xl tracking-wide text-pink-700">
                            {group.lane}
                          </h3>
                          <span className="text-xs text-slate-500">
                            Top {group.heroes.length}
                          </span>
                        </div>

                        <div className="space-y-2">
                          {group.heroes.map((hero, index) => (
                            <div
                              key={`${group.lane}-${hero.hero}-${index}`}
                              className="rounded-lg bg-white px-3 py-3 shadow-sm"
                            >
                              <div className="flex items-start justify-between gap-3">
                                <div className="min-w-0">
                                  <p className="truncate font-medium">
                                    {hero.hero}
                                  </p>
                                  <p className="mt-1 text-xs text-slate-500">
                                    Tier {hero.tier || "-"}
                                  </p>
                                </div>

                                <div className="shrink-0 text-right text-xs text-slate-600">
                                  <p>WR {formatPercent(hero.win_rate)}</p>
                                  <p>Pick {formatPercent(hero.pick_rate)}</p>
                                  <p>Ban {formatPercent(hero.ban_rate)}</p>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}

export default App;