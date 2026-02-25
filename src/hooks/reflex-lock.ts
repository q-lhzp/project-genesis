// Reflex-Lock Hook - Blockiert Tools wenn kritische Bedürfnisse erreicht sind
import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { readJson } from "../utils/index.js";
import { join } from "node:path";
import * as fs from "fs";
import type { SimulationPaths } from "../types/paths.js";

interface Needs {
  energy: number;
  hunger: number;
  thirst: number;
  bladder: number;
  bowel: number;
  hygiene: number;
  stress: number;
  arousal: number;
  libido?: number;
}

interface Physique {
  needs: Needs;
  current_location?: string;
  current_outfit?: string[];
}

export function registerReflexLockHook(
  api: OpenClawPluginApi,
  paths: SimulationPaths,
  reflexThreshold: number = 95
) {
  api.on("before_tool_call", async (event: unknown, ctx: unknown) => {
    try {
      // Type casting for OpenClaw context
      const context = ctx as {
        toolName: string;
        sessionId?: string;
        agentId?: string;
      };

      const toolName = context.toolName;

      // Always allow reality_needs - prevents deadlock
      if (toolName.startsWith("reality_needs")) {
        return;
      }

      // Always allow genesis tools
      if (toolName.startsWith("reality_genesis") || toolName.startsWith("genesis")) {
        return;
      }

      // Allow debug/utility tools
      if (toolName === "evolution_debug" || toolName === "debug") {
        return;
      }

      // Read current physique
      let physique: Physique | null = null;
      try {
        physique = await readJson<Physique>(paths.physique);
      } catch (e) {
        // No physique yet - allow all
        return;
      }

      if (!physique || !physique.needs) {
        return;
      }

      // Check for critical needs
      const criticalNeeds: string[] = [];
      const needs = physique.needs;

      if (needs.energy >= reflexThreshold) criticalNeeds.push("energy");
      if (needs.hunger >= reflexThreshold) criticalNeeds.push("hunger");
      if (needs.thirst >= reflexThreshold) criticalNeeds.push("thirst");
      if (needs.bladder >= reflexThreshold) criticalNeeds.push("bladder");
      if (needs.bowel >= reflexThreshold) criticalNeeds.push("bowel");
      if (needs.hygiene >= reflexThreshold) criticalNeeds.push("hygiene");
      if (needs.stress >= reflexThreshold) criticalNeeds.push("stress");
      if (needs.arousal >= reflexThreshold) criticalNeeds.push("arousal");
      if ((needs.libido ?? 0) >= reflexThreshold) criticalNeeds.push("libido");

      if (criticalNeeds.length > 0) {
        const message = `⚠️ BIOLOGISCHER NOTFALL: ${criticalNeeds.join(", ")} hat Priorität.`;
        const advice = `Nutze zuerst 'reality_needs' um diese Bedürfnisse zu befriedigen.`;

        api.logger.warn(`[reflex-lock] Blocked ${toolName} - critical needs: ${criticalNeeds.join(", ")}`);

        return {
          block: true,
          blockReason: `${message}\n${advice}\n\nAktuelle Werte: ${JSON.stringify(needs, null, 2)}`
        };
      }

      return;
    } catch (e) {
      api.logger.error(`[reflex-lock] Error: ${e}`);
      // On error, allow the call
      return;
    }
  });

  api.logger.info(`[reflex-lock] Hook registered (threshold: ${reflexThreshold})`);
}
