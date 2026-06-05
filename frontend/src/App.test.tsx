import { render, screen } from "@testing-library/react";
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

  test("submits a query and displays hero recommendations", async () => {
    const user = userEvent.setup();

    vi.stubGlobal(
      "fetch",
      vi.fn((url, options) => {
        if (url === "/query" && options?.method === "POST") {
          return mockJsonResponse({
            query: "summarize the current meta",
            plan: {
              task_type: "summarize_meta",
              filters: {
                lane: null,
                hero: null,
                min_win_rate: null,
                max_win_rate: null,
                min_pick_rate: null,
                max_pick_rate: null,
                min_ban_rate: null,
                max_ban_rate: null,
                top_n: 5,
              },
            },
            recommendations: [
              {
                hero: "Alice",
                lane: "Mid",
                tier: "S",
                win_rate: 53.2,
                pick_rate: 8.4,
                ban_rate: 12.1,
              },
            ],
            role_summary: [
              {
                lane: "Mid",
                heroes: [
                  {
                    hero: "Alice",
                    tier: "S",
                    win_rate: 53.2,
                    pick_rate: 8.4,
                    ban_rate: 12.1,
                  },
                ],
              },
            ],
            generated_at: "2026-05-08T12:00:00Z",
          });
        }

        return mockJsonResponse({});
      })
    );

    render(<App />);

    await user.click(
      screen.getByRole("button", { name: /analyze|submit|search|generate/i })
    );

    expect((await screen.findAllByText("Alice")).length).toBeGreaterThan(0);
    expect(screen.getAllByText("Mid").length).toBeGreaterThan(0);
    expect(screen.getAllByText("S").length).toBeGreaterThan(0);
    expect(screen.getAllByText(/53\.2/).length).toBeGreaterThan(0);
  });
});