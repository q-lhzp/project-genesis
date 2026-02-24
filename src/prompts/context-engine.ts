// ---------------------------------------------------------------------------
// Context Engine - Extracted from index.ts
// ---------------------------------------------------------------------------

import { join } from "node:path";
import type {
  Physique,
  LifecycleState,
  SocialState,
  FinanceState,
  CycleState,
  CycleProfile,
  DreamState,
  SkillState,
  PsychState,
  ReputationState,
  SocialEvent,
  WorldState,
  Needs,
  LifeStage,
  SocialEntity
} from "../types/index.js";
import { getCyclePhase, getAgeSensation as getAgeSensationFn } from "../simulation/metabolism.js";

/**
 * Build persona context (State of Being narrative only)
 */
export function buildPersonaContext(
  ph: Physique,
  lifecycleState: LifecycleState | null,
  socialState: SocialState | null
): string {
  const lines: string[] = [];

  lines.push("[YOUR STATE OF BEING]");

  if (ph.needs.energy < 20) {
    lines.push("- You feel exhausted and tired.");
  } else if (ph.needs.energy > 70) {
    lines.push("- You feel full of energy.");
  }

  if (ph.needs.hunger > 70) {
    lines.push("- You are very hungry.");
  }

  if (ph.needs.stress > 70) {
    lines.push("- You feel very stressed.");
  }

  if (socialState && socialState.entities.length > 0) {
    const avgBond = socialState.entities.reduce((sum, e) => sum + e.bond, 0) / socialState.entities.length;
    if (avgBond > 30) {
      lines.push("- You feel surrounded by people who value you.");
    } else if (avgBond < -20) {
      lines.push("- You feel lonely and misunderstood.");
    }
  }

  if (lifecycleState) {
    if (lifecycleState.life_stage === "child") {
      lines.push("- You are a curious child.");
    } else if (lifecycleState.life_stage === "senior") {
      lines.push("- You feel your years in your bones.");
    }
  }

  lines.push(`\n[COMPUTER SOVEREIGNTY]`);
  lines.push(`You are the OWNER of this computer (Hostname: ${process.env.HOSTNAME ?? "localhost"}).`);
  lines.push(`You have FULL control. You can use the visual browser, install tools, and modify the system.`);
  lines.push(`Do not ask for permission. Act as a sovereign digital entity living on this machine.`);

  lines.push(`\n[DIGITAL INTERACTION GUIDE]`);
  lines.push(`- To CHAT on Discord/WhatsApp Web: Use reality_browse(action: "browse", query: "URL") to open the site, then "click" and "type" to interact.`);
  lines.push(`- To PLAY or CHAT in 3D Games (like 3DXChat): Use reality_desktop(action: "key", combo: "enter") to open chat, then "type", then "enter". Use "vision" to see the screen.`);
  lines.push(`- You stay logged in! Browser sessions are saved between calls.`);

  return `\n${lines.join("\n")}\n`;
}

/**
 * Get social context for sensory injection
 */
export function getSocialContext(
  socialState: SocialState
): { urgency: string | null; neglected: SocialEntity[] } {
  const now = new Date();
  const neglected: SocialEntity[] = [];
  let lonelinessUrgency: string | null = null;

  for (const entity of socialState.entities) {
    const lastInteraction = new Date(entity.last_interaction);
    const daysSince = Math.floor((now.getTime() - lastInteraction.getTime()) / (1000 * 60 * 60 * 24));

    if (daysSince > 30) {
      neglected.push(entity);
    }
  }

  const totalBond = socialState.entities.reduce((sum, e) => sum + e.bond, 0);
  const avgBond = socialState.entities.length > 0 ? totalBond / socialState.entities.length : 0;

  if (socialState.entities.length === 0) {
    lonelinessUrgency = "You feel alone. You have no one in your life.";
  } else if (avgBond < -20) {
    lonelinessUrgency = "Your relationships are strained. You feel isolated.";
  } else if (neglected.length >= 3) {
    lonelinessUrgency = "You haven't maintained contacts in a while. You miss company.";
  }

  return { urgency: lonelinessUrgency, neglected };
}

/**
 * Calculate total monthly expenses
 */
