// ---------------------------------------------------------------------------
// Project Genesis v4.0.0 - Modular Entry Point
// ---------------------------------------------------------------------------

import { Type } from "@sinclair/typebox";
import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { promises as fs } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

// v4.0.0 Modular imports
import { readJson, writeJson, withFileLock, resolvePath, generateId, todayStr, generateExpId, appendJsonl } from "./src/utils/index.js";
import * as Simulation from "./src/simulation/index.js";
import * as Prompts from "./src/prompts/index.js";
import { registerBeforePromptHook, registerLlmOutputHook } from "./src/hooks/index.js";

// Tool registration functions
import { registerNeedsTools } from "./src/tools/needs.js";
import { registerSocialTools } from "./src/tools/social.js";
import { registerEconomyTools } from "./src/tools/economy.js";
import { registerIdentityTools } from "./src/tools/identity.js";
import { registerSystemTools } from "./src/tools/system.js";

// Types
import type { PluginConfig } from "./src/types/config.js";
import type { SimulationPaths, ToolModules } from "./src/types/paths.js";
import type { Physique, SkillState, Needs, LifecycleState, CycleState, WorldState, SocialState, FinanceState, DreamState, SkillState as SkillStateType, ReputationState } from "./src/types/index.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// ---------------------------------------------------------------------------
// Plugin Configuration Interface
// ---------------------------------------------------------------------------

// Note: Using SimulationPaths from src/types/paths.ts

// ---------------------------------------------------------------------------
// Plugin Export
// ---------------------------------------------------------------------------

