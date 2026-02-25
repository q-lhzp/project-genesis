// ---------------------------------------------------------------------------
// Before Prompt Build Hook - Phase 6-21
// ---------------------------------------------------------------------------

import { join } from "node:path";
import { promises as fs } from "node:fs";
import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import {
  readJson,
  writeJson,
  withFileLock,
  resolvePath
} from "../utils/persistence.js";
import {
  updateMetabolism,
  updateLifecycle,
  advanceCycleDay,
  detectAgentRole,
  cleanupExpiredMemos,
  logVitalityTelemetry,
} from "../simulation/index.js";
import {
  buildSensoryContext,
  queryMem0,
} from "../prompts/context-engine.js";
import { getInteractionContext } from "../simulation/prop_mapper.js";
import { getCurrentProject } from "../simulation/self_expansion_engine.js";
import type {
  Physique,
  LifecycleState,
  CycleState,
  CycleProfile,
  SocialState,
  FinanceState,
  ReputationState,
  SocialEvent,
  InternalComm,
  SkillState,
  PsychState,
  DreamState,
} from "../types/simulation.js";
import type { SimulationPaths, ToolModules } from "../types/paths.js";
import type { PluginConfig } from "../types/config.js";

// PromptBuildCtx interface (from OpenClaw SDK)
interface PromptBuildCtx {
  agent?: { id?: string; name?: string };
  agentId: string;
  agentName: string;
  workspace: string;
}