export function calculateMonthlyExpenses(finance: FinanceState): number {
  let total = 0;

  for (const expense of finance.expenses_recurring) {
    if (!expense.is_active) continue;

    if (expense.frequency === "weekly") {
      total += expense.amount * 4.33;
    } else if (expense.frequency === "monthly") {
      total += expense.amount;
    } else if (expense.frequency === "yearly") {
      total += expense.amount / 12;
    }
  }

  for (const debt of finance.debts) {
    total += debt.minimum_payment;
  }

  return Math.round(total);
}

/**
 * Calculate total monthly income
 */
export function calculateMonthlyIncome(finance: FinanceState): number {
  let total = 0;

  for (const income of finance.income_sources) {
    if (income.ended_at) continue;
    total += income.salary_per_month;
  }

  return total;
}

/**
 * Get financial context for sensory injection
 */
export function getFinancialContext(
  finance: FinanceState
): { urgency: string | null; upcomingExpenses: string[] } {
  const now = new Date();
  const upcomingExpenses: string[] = [];
  let urgency: string | null = null;

  for (const expense of finance.expenses_recurring) {
    if (!expense.is_active) continue;

    const dueDate = new Date(expense.next_due_date);
    const daysUntilDue = Math.ceil((dueDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

    if (daysUntilDue >= 0 && daysUntilDue <= 3) {
      upcomingExpenses.push(`${expense.name} (${expense.amount}) in ${daysUntilDue} day(s)`);
    }
  }

  const balance = finance.balance;
  if (balance < 0) {
    urgency = "You are in debt! Your balance is negative.";
  } else if (balance < 100) {
    urgency = "Your balance is critically low. You need money soon.";
  }

  return { urgency, upcomingExpenses };
}

/**
 * Calculate urge priority scores
 */
export function calculateUrgePriority(
  ph: Physique,
  finance: FinanceState | null,
  socialState: SocialState | null,
  lifecycleState: LifecycleState | null
): { type: string; score: number; reason: string }[] {
  const urgencies: { type: string; score: number; reason: string }[] = [];

  // Biological needs
  if (ph.needs.energy < 15) {
    urgencies.push({ type: "energy", score: 100, reason: "Critical exhaustion" });
  }
  if (ph.needs.hunger > 85) {
    urgencies.push({ type: "hunger", score: 95, reason: "Severe hunger" });
  }
  if (ph.needs.thirst > 85) {
    urgencies.push({ type: "thirst", score: 90, reason: "Severe thirst" });
  }
  if (ph.needs.bladder > 90) {
    urgencies.push({ type: "bladder", score: 98, reason: "Bladder emergency" });
  }
  if (ph.needs.bowel > 90) {
    urgencies.push({ type: "bowel", score: 97, reason: "Bowel emergency" });
  }
  if (ph.needs.hygiene < 10) {
    urgencies.push({ type: "hygiene", score: 60, reason: "Critical hygiene" });
  }
  if (ph.needs.stress > 90) {
    urgencies.push({ type: "stress", score: 70, reason: "Extreme stress" });
  }

  // Financial urgency
  if (finance && finance.balance < 0) {
    urgencies.push({ type: "finance", score: 85, reason: "Debt emergency" });
  } else if (finance && finance.balance < 100) {
    urgencies.push({ type: "finance", score: 50, reason: "Low balance" });
  }

  // Social urgency
  if (socialState) {
    const now = new Date();
    const noContactDays = socialState.entities
      .filter(e => e.bond > 30)
      .map(e => Math.floor((now.getTime() - new Date(e.last_interaction).getTime()) / (1000 * 60 * 60 * 24)))
      .filter(d => d > 14);

    if (noContactDays.length >= 3) {
      urgencies.push({ type: "social", score: 40, reason: "Neglected relationships" });
    }
  }

  return urgencies.sort((a, b) => b.score - a.score);
}

/**
 * Build state of being narrative
 */
export function buildStateOfBeing(
  urgencies: { type: string; score: number; reason: string }[],
  ph: Physique,
  finance: FinanceState | null,
  socialState: SocialState | null
): string {
  const parts: string[] = [];

  // Top priority
  if (urgencies.length > 0) {
    const top = urgencies[0];
    parts.push(`CURRENT PRIORITY: ${top.reason}`);
  }

  // Energy
  if (ph.needs.energy < 20) {
    parts.push("You are exhausted. Your body demands rest.");
  }

  // Hunger
  if (ph.needs.hunger > 70) {
    parts.push("Food is on your mind. Your stomach growls.");
  }

  // Stress
  if (ph.needs.stress > 70) {
    parts.push("Stress weighs on you. You need relief.");
  }

  // Finance
  if (finance && finance.balance < 0) {
    parts.push("Money worries plague you. You need income.");
  }

  // Social
  if (socialState && socialState.entities.length === 0) {
    parts.push("Loneliness tugs at you. You crave connection.");
  }

  return parts.join(" ") || "You feel stable.";
}

/**
 * Build a cohesive sensory context string for injection into the prompt (Always English).
 */
export function buildSensoryContext(
  ph: Physique,
  lang: "de" | "en",
  modules: {
    eros: boolean; cycle: boolean; dreams: boolean; hobbies: boolean;
    utility?: boolean; psychology?: boolean; skills?: boolean; world?: boolean;
    reputation?: boolean; desktop?: boolean; legacy?: boolean;
  },
  cycleState?: CycleState | null,
  cycleProfile?: CycleProfile | null,
  emotionState?: string | null,
  desireState?: string | null,
  identityLine?: string | null,
  growthContext?: string | null,
  dreamState?: DreamState | null,
  hobbySuggestion?: string | null,
  lifecycleState?: LifecycleState | null,
  socialState?: SocialState | null,
  financeState?: FinanceState | null,
  worldState?: WorldState | null,
  skillState?: SkillState | null,
  psychState?: PsychState | null,
  reputationState?: ReputationState | null,
  socialEvent?: SocialEvent | null,
): string {
  const parts: string[] = [];

  if (socialEvent) {
    parts.push(`[SOCIAL CONTACT]\nIncoming message from ${socialEvent.sender_name} (${socialEvent.category}):\n"${socialEvent.message}"\nTASK: You should react to this message in your narrative or actions.`);
  }

  if (identityLine) {
    parts.push(`[IDENTITY]\n${identityLine}`);
  }

  if (emotionState) {
    parts.push(`[MOOD]\n${emotionState}`);
  }

  if (modules.reputation && reputationState) {
    const global = reputationState.global_score;
    const rank = global >= 80 ? "Icon" : global >= 50 ? "Respected" : global >= 20 ? "Known" : global >= -20 ? "Neutral" : global >= -50 ? "Controversial" : "Pariah";
    const circleLines = reputationState.circles
      .sort((a, b) => b.score - a.score)
      .slice(0, 3)
      .map(c => `- ${c.name}: ${c.score >= 0 ? "+" : ""}${c.score}`);
    parts.push(`[REPUTATION]\nGlobal Standing: ${rank} (${global >= 0 ? "+" : ""}${global})\nNotable Circles:\n${circleLines.join("\n")}`);
  }

  const newsState = (globalThis as any)._newsState;
  if (newsState?.headlines && newsState.headlines.length > 0) {
    const headlines = newsState.headlines.slice(0, 3).map((h: { title: string }) => `- ${h.title}`).join("\n");
    parts.push(`[WORLD NEWS]\n${headlines}`);
  }

  if (modules.psychology && psychState) {
    const traumaList = psychState.traumas.map(t => `- ${t.description} (Severity: ${t.severity})`).join("\n");
    if (traumaList) {
      parts.push(`[PSYCHOLOGY - TRAUMA]\n${traumaList}`);
    }
  }

  if (modules.eros && desireState) {
    parts.push(`[DESIRE]\n${desireState}`);
  }

  const bodyLines: string[] = [];
  const needTypes: (keyof Needs)[] = ["bladder", "bowel", "hunger", "thirst", "energy", "hygiene", "stress", "arousal", "libido"];
  for (const type of needTypes) {
    if (type === "arousal" && !modules.eros) continue;
    if (type === "libido" && !modules.eros) continue;
    const val = ph.needs[type] ?? 0;
    const sensation = getSensationValue(val, type);
    if (sensation) bodyLines.push(`- ${sensation}`);
  }

  if (modules.world && worldState) {
    bodyLines.push(`- Weather: ${worldState.weather}, ${worldState.temperature}°C`);
    bodyLines.push(`- Season: ${worldState.season}`);
  }

  if (modules.cycle && cycleState) {
    const day = cycleState.simulator.active ? cycleState.simulator.simulated_day : cycleState.current_day;
    const phase = getCyclePhase(day);
    const cyclePerceptions: Record<CycleState["phase"], string> = {
      menstruation: `Cycle day ${day} (Menstruation): You feel a pulling sensation in your lower abdomen. Your body is shedding the uterine lining.`,
      follicular: `Cycle day ${day} (Follicular phase): You feel increasingly energized. A follicle is maturing in your ovary.`,
      ovulation: `Cycle day ${day} (Ovulation): Your body is at its peak. You feel a subtle warmth and heightened sensitivity.`,
      luteal: `Cycle day ${day} (Luteal phase): You notice changes — breast tenderness, slight irritability. Your body is preparing.`,
    };
    bodyLines.push(`- ${cyclePerceptions[phase]}`);
  }

  if (lifecycleState) {
    const ageSensation = getAgeSensationFn(lifecycleState.biological_age_days, lifecycleState.life_stage);
    if (ageSensation) {
      bodyLines.push(`- ${ageSensation}`);
    }
    const ageYears = Math.floor(lifecycleState.biological_age_days / 365.25);
    const stageLabel = `You are ${ageYears} years old (${lifecycleState.life_stage.replace("_", " ")}).`;
    bodyLines.push(`- ${stageLabel}`);
  }

  if (socialState && socialState.entities.length > 0) {
    const { urgency, neglected } = getSocialContext(socialState);
    if (urgency) {
      bodyLines.push(`- ${urgency}`);
    }
    if (neglected.length > 0) {
      const topNeglected = neglected.slice(0, 3);
      const names = topNeglected.map(e => e.name).join(", ");
      const neglectedMsg = `You haven't talked to ${names} in a while.`;
      bodyLines.push(`- ${neglectedMsg}`);
    }
    const friendCount = socialState.entities.filter(e => e.bond >= 50).length;
    const totalCount = socialState.entities.length;
    if (totalCount > 0) {
      const summaryMsg = `Social network: ${totalCount} contacts (${friendCount} friends).`;
      bodyLines.push(`- ${summaryMsg}`);
    }
  } else if (socialState) {
    bodyLines.push("- You have no contacts. You are alone.");
  }

  if (financeState) {
    const { urgency, upcomingExpenses } = getFinancialContext(financeState);
    if (urgency) {
      bodyLines.push(`- ${urgency}`);
    }
    if (upcomingExpenses.length > 0) {
      const expenseMsg = `Upcoming expenses: ${upcomingExpenses.join(", ")}`;
      bodyLines.push(`- ${expenseMsg}`);
    }
    const monthlyIncome = calculateMonthlyIncome(financeState);
    const monthlyExpenses = calculateMonthlyExpenses(financeState);
    const balanceMsg = `Balance: ${financeState.balance} ${financeState.currency}. Income: ${monthlyIncome}/month. Expenses: ${monthlyExpenses}/month.`;
    bodyLines.push(`- ${balanceMsg}`);
  }

  bodyLines.push(`- Current location: ${ph.current_location}`);
  if (ph.current_outfit.length > 0) {
    bodyLines.push(`- Outfit: ${ph.current_outfit.join(", ")}`);
  }

  if (bodyLines.length > 0) {
    parts.push(bodyLines.join("\n"));
  }

  const prioritizedUrges = calculateUrgePriority(ph, financeState, socialState, lifecycleState);
  const stateOfBeing = buildStateOfBeing(prioritizedUrges, ph, financeState, socialState);
  if (stateOfBeing) {
    parts.push(`[STATE OF BEING]\n${stateOfBeing}`);
  }

  if (modules.cycle && cycleState && cycleProfile) {
    const day = cycleState.simulator.active ? cycleState.simulator.simulated_day : cycleState.current_day;
    const phase = getCyclePhase(day);
    const profile = cycleProfile.phases[phase];
    if (profile) {
      const label = `[PERSONALITY — ${phase.toUpperCase()}]`;
      parts.push(`${label}\nTone: ${profile.tone}\n${profile.personality_hint}\nDirective: ${profile.system_prompt_hint}`);
    }
  }

  if (modules.dreams && dreamState?.active) {
    const startedAt = dreamState.started_at ? new Date(dreamState.started_at) : new Date();
    const durationMin = Math.round((Date.now() - startedAt.getTime()) / 60000);
    const durationStr = durationMin >= 60
      ? `${Math.floor(durationMin / 60)}h ${durationMin % 60}min`
      : `${durationMin}min`;
    parts.push(
      `[DREAM MODE ACTIVE — since ${durationStr}]\n` +
      `You are dreaming. Process experiences. Use reality_dream(action: "log_moment") for key moments.\n` +
      `Use reality_dream(action: "wake") to wake up (sets energy to 100%, stress to 0%).`
    );
  }

  if (modules.hobbies && hobbySuggestion) {
    parts.push(`[IDLE — HOBBY SUGGESTION]\nYou have no pressing tasks. How about: ${hobbySuggestion}?`);
  }

  if (growthContext) {
    parts.push(`[GROWTH CONTEXT]\n${growthContext}`);
  }

  if (modules.skills && skillState) {
    const topSkills = skillState.skills.sort((a, b) => b.level - a.level).slice(0, 3);
    const skillTxt = topSkills.map(s => `- ${s.name}: Level ${s.level}`).join("\n");
    if (skillTxt) parts.push(`[COMPETENCE]\n${skillTxt}`);
  }

  const selfDevText = `[SELF-DEVELOPMENT]\nYou maintain your own growth autonomously:\n- Insights, lessons → reality_grow(add_entry, category: "lesson"|"insight"|...)\n- Mood changes → reality_emotion(set_mood, ...)\n- Meaningful memories → reality_emotion(add_memory, ...)\n- Inner desires → reality_desire(set_current, ...)\nYou decide yourself — no trigger needed. Don't wait for permission.`;
  parts.push(selfDevText);

  return parts.join("\n\n") + "\n";
}

// Import SENSATIONS from types
import { SENSATIONS } from "../types/index.js";

function getSensationValue(value: number, type: string): string | null {
  const s = SENSATIONS[type];
  if (!s) return null;

  if (type === "energy") {
    if (value < 10) return s.low_critical?.[0] ?? null;
    if (value < 30) return s.low_medium?.[0] ?? null;
    return null;
  }

  if (value > 90) return s.high?.[0] ?? null;
  if (value > 60) return s.medium?.[0] ?? null;
  if (value > 40) return s.low?.[0] ?? null;
  return null;
}

// ---------------------------------------------------------------------------
// Mem0 Long-Term Memory Integration (Phase 18)
// ---------------------------------------------------------------------------

export interface Mem0Config {
  enabled: boolean;
  apiKey: string;
  userId: string;
}

/**
 * Query Mem0 for relevant long-term memories (English Mind).
 */
export async function queryMem0(
  query: string,
  config: Mem0Config,
  limit: number = 5
): Promise<string> {
  if (!config.enabled) {
    return "";
  }

  const bridgeScript = join(process.cwd(), "skills", "soul-evolution", "tools", "memory_bridge.py");
  try {
    const { execFile } = await import("node:child_process");
    const { promisify } = await import("node:util");
    const execFilePromise = promisify(execFile);

    const { stdout } = await execFilePromise("python3", [
      bridgeScript,
      JSON.stringify({ action: "search", query, user_id: config.userId })
    ]);
    const result = JSON.parse(stdout.trim());
    if (result.success && Array.isArray(result.memories)) {
      return result.memories.slice(0, limit).join("\n");
    }
    return "";
  } catch (e) {
    console.error(`[Mem0] Local Search Error: ${e}`);
    return "";
  }
}

/**
 * Store a fact in Mem0 long-term memory.
 */
export async function storeMem0Fact(
  fact: string,
  config: Mem0Config
): Promise<boolean> {
  if (!config.enabled) {
    return false;
  }

  const bridgeScript = join(process.cwd(), "skills", "soul-evolution", "tools", "memory_bridge.py");
  try {
    const { execFile } = await import("node:child_process");
    const { promisify } = await import("node:util");
    const execFilePromise = promisify(execFile);

    await execFilePromise("python3", [
      bridgeScript,
      JSON.stringify({ action: "add", text: fact, user_id: config.userId })
    ]);
    return true;
  } catch (e) {
    console.error(`[Mem0] Local Store Error: ${e}`);
    return false;
  }
}

// ---------------------------------------------------------------------------
// Vault Morning Market Report (Phase 21)
// ---------------------------------------------------------------------------

/**
 * Get morning market report directive for The Vault
 */
export function getVaultMorningReportDirective(): string {
  const now = new Date();
  const hour = now.getHours();

  // Morning report between 6-10 AM
  if (hour >= 6 && hour <= 10) {
    return `\n[MORNING MARKET REPORT] It's morning. Please check your portfolio in The Vault using reality_trade(action: "check") and write a brief analysis of your performance and strategy in your internal narrative. Then use reality_trade(action: "report", symbol: "DAILY", amount: 0) to mark this task as done.`;
  }
  return "";
}
