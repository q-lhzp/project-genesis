// ---------------------------------------------------------------------------
// Economy Tools - Extracted from index.ts
// ---------------------------------------------------------------------------

import { Type } from "@sinclair/typebox";
import { readJson, writeJson, generateId } from "../utils/persistence.js";
import { execFilePromise } from "../utils/bridge-executor.js";
import { join } from "node:path";
import type { FinanceState, JobType } from "../types/simulation.js";
import type { SimulationPaths, ToolModules } from "../types/paths.js";
import type { OpenClawPluginApi } from "openclaw/plugin-sdk";

// Helper to ensure tool return has details field
function toolResult(text: string): any {
  return { content: [{ type: "text", text }], details: {} };
}

export function registerEconomyTools(
  api: OpenClawPluginApi,
  paths: SimulationPaths,
  vaultPaths: SimulationPaths,
  modules: ToolModules,
  workspacePath: string
): void {
  // Tool: reality_work
  api.registerTool({
    name: "reality_work",
    description: "Work at a job to earn money.",
    parameters: Type.Object({
      action: Type.String({ description: "Action: work | list_jobs | resign | apply" }),
      position: Type.Optional(Type.String({ description: "Job position" })),
      employer: Type.Optional(Type.String({ description: "Employer name" })),
      salary: Type.Optional(Type.Number({ description: "Monthly salary" })),
    }),
    async execute(_id: string, params: { action: string; position?: string; employer?: string; salary?: number }): Promise<any> {
      if (!modules.economy) return { content: [{ type: "text", text: "Economy module not enabled." }], details: {} };

      const finance = await readJson<FinanceState>(paths.finances);
      if (!finance) return { content: [{ type: "text", text: "finances.json not found." }], details: {} };

      if (params.action === "work") {
        const income = finance.income_sources.find(i => !i.ended_at);
        if (!income) return { content: [{ type: "text", text: "No active job. Apply first." }], details: {} };

        finance.balance += income.salary_per_month / 30; // Daily rate
        await writeJson(paths.finances, finance);
        return { content: [{ type: "text", text: `Worked. Earned ${income.salary_per_month / 30} Credits.` }] };
      }

      if (params.action === "apply" && params.position && params.employer && params.salary) {
        finance.income_sources.push({
          id: generateId("job"),
          source_name: params.position,
          job_type: "full_time" as JobType,
          position: params.position,
          employer_id: null,
          salary_per_month: params.salary,
          salary_per_hour: null,
          hours_per_week: null,
          started_at: new Date().toISOString(),
          ended_at: null,
        });
        await writeJson(paths.finances, finance);
        return { content: [{ type: "text", text: `Applied for: ${params.position} at ${params.employer}` }] };
      }

      return { content: [{ type: "text", text: "Use: reality_work(action: 'work') or reality_work(action: 'apply', position: '...', employer: '...', salary: 3000)" }] };
    },
  });

  // Tool: reality_shop
  api.registerTool({
    name: "reality_shop",
    description: "Buy items from inventory.",
    parameters: Type.Object({
      item: Type.String({ description: "Item name" }),
      quantity: Type.Optional(Type.Number({ description: "Quantity" })),
    }),
    async execute(_id: string, params: { item: string; quantity?: number }) {
      if (!modules.economy) return { content: [{ type: "text", text: "Economy module not enabled." }], details: {} };

      const finance = await readJson<FinanceState>(paths.finances);
      if (!finance) return { content: [{ type: "text", text: "finances.json not found." }], details: {} };

      // Simple price estimation
      const price = 10 * (params.quantity ?? 1);

      if (finance.balance < price) {
        return { content: [{ type: "text", text: `Insufficient funds. Need ${price}, have ${finance.balance}.` }] };
      }

      finance.balance -= price;
      await writeJson(paths.finances, finance);
      return { content: [{ type: "text", text: `Bought: ${params.item} (${params.quantity ?? 1}) for ${price} Credits.` }] };
    },
  });

  // Tool: reality_trade (Phase 21 - The Vault)
  api.registerTool({
    name: "reality_trade",
    description: "Trade real assets (crypto/stocks) via The Vault. Use 'check' to view portfolio, 'buy'/'sell' to trade, 'report' to mark morning analysis as done.",
    parameters: Type.Object({
      action: Type.String({ description: "Action: check | buy | sell | report" }),
      symbol: Type.Optional(Type.String({ description: "Asset symbol (e.g., BTC, AAPL)" })),
      amount: Type.Optional(Type.Number({ description: "Amount in EUR" })),
    }),
    async execute(_id: string, params: { action: string; symbol?: string; amount?: number }) {
      const vaultBridge = join(workspacePath, "tools", "vault_bridge.py");

      if (params.action === "check") {
        try {
          const { stdout } = await execFilePromise(vaultBridge, ["check"], { timeout: 30000 });
          const vaultState = JSON.parse(stdout);
          const lines = ["## The Vault - Portfolio\n"];

          if (vaultState.positions) {
            for (const pos of vaultState.positions) {
              const value = pos.amount * pos.current_price;
              lines.push(`- ${pos.symbol}: ${pos.amount} @ ${pos.current_price}€ = ${value.toFixed(2)}€ (${pos.pnl}%)`);
            }
          }
          lines.push(`\nTotal Value: ${vaultState.total_value?.toFixed(2) || "0"}€`);
          lines.push(`Cash: ${vaultState.cash?.toFixed(2) || "0"}€`);

          return { content: [{ type: "text", text: lines.join("\n") }] };
        } catch (error) {
          return { content: [{ type: "text", text: "Vault error: " + String(error) }] };
        }
      }

      if (params.action === "buy" && params.symbol && params.amount) {
        try {
          await execFilePromise(vaultBridge, ["buy", params.symbol, String(params.amount)], { timeout: 30000 });
          return { content: [{ type: "text", text: `Bought ${params.amount}€ of ${params.symbol}` }] };
        } catch (error) {
          return { content: [{ type: "text", text: "Trade error: " + String(error) }] };
        }
      }

      if (params.action === "sell" && params.symbol && params.amount) {
        try {
          await execFilePromise(vaultBridge, ["sell", params.symbol, String(params.amount)], { timeout: 30000 });
          return { content: [{ type: "text", text: `Sold ${params.amount}€ of ${params.symbol}` }] };
        } catch (error) {
          return { content: [{ type: "text", text: "Trade error: " + String(error) }] };
        }
      }

      return { content: [{ type: "text", text: "Use: reality_trade(action: 'check' | 'buy' | 'sell', symbol: 'BTC', amount: 100)" }] };
    },
  });
}
