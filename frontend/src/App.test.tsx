import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, test, vi, beforeEach, afterEach } from "vitest";
import App from "./App";

function mockJsonResponse(body: unknown, ok = true) {
  return Promise.resolve({
    ok,
    json: async () => body,
  });
}

describe("App", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("loads saved report history on page load", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn((url) => {
        if (url === "/reports") {
          return mockJsonResponse({
            reports: [
              {
                report_id: "report_new",
                filename: "report_new.md",
                created_at: "2026-05-08T12:00:00Z",
              },
              {
                report_id: "report_old",
                filename: "report_old.md",
                created_at: "2026-05-08T10:00:00Z",
              },
            ],
          });
        }

        return mockJsonResponse({});
      })
    );

    render(<App />);

    expect(await screen.findByText("report_new")).toBeInTheDocument();
    expect(screen.getByText("report_old")).toBeInTheDocument();
  });

  test("loads selected saved report into output area", async () => {
    const user = userEvent.setup();

    vi.stubGlobal(
      "fetch",
      vi.fn((url) => {
        if (url === "/reports") {
          return mockJsonResponse({
            reports: [
              {
                report_id: "report_new",
                filename: "report_new.md",
                created_at: "2026-05-08T12:00:00Z",
              },
            ],
          });
        }

        if (url === "/reports/report_new") {
          return mockJsonResponse({
            report_id: "report_new",
            filename: "report_new.md",
            content: "# Saved Report\n\nThis came from DB.",
            created_at: "2026-05-08T12:00:00Z",
          });
        }

        return mockJsonResponse({});
      })
    );

    render(<App />);

    await user.click(await screen.findByText("report_new"));

    const reportOutput = screen.getByLabelText(/report output/i);

    expect(await within(reportOutput).findByText(/# Saved Report/i)).toBeInTheDocument();
    expect(within(reportOutput).getByText(/this came from db/i)).toBeInTheDocument();
  });

  test("generates report, displays it, and refreshes history", async () => {
    const user = userEvent.setup();

    vi.stubGlobal(
      "fetch",
      vi.fn((url, options) => {
        if (url === "/reports") {
          return mockJsonResponse({
            reports: [
              {
                report_id: "report_generated",
                filename: "report_generated.md",
                created_at: "2026-05-08T12:00:00Z",
              },
            ],
          });
        }

        if (url === "/query" && options?.method === "POST") {
          return mockJsonResponse({
            report_id: "report_generated",
            query: "summarize the current meta",
            plan: {},
            analyst_output: {
              headline: "Generated Meta Watch",
              key_findings: [],
              meta_summary: "Generated report body.",
              caveats: [],
            },
            report_md: "# Generated Meta Watch\n\nGenerated report body.",
            generated_at: "2026-05-08T12:00:00Z",
          });
        }

        return mockJsonResponse({});
      })
    );

    render(<App />);

    await user.click(screen.getByRole("button", { name: /generate report/i }));

    expect(await screen.findByText(/generated meta watch/i)).toBeInTheDocument();
    expect(screen.getByText("report_generated")).toBeInTheDocument();
  });
});