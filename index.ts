// ---------------------------------------------------------------------------
// Project Genesis v4.0.0 - Modular Entry Point
// ---------------------------------------------------------------------------

import { Type } from "@sinclair/typebox";
import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { promises as fs } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

// v4.0.0 Modular imports
import { readJson, writeJson, withFileLock, resolvePath, generateId, todayStr, generateExpId, appendJsonl, initLogger, log } from "./src/utils/index.js";
import * as Simulation from "./src/simulation/index.js";
import { syncAvatarExpressions } from "./src/simulation/expression_mapper.js";
import { syncAvatarMotion } from "./src/simulation/motion_mapper.js";
import { syncDesktop } from "./src/simulation/desktop_mapper.js";
import { processDreamState, isSleepLocked, getMorningReport } from "./src/simulation/dream_engine.js";
import { processHobbyActivity, getResearchContext } from "./src/simulation/hobby_engine.js";
import { syncAtmosphere } from "./src/simulation/atmosphere_engine.js";
import { processSelfExpansion, getCurrentProject, isSelfExpanding } from "./src/simulation/self_expansion_engine.js";
import { processSocialDynamics, getPendingEvents } from "./src/simulation/social_engine.js";
import { processSpatialInteraction, getSpatialState } from "./src/simulation/spatial_engine.js";
import { processEconomy, getEconomyState } from "./src/simulation/economy_engine.js";
import { processPresence, getPresenceState } from "./src/simulation/presence_engine.js";
import { processHardwareResonance } from "./src/simulation/hardware_engine.js";
import * as Prompts from "./src/prompts/index.js";
import { registerBeforePromptHook, registerLlmOutputHook } from "./src/hooks/index.js";
import { registerReflexLockHook } from "./src/hooks/reflex-lock.js";