export default {
  id: "project_genesis",
  name: "Project Genesis",

  register(api: OpenClawPluginApi) {
    // Synchronous registration
  },

  async activate(api: OpenClawPluginApi) {
    // ---------------------------------------------------------------------------
    // Configuration
    // ---------------------------------------------------------------------------
    const cfg = api.pluginConfig as Partial<PluginConfig> | undefined;
    const ws = cfg?.workspacePath ?? api.config?.agents?.list?.[0]?.workspace ?? ".";

    if (!cfg?.workspacePath && !api.config?.agents?.list?.[0]?.workspace) {
      api.logger.warn("[genesis] workspacePath not configured — using '.' (cwd).");
    }

    const lang = cfg?.language ?? "en";
    const modules: ToolModules = {
      eros: cfg?.modules?.eros ?? false,
      cycle: cfg?.modules?.cycle ?? false,
      dreams: cfg?.modules?.dreams ?? false,
      hobbies: cfg?.modules?.hobbies ?? false,
      utility: cfg?.modules?.utility ?? true,
      economy: cfg?.modules?.economy ?? true,
      social: cfg?.modules?.social ?? true,
      psychology: cfg?.modules?.psychology ?? true,
      skills: cfg?.modules?.skills ?? true,
      world: cfg?.modules?.world ?? true,
      reputation: cfg?.modules?.reputation ?? true,
      desktop: cfg?.modules?.desktop ?? false,
      legacy: cfg?.modules?.legacy ?? false,
      genesis: cfg?.modules?.genesis ?? false,
      multi_model_optimization: cfg?.modules?.multi_model_optimization ?? true,
      voice_enabled: cfg?.modules?.voice_enabled ?? false,
      mem0: {
        enabled: cfg?.modules?.mem0?.enabled ?? false,
        apiKey: cfg?.modules?.mem0?.api_key ?? "",
        userId: cfg?.modules?.mem0?.user_id ?? "genesis_agent",
      },
    };

    const rates = cfg?.metabolismRates ?? {};

    // ---------------------------------------------------------------------------
    // Paths
    // ---------------------------------------------------------------------------
    const paths: SimulationPaths = {
      physique: resolvePath(ws, "memory", "reality", "physique.json"),
      wardrobe: resolvePath(ws, "memory", "reality", "wardrobe.json"),
      locations: resolvePath(ws, "memory", "reality", "world.json"),
      interests: resolvePath(ws, "memory", "reality", "interests.json"),
      diary: resolvePath(ws, "memory", "reality", "diary"),
      experiences: resolvePath(ws, "memory", "experiences"),
      soulState: resolvePath(ws, "memory", "soul-state.json"),
      pendingProposals: resolvePath(ws, "memory", "proposals", "pending.jsonl"),
      interior: resolvePath(ws, "memory", "reality", "interior.json"),
      inventory: resolvePath(ws, "memory", "reality", "inventory.json"),
      media: resolvePath(ws, "memory", "reality", "media"),
      devManifest: resolvePath(ws, "memory", "development", "manifest.json"),
      devProjects: resolvePath(ws, "memory", "development", "projects"),
      cycle: resolvePath(ws, "memory", "reality", "cycle.json"),
      emotions: resolvePath(ws, "EMOTIONS.md"),
      growth: resolvePath(ws, "GROWTH.md"),
      desires: resolvePath(ws, "DESIRES.md"),
      identity: resolvePath(ws, "IDENTITY.md"),
      dreams: resolvePath(ws, "memory", "reality", "dreams.md"),
      dreamState: resolvePath(ws, "memory", "reality", "dream_state.json"),
      hobbies: resolvePath(ws, "memory", "reality", "hobbies.json"),
      cycleProfile: resolvePath(ws, "memory", "reality", "cycle_profile.json"),
      lifecycle: resolvePath(ws, "memory", "reality", "lifecycle.json"),
      telemetry: resolvePath(ws, "memory", "telemetry"),
      social: resolvePath(ws, "memory", "reality", "social.json"),
      socialTelemetry: resolvePath(ws, "memory", "telemetry", "social"),
      finances: resolvePath(ws, "memory", "reality", "finances.json"),
      economyTelemetry: resolvePath(ws, "memory", "telemetry", "economy"),
      skills: resolvePath(ws, "memory", "reality", "skills.json"),
      skillsConfig: join(__dirname, "skills", "soul-evolution", "skills.json"),
      reputation: resolvePath(ws, "memory", "reality", "reputation.json"),
      reputationEvents: resolvePath(ws, "memory", "telemetry", "reputation"),
      world: resolvePath(ws, "memory", "reality", "world.json"),
      worldNews: resolvePath(ws, "memory", "reality", "news.json"),
      psych: resolvePath(ws, "memory", "reality", "psych.json"),
      newsEvents: resolvePath(ws, "memory", "telemetry", "news"),
      socialEvents: resolvePath(ws, "memory", "reality", "social_events.json"),
      genesisLog: resolvePath(ws, "memory", "genesis_log.jsonl"),
      vaultState: resolvePath(ws, "memory", "vault", "state.json"),
    };

    // ---------------------------------------------------------------------------
    // Register Hooks & Tools (v4.0.0 Modular)
    // ---------------------------------------------------------------------------
    registerBeforePromptHook(api, paths, cfg, modules, rates, 95, ws, lang);
    registerLlmOutputHook(api, paths, modules);
    
    registerNeedsTools(api, paths, modules, lang);
    registerSocialTools(api, paths, modules);
    registerEconomyTools(api, paths, paths, modules, ws);
    registerIdentityTools(api, paths, ws);
    registerSystemTools(api, ws);

    // ---------------------------------------------------------------------------
    // Lifecycle Tick (periodic metabolism updates)
    // ---------------------------------------------------------------------------
    api.on("tick", async () => {
      try {
        const ph = await readJson<Physique>(paths.physique);
        if (!ph) return;

        const lifecycleState = modules.cycle || modules.dreams ? await readJson<LifecycleState>(paths.lifecycle) : null;
        const cycleState = modules.cycle ? await readJson<CycleState>(paths.cycle) : null;

        const updated = Simulation.updateMetabolism(ph, rates, { eros: modules.eros, cycle: modules.cycle }, cycleState, lifecycleState ?? undefined);
        if (updated) {
          await writeJson(paths.physique, ph);
        }
      } catch (e) {
        api.logger.error(`[genesis] tick error: ${e}`);
      }
    });

    // ---------------------------------------------------------------------------
    // Log startup
    // ---------------------------------------------------------------------------
    api.logger.info(`[genesis] v4.0.0 initialized: modular architecture active, workspace: ${ws}, lang: ${lang}`);
  },
};