export function registerBeforePromptHook(
  api: OpenClawPluginApi, 
  paths: SimulationPaths, 
  cfg: Partial<PluginConfig> | undefined, 
  modules: ToolModules, 
  rates: any, 
  reflexThreshold: number, 
  ws: string, 
  lang: "de" | "en"
) {
  api.on("before_prompt_build", async (_event: unknown, ctx: unknown) => {
    const isDe = lang === "de";
    const promptCtx = ctx as PromptBuildCtx;
    const agentId = promptCtx?.agent?.id ?? promptCtx?.agent?.name ?? "persona";
    const roleMapping = cfg?.roleMapping;
    const agentRole = detectAgentRole(agentId, roleMapping);

    // Clean up expired memos (daily)
    const memoTTL = cfg?.memoTTL ?? 7;
    await cleanupExpiredMemos(paths.internalComm, memoTTL);

    // Initialize internal_comm.json if missing
    const internalComm = await readJson<InternalComm>(paths.internalComm);
    if (!internalComm) {
      await writeJson(paths.internalComm, { memos: [], last_cleanup: new Date().toISOString() });
    }

    const ph = await withFileLock(paths.physique, async () => {
      const p = await readJson<Physique>(paths.physique);
      return p;
    });
    if (!ph) return { prependContext: "" };

    // Ensure libido field exists on legacy physique data
    if (ph.needs.libido === undefined) ph.needs.libido = 0;

    // Load and advance cycle state (auto-init if missing)
    let cycleState: CycleState | null = null;
    if (modules.cycle) {
      cycleState = await withFileLock(paths.cycle, async () => {
        let cs = await readJson<CycleState>(paths.cycle);
        if (!cs) {
          cs = {
            cycle_length: 28,
            current_day: 1,
            start_date: new Date().toISOString(),
            last_advance: new Date().toISOString(),
            phase: "menstruation",
            hormones: { estrogen: 10, progesterone: 5, lh: 5, fsh: 10 },
            symptom_modifiers: {
              cramps: 0, bloating: 0, fatigue: 0, mood_swings: 0,
              headache: 0, breast_tenderness: 0, acne: 0, appetite_changes: 0,
              back_pain: 0, insomnia: 0
            },
            simulator: { active: false, simulated_day: 0, custom_modifiers: {} }
          };
          await writeJson(paths.cycle, cs);
        }
        const advanced = advanceCycleDay(cs);
        if (advanced) await writeJson(paths.cycle, cs);
        return cs;
      });
    }

    // Phase 1: Chronos - Load and advance lifecycle state (auto-init if missing)
    const birthDate = cfg?.birthDate;
    const initialAgeDays = cfg?.initialAgeDays ?? 0;
    let lifecycleState: LifecycleState | null = await withFileLock(paths.lifecycle, async () => {
      let ls = await readJson<LifecycleState>(paths.lifecycle);
      if (!ls) {
        ls = {
          birth_date: birthDate || new Date().toISOString(),
          biological_age_days: initialAgeDays,
          life_stage: "adult",
          last_aging_check: new Date().toISOString(),
          age_progression_enabled: true
        };
        await writeJson(paths.lifecycle, ls);
      } else {
        const advanced = updateLifecycle(ls);
        if (advanced) await writeJson(paths.lifecycle, ls);
      }
      return ls;
    });

    const changed = updateMetabolism(ph, rates, modules, cycleState, lifecycleState);
    if (changed) await withFileLock(paths.physique, () => writeJson(paths.physique, ph));

    // Phase 1: Chronos - Log vitality telemetry (every tick)
    if (lifecycleState) {
      await logVitalityTelemetry(paths.telemetry, lifecycleState, ph.needs, ph.current_location);
    }

    // Phase 8: Time Vault - Auto-Snapshot (once per day)
    const today = new Date().toISOString().slice(0, 10);
    const todayBackupDir = join(paths.backups, today);
    const snapshotMarker = join(todayBackupDir, ".snapshot_done");

    // Morning Market Report Logic
    const now = new Date();
    const hour = now.getHours();
    let marketReportDirective = "";
    if (hour >= 7 && hour <= 10) {
      const vaultState = await readJson<any>(paths.vaultState);
      const lastReport = vaultState?.last_report_date;
      if (lastReport !== today) {
        marketReportDirective = `
[MORNING MARKET REPORT] It's morning. Please check your portfolio in The Vault using reality_trade(action: "check") and write a brief analysis of your performance and strategy in your internal narrative. Then use reality_trade(action: "report", symbol: "DAILY", amount: 0, text: "...") to mark this task as done.`;
      }
    }

    try {
      const markerExists = await fs.access(snapshotMarker).then(() => true).catch(() => false);
      if (!markerExists) {
        await fs.mkdir(todayBackupDir, { recursive: true });
        const filesToBackup = [
          paths.physique, paths.lifecycle, paths.finances, paths.social,
          paths.skills, paths.psychology, paths.world, paths.interests,
          paths.identity, resolvePath(ws, "SOUL.md"),
          paths.emotions, paths.growth, paths.desires
        ];
        for (const file of filesToBackup) {
          try {
            const content = await fs.readFile(file, "utf-8");
            const fileName = file.split("/").pop() || "unknown";
            await fs.writeFile(join(todayBackupDir, fileName), content);
          } catch { /* ignore missing files */ }
        }
        await fs.writeFile(snapshotMarker, new Date().toISOString());
        api.logger.info(`[genesis] Daily snapshot created: ${today}`);
      }
    } catch (e) {
      api.logger.warn(`[genesis] Snapshot failed: ${e}`);
    }

    // Load states for role-specific contexts
    let socialState: SocialState | null = await readJson<SocialState>(paths.social);
    let financeState: FinanceState | null = await readJson<FinanceState>(paths.finances);

    // Phase 12: Autonomous Social Life - NPCs initiate interactions
    let activeSocialEvent: SocialEvent | null = null;
    if (modules.social && socialState && socialState.entities.length > 0) {
      const events = await readJson<{ pending: SocialEvent[] }>(paths.socialEvents);
      activeSocialEvent = events?.pending.find(e => !e.processed) || null;

      if (!activeSocialEvent && Math.random() < 0.15) {
        const entity = socialState.entities[Math.floor(Math.random() * socialState.entities.length)];
        const bond = entity.bond;
        let category: SocialEvent["category"] = "chat";
        let message = isDe ? `Lange nicht gesprochen, was gibts neues?` : `Long time no see, what's new?`;

        if (bond < -20) {
          category = "conflict";
          message = isDe ? `Hey, wir haben noch eine Rechnung offen.` : `Hey, we have some unfinished business.`;
        } else if (bond > 50) {
          category = Math.random() < 0.5 ? "support" : "request";
          message = category === "support" 
            ? (isDe ? `Ich dachte an dich, hoffe es geht dir gut!` : `Just thought of you, hope you're doing well!`)
            : (isDe ? `Kannst du mir bei einer Sache helfen?` : `Can you help me with something?`);
        }

        activeSocialEvent = {
          timestamp: new Date().toISOString(),
          sender_name: entity.name,
          sender_id: entity.id,
          message,
          category,
          processed: false
        };

        const allEvents = events || { pending: [] };
        allEvents.pending.push(activeSocialEvent);
        await writeJson(paths.socialEvents, allEvents);
      }
    }

    // Phase 10: Reputation - Auto-initialize if missing
    let reputationState: ReputationState | null = await withFileLock(paths.reputation, async () => {
      let rep = await readJson<ReputationState>(paths.reputation);
      if (!rep) {
        rep = { global_score: 0, circles: [
          { name: "Professional", score: 0 },
          { name: "Family", score: 0 },
          { name: "Friends", score: 0 },
          { name: "Public", score: 0 }
        ], events: [], last_propagation: new Date().toISOString() };
        await writeJson(paths.reputation, rep);
      }
      return rep;
    });

    // Load world news state
    const newsState = await readJson<{ headlines: any[] }>(paths.news);
    (globalThis as any)._newsState = newsState;

    const cycleProfile = await readJson<CycleProfile>(paths.cycleProfile);
    const emotionState = await fs.readFile(paths.emotions, "utf-8").catch(() => "");
    const desireState = await fs.readFile(paths.desires, "utf-8").catch(() => "");
    const identityLine = await fs.readFile(paths.identity, "utf-8").catch(() => "");
    const growthCtx = await fs.readFile(paths.growth, "utf-8").catch(() => "");
    const dreamState = await readJson<DreamState>(paths.dreamState);
    const hobbySuggestion = await fs.readFile(paths.hobbies, "utf-8").catch(() => "");
    const skillState = await readJson<SkillState>(paths.skills);
    const psychState = await readJson<PsychState>(paths.psychology);
    const dreamEnergyThreshold = cfg?.dreamEnergyThreshold ?? 20;

    const dreamTriggerHint = (modules.dreams && ph.needs.energy < dreamEnergyThreshold)
      ? `
[TRAUM-IMPULS] Deine Energie ist niedrig (${ph.needs.energy}%). Du koenntest schlafen gehen und im Traum deine Erlebnisse verarbeiten.`
      : "";

    // Phase 33: Load interaction context (props, furniture, light)
    const interactionContext = await getInteractionContext(ws);

    // Build default sensory context
    const defaultContext = buildSensoryContext(
      ph, lang, modules, cycleState, cycleProfile,
      emotionState, desireState, identityLine, growthCtx,
      dreamState, hobbySuggestion, lifecycleState, socialState, financeState,
      null, skillState, psychState, reputationState,
      activeSocialEvent
    ) + dreamTriggerHint + marketReportDirective;

    // Phase 33: Add interaction context if available
    const enrichedContext = interactionContext
      ? `\n[UMGEBUNG] ${interactionContext}`
      : "";

    // Phase 34: Add self-expansion context
    const currentProject = getCurrentProject();
    const selfDevContext = currentProject
      ? `\n[SELF-ENTWICKLUNG] Du arbeitest gerade an deinem Projekt: "${currentProject.name}" (${currentProject.progress}% abgeschlossen).`
      : "";

    // Role-specific context
    const roleContext = ""; // Simplified for now, can be expanded per role
    const memoContext = "";

    let finalContext: string;
    if (modules.multi_model_optimization) {
      if (agentRole === "persona") finalContext = roleContext + enrichedContext + selfDevContext;
      else if (agentRole === "limbic") finalContext = roleContext + memoContext + enrichedContext + selfDevContext;
      else if (agentRole === "world_engine") finalContext = roleContext;
      else if (agentRole === "analyst") finalContext = roleContext + defaultContext + memoContext + enrichedContext;
      else finalContext = roleContext + defaultContext + memoContext + enrichedContext;
    } else {
      finalContext = roleContext + defaultContext + memoContext + enrichedContext;
    }

    // Phase 18: Mem0 Long-Term Memory Integration
    if (modules.mem0?.enabled && (agentRole === "persona" || agentRole === "analyst")) {
      const mem0Query = `Location: ${ph.current_location}. Outfit: ${ph.current_outfit.join(", ")}. State: energy=${ph.needs.energy}, stress=${ph.needs.stress}.`;
      const mem0Config = { ...modules.mem0, userId: agentId };
      const memories = await queryMem0(mem0Query, mem0Config, 5);
      if (memories) {
        finalContext += `
[LONG-TERM MEMORY - from Mem0]
${memories}
`;
      }
    }

    return { prependContext: finalContext };
  });
}