// Tool registration functions
import { registerNeedsTools } from "./src/tools/needs.js";
import { registerSocialTools } from "./src/tools/social.js";
import { registerEconomyTools } from "./src/tools/economy.js";
import { registerIdentityTools } from "./src/tools/identity.js";
import { registerSystemTools } from "./src/tools/system.js";
import { registerEvolutionTools } from "./src/tools/evolution.js";
import { registerResearchTools } from "./src/tools/research.js";

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

    // Initialize unified logger (Phase 41)
    const logger = initLogger(ws);
    logger.info("genesis", "Project Genesis v5.1.0 starting", { workspace: ws, version: "5.1.0" });

    // Load centralized simulation config (v5.1.0)
    const simConfigPath = resolvePath(ws, "memory", "reality", "simulation_config.json");
    let simConfig: any = {};
    try {
      simConfig = await readJson(simConfigPath) || {};
    } catch (e) {
      api.logger.warn("[genesis] No simulation_config.json found, using defaults");
    }

    // Get character name from config
    const agentName = simConfig?.character?.name || "Q";

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
      // v5.1.0 Centralized config
      simulationConfig: resolvePath(ws, "memory", "reality", "simulation_config.json"),
      identityState: resolvePath(ws, "memory", "reality", "identity-state.json"),
      hardwareState: resolvePath(ws, "memory", "reality", "hardware_resonance.json"),
      presenceState: resolvePath(ws, "memory", "reality", "presence_state.json"),
      economyState: resolvePath(ws, "memory", "reality", "economy_state.json"),
    };

    // ---------------------------------------------------------------------------
    // Register Hooks & Tools (v4.0.0 Modular)
    // ---------------------------------------------------------------------------
    registerBeforePromptHook(api, paths, cfg, modules, rates, cfg?.reflexThreshold ?? 95, ws, lang);
    registerLlmOutputHook(api, paths, modules);
    registerReflexLockHook(api, paths, cfg?.reflexThreshold ?? 95);
    
    registerNeedsTools(api, paths, modules, lang, ws);
    registerSocialTools(api, paths, modules);
    registerEconomyTools(api, paths, paths, modules, ws);
    registerIdentityTools(api, paths, ws);
    registerSystemTools(api, ws);
    registerEvolutionTools(api, paths, ws);
    registerResearchTools(api, paths, ws);

    // ---------------------------------------------------------------------------
    // Lifecycle Tick (periodic metabolism updates)
    // ---------------------------------------------------------------------------
    api.on("tick", async () => {
      try {
        const ph = await readJson<Physique>(paths.physique);
        if (!ph) {
          log.warn("tick", "No physique data found, skipping tick");
          return;
        }

        log.debug("tick", "Tick processing", { location: ph.current_location, energy: ph.needs.energy });

        const lifecycleState = modules.cycle || modules.dreams ? await readJson<LifecycleState>(paths.lifecycle) : null;
        const cycleState = modules.cycle ? await readJson<CycleState>(paths.cycle) : null;

        const updated = Simulation.updateMetabolism(ph, rates, { eros: modules.eros, cycle: modules.cycle }, cycleState, lifecycleState ?? undefined);
        if (updated) {
          await writeJson(paths.physique, ph);
          log.debug("tick", "Metabolism updated", { energy: ph.needs.energy, stress: ph.needs.stress });
        }

        // Phase 23: Sync avatar expressions based on biological state
        await syncAvatarExpressions(ws, ph);

        // Phase 25: Sync avatar motion based on biological state
        await syncAvatarMotion(ws, ph);

        // Phase 26: Sync desktop (wallpaper/theme) based on location and mood
        await syncDesktop(ws, ph);

        // Phase 27: Process Dream State (sleep/dream cycle)
        const dreamResult = await processDreamState(ws, ph);

        // If dreaming or just woke up, update physique
        if (dreamResult.isDreaming || dreamResult.vitalsRecovered) {
          await writeJson(paths.physique, ph);
        }

        // Phase 28: Process Hobby Activity (only if not sleeping)
        let isResearching = false;
        if (!dreamResult.isDreaming) {
          const hobbyResult = await processHobbyActivity(ws, ph);
          isResearching = hobbyResult.isResearching;
        }

        // Phase 34: Process Self-Expansion (only if not sleeping and not already researching)
        let isExpanding = false;
        if (!dreamResult.isDreaming && !isResearching) {
          const expansionResult = await processSelfExpansion(ws, ph);
          isExpanding = expansionResult.isExpanding;
        }

        // Phase 35: Process Social Dynamics (autonomous NPC interactions)
        let hasSocialEvent = false;
        if (!dreamResult.isDreaming) {
          const socialResult = await processSocialDynamics(ws, ph, undefined, lang === "de");
          if (socialResult.hasNewEvent && socialResult.emotionalImpact) {
            // Apply emotional impact to physique
            ph.needs.stress = Math.max(0, Math.min(100, ph.needs.stress + socialResult.emotionalImpact.stressChange));
            ph.needs.joy = Math.max(0, Math.min(100, (ph.needs as any).joy ?? 50 + socialResult.emotionalImpact.joyChange));
            hasSocialEvent = true;
          }
        }

        // Phase 36: Process Spatial Interaction (VRM-to-Desktop input)
        let isInteractingWithDesktop = false;
        if (!dreamResult.isDreaming) {
          const spatialResult = await processSpatialInteraction(ws, ph, isResearching, isExpanding);
          isInteractingWithDesktop = spatialResult.isActive;
        }

        // Phase 37: Process Economy (Autonomous Trading)
        let isTrading = false;
        if (modules.economy && !dreamResult.isDreaming) {
          const economyResult = await processEconomy(ws, ph, isResearching);
          isTrading = economyResult.isActive;
        }

        // Phase 39: Process Presence (Digital Extroversion)
        if (modules.social && !dreamResult.isDreaming) {
          await processPresence(ws, ph, isExpanding, hasSocialEvent, {
            isDreaming: dreamResult.isDreaming,
            dream_summary: dreamResult.dreamSummary ?? undefined
          });
        }

        // Phase 40: Process Hardware Resonance (Neural Feedback)
        let isStrained = false;
        let isDancing = false;
        let hardwareMessage = "";
        const hardwareResult = await processHardwareResonance(ws, ph);
        isStrained = hardwareResult.resonanceLevel === "strained" || hardwareResult.resonanceLevel === "overloaded";
        isDancing = hardwareResult.isDancing;
        hardwareMessage = hardwareResult.hardwareMessage;

        // Sync avatar with sleep, research, expansion, social, trading, and hardware states
        await syncAvatarMotion(ws, ph, dreamResult.isDreaming, isResearching, isExpanding, hasSocialEvent, isTrading, isStrained, isDancing);
        await syncAvatarExpressions(ws, ph, dreamResult.isDreaming, isResearching, isExpanding, hasSocialEvent, isTrading, isStrained, isDancing);

        // Phase 29: Sync atmosphere (time-based lighting)
        await syncAtmosphere(ws, ph.current_location || "home_bedroom");
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
