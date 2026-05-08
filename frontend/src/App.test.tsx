import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, test, vi, beforeEach, afterEach } from "vitest";
import App from "./App";

describe("App", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("renders query input and empty report output", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: /mlbb meta drafter/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/query/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /generate report/i })).toBeInTheDocument();
    expect(screen.getByText(/no report generated yet/i)).toBeInTheDocument();
  });

  test("submits query and displays returned report", async () => {
    const user = userEvent.setup();

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        text: async () =>
          'data: {"step":"done","message":"Report ready.","done":true,"data":{"report_id":"report_2026-05-08_120000","query":"summarize the current meta","report_md":"# Mid Lane Meta Watch\\n\\nCecilion is strong."}}',
      })
    );

    render(<App />);

    const input = screen.getByLabelText(/query/i);
    await user.clear(input);
    await user.type(input, "summarize the current meta");
    await user.click(screen.getByRole("button", { name: /generate report/i }));

    expect(fetch).toHaveBeenCalledWith("/query", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query: "summarize the current meta",
      }),
    });

    expect(await screen.findByText(/mid lane meta watch/i)).toBeInTheDocument();
    expect(screen.getByText(/cecilion is strong/i)).toBeInTheDocument();
  });

  test("shows an error message when report generation fails", async () => {
    const user = userEvent.setup();

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        json: async () => ({
          detail: "No local reports found.",
        }),
      })
    );

    render(<App />);

    await user.click(screen.getByRole("button", { name: /generate report/i }));

    expect(await screen.findByText(/no local reports found/i)).toBeInTheDocument();
  });
});