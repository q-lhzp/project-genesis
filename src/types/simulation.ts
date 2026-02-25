// ---------------------------------------------------------------------------
// Core Simulation Types - Extracted from index.ts
// ---------------------------------------------------------------------------

// Needs & Physique
export interface Needs {
  energy: number;
  hunger: number;
  thirst: number;
  hygiene: number;
  bladder: number;
  bowel: number;
  stress: number;
  arousal: number;
  libido: number;
  joy?: number;
}

export interface Appearance {
  hair: string;
  eyes: string;
  modifications: string[];
}

export interface Physique {
  current_location: string;
  current_outfit: string[];
  needs: Needs;
  last_tick: string;
  appearance: Appearance;
}

// Lifecycle & Aging
export type LifeStage = "infant" | "child" | "teen" | "adult" | "middle_adult" | "senior";

export interface LifecycleState {
  birth_date: string;
  biological_age_days: number;
  life_stage: LifeStage;
  last_aging_check: string;
  age_progression_enabled: boolean;
}

export interface VitalityMetrics {
  timestamp: string;
  age_days: number;
  age_years: number;
  life_stage: LifeStage;
  health_index: number;
  energy: number;
  hunger: number;
  thirst: number;
  stress: number;
  location: string;
}

export interface TelemetryEntry {
  timestamp: string;
  age_days: number;
  age_years: number;
  life_stage: LifeStage;
  health_index: number;
  energy: number;
  hunger: number;
  thirst: number;
  stress: number;
  hygiene: number;
  bladder: number;
  bowel: number;
  location: string;
}

export interface LifeStageMultipliers {
  energy: number;
  hunger: number;
  thirst: number;
  hygiene: number;
  stress: number;
  bladder: number;
  bowel: number;
  arousal?: number;
  libido?: number;
}

// World & Environment
export interface WorldLocation {
  id: string;
  name: string;
  description: string;
}

export interface WorldState {
  weather: "sunny" | "cloudy" | "rainy" | "stormy" | "snowy";
  temperature: number;
  season: "spring" | "summer" | "autumn" | "winter";
  market_modifier: number;
  last_update: string;
  sync_to_real_world: boolean;
}

// Skills
export interface SkillEntry {
  id: string;
  name: string;
  level: number;
  xp: number;
  xp_to_next: number;
  last_trained: string | null;
}

export interface SkillState {
  skills: SkillEntry[];
  total_xp: number;
}

// Psychology
export interface Trauma {
  id: string;
  description: string;
  severity: number;
  trigger: string;
  decay_rate: number;
  added_at: string;
}

export interface PsychState {
  resilience: number;
  traumas: Trauma[];
  phobias: string[];
  joys: string[];
}

// Reputation
export interface ReputationEvent {
  timestamp: string;
  circle: string;
  change: number;
  reason: string;
}

export interface ReputationState {
  global_score: number;
  circles: { name: string; score: number }[];
  events: ReputationEvent[];
  last_propagation: string | null;
}

// Social
export type RelationshipType = "family" | "friend" | "romantic" | "professional" | "acquaintance" | "stranger";

export interface SocialEntity {
  id: string;
  name: string;
  relationship_type: RelationshipType;
  bond: number;
  trust: number;
  intimacy: number;
  last_interaction: string;
  interaction_count: number;
  history_summary: string;
  introduced_at: string;
  notes: string;
  circle?: string;
  visual_description?: string;
  portrait_url?: string;
  is_external?: boolean;
}

export interface SocialState {
  entities: SocialEntity[];
  last_network_search: string | null;
  circles: string[];
  last_decay_check?: string;
}

export interface SocialEvent {
  timestamp: string;
  sender_name: string;
  sender_id: string;
  message: string;
  category: "chat" | "request" | "conflict" | "support";
  processed: boolean;
}

export interface SocialInteractionLog {
  id: string;
  timestamp: string;
  entity_id: string;
  entity_name: string;
  action: "talk" | "gift" | "conflict" | "apologize" | "support" | "ignore";
  bond_change: number;
  trust_change: number;
  intimacy_change: number;
  context: string;
}

// Economy
export type JobType = "full_time" | "part_time" | "freelance" | "contract";

export interface IncomeSource {
  id: string;
  source_name: string;
  job_type: JobType;
  position: string;
  employer_id: string | null;
  salary_per_month: number;
  salary_per_hour: number | null;
  hours_per_week: number | null;
  started_at: string;
  ended_at: string | null;
}

export interface RecurringExpense {
  id: string;
  name: string;
  amount: number;
  frequency: "weekly" | "monthly" | "yearly";
  category: "rent" | "utilities" | "insurance" | "subscription" | "loan" | "other";
  next_due_date: string;
  is_active: boolean;
}

export interface Debt {
  id: string;
  name: string;
  principal: number;
  current_balance: number;
  interest_rate_annual: number;
  minimum_payment: number;
  due_date: string;
  creditor: string;
}

export interface FinanceState {
  balance: number;
  currency: string;
  income_sources: IncomeSource[];
  expenses_recurring: RecurringExpense[];
  debts: Debt[];
  last_expense_process: string;
  last_income_process: string;
  last_interest_process?: string;
  net_worth: number;
}

export interface EconomyEvent {
  id: string;
  timestamp: string;
  event_type: "income" | "expense" | "debt_payment" | "debt_incurred" | "job_started" | "job_ended" | "crisis";
  amount: number;
  description: string;
  related_entity_id: string | null;
}

// Interior & Inventory
export interface InteriorObject {
  id: string;
  name: string;
  category: string;
  description: string;
  located_on?: string;
  items_on?: string[];
  images: string[];
  added_at: string;
}

export interface InteriorRoom {
  id: string;
  name: string;
  description: string;
  objects: InteriorObject[];
}

export interface Interior {
  rooms: InteriorRoom[];
}

export interface InventoryItem {
  id: string;
  name: string;
  category: string;
  description: string;
  quantity: number;
  location?: string;
  images: string[];
  tags: string[];
  added_at: string;
  effects?: {
    energy?: number;
    stress?: number;
    hunger?: number;
    health?: number;
    mood?: string;
    duration_minutes?: number;
  };
  equippable?: boolean;
  equipped?: boolean;
}

export interface Inventory {
  items: InventoryItem[];
  categories: string[];
}

export interface WardrobeItem {
  id: string;
  name: string;
  images: string[];
}

// Development
export interface DevTestResult {
  timestamp: string;
  status: "pass" | "fail" | "error";
  message: string;
  details?: string;
}

export interface DevProject {
  id: string;
  name: string;
  type: "tool" | "skill" | "plugin" | "script";
  status: "draft" | "pending_review" | "approved" | "active";
  description: string;
  files: string[];
  created_at: string;
  approved: boolean;
  approved_at: string | null;
  review_feedback?: string;
  reviewed_by?: string;
  test_results?: DevTestResult[];
  last_test_run?: string;
  auto_load?: boolean;
}

export interface DevManifest {
  projects: DevProject[];
}

// Experience & Dreams
export interface ExperienceEntry {
  id: string;
  timestamp: string;
  source: string;
  content: string;
  significance: "routine" | "notable" | "pivotal";
  significance_reason: string;
  reflected: boolean;
  somatic_context?: Partial<Needs>;
}

export interface DreamMoment {
  timestamp: string;
  text: string;
}

export interface DreamState {
  active: boolean;
  started_at: string | null;
  moments: DreamMoment[];
}

export interface HobbySession {
  id: string;
  started_at: string;
  ended_at: string | null;
  duration_minutes: number | null;
  notes: string;
  mood_before: string;
  mood_after: string;
}

export interface HobbyEntry {
  id: string;
  name: string;
  category: string;
  description: string;
  added_at: string;
  last_pursued: string | null;
  total_sessions: number;
  total_minutes: number;
  current_session: HobbySession | null;
  log: HobbySession[];
}

export interface HobbyLog {
  hobbies: HobbyEntry[];
}

// Interests
export interface Interests {
  hobbies: string[];
  likes: string[];
  wishes: string[];
}

// Cycle (Menstrual)
export interface CycleState {
  cycle_length: number;
  current_day: number;
  start_date: string;
  last_advance: string;
  phase: "menstruation" | "follicular" | "ovulation" | "luteal";
  hormones: { estrogen: number; progesterone: number; lh: number; fsh: number };
  symptom_modifiers: {
    cramps: number; bloating: number; fatigue: number; mood_swings: number;
    headache: number; breast_tenderness: number; acne: number; appetite_changes: number;
    back_pain: number; insomnia: number;
  };
  simulator: { active: boolean; simulated_day: number; custom_modifiers: Record<string, number> };
}

export interface PhasePersonality {
  personality_hint: string;
  tone: string;
  system_prompt_hint: string;
}

export interface CycleProfile {
  name: string;
  gender: string;
  phases: Record<"menstruation" | "follicular" | "ovulation" | "luteal", PhasePersonality>;
}

// MAC - Multi-Agent Cluster
export type AgentRole = "persona" | "analyst" | "developer" | "limbic" | "world_engine";

export interface RoleMapping {
  persona?: string[];
  analyst?: string[];
  developer?: string[];
  limbic?: string[];
  world_engine?: string[];
}

export interface AgentMemo {
  id: string;
  sender: AgentRole;
  recipient: AgentRole;
  type: "emotion" | "urgency" | "strategy" | "info" | "warning";
  content: string;
  timestamp: string;
  ttl_days: number;
  read: boolean;
  priority: "low" | "normal" | "high" | "critical";
}

export interface InternalComm {
  memos: AgentMemo[];
  last_cleanup: string;
}

export interface AgentActivityLog {
  timestamp: string;
  agent_id: string;
  agent_role: AgentRole;
  action: string;
  reason: string;
  metadata?: Record<string, unknown>;
}

// Tool Parameters
export interface EmotionParams {
  action: string;
  mood?: string;
  energy?: string;
  memory?: string;
  pattern?: string;
  person?: string;
  note?: string;
}

export interface GrowthParams {
  action: string;
  category?: string;
  content?: string;
  limit?: number;
}

export interface DesireParams {
  action: string;
  content?: string;
  goal?: string;
}

export interface HobbyParams {
  action: string;
  hobby_id?: string;
  name?: string;
  category?: string;
  description?: string;
  notes?: string;
  mood_before?: string;
  mood_after?: string;
}

export interface DreamParams {
  action: string;
  moment?: string;
  notes?: string;
}

// ---------------------------------------------------------------------------
// Sensory descriptions (Prompts - Always English)
// ---------------------------------------------------------------------------

export const SENSATIONS: Record<string, Record<string, string[]>> = {
  bladder: {
    high: ["Extreme, painful bladder pressure. You MUST go NOW!"],
    medium: ["Strong urge to pee. You feel restless."],
    low: ["You notice your bladder clearly."],
  },
  hunger: {
    high: ["Your stomach growls loudly, you feel weak from hunger."],
    medium: ["You have a strong appetite."],
    low: ["You notice you should eat something soon."],
  },
  thirst: {
    high: ["Your mouth is dry, you desperately need a drink."],
    medium: ["You're thirsty."],
    low: ["A glass of water would be nice."],
  },
  arousal: {
    high: ["Extreme physical arousal. Every touch of your clothing is intense."],
    medium: ["A pulsing desire spreads through you."],
    low: ["A faint tingle beneath your skin."],
  },
  stress: {
    high: ["You're extremely tense, your hands are slightly trembling."],
    medium: ["You feel stressed and restless."],
    low: ["Slight inner tension."],
  },
  hygiene: {
    high: ["You feel uncomfortable and unclean. A shower is urgently needed."],
    medium: ["You could use a shower."],
    low: ["You don't feel quite fresh anymore."],
  },
  energy: {
    low_critical: ["You're completely exhausted. Your eyes are closing."],
    low_medium: ["You're tired and unfocused."],
  },
  bowel: {
    high: ["Strong pressure in your abdomen. You urgently need the toilet."],
    medium: ["Your stomach is rumbling. You should find a toilet soon."],
    low: ["Slight feeling of fullness in your abdomen."],
  },
  libido: {
    high: ["A deep, persistent desire burns within you. It's hard to think of anything else."],
    medium: ["You feel a warm, pulsing desire."],
    low: ["A quiet longing, barely more than a whisper."],
  },
};

// ---------------------------------------------------------------------------
// Cycle: Hormone lookup tables (28-day, 0-100 scale, medically referenced)
// ---------------------------------------------------------------------------

export const HORMONE_ESTROGEN = [
  20, 22, 25, 28, 30, 35, 42, 50, 60, 70, 80, 90, 95, 100,
  85, 65, 50, 45, 55, 65, 70, 68, 60, 50, 40, 32, 25, 20
];
export const HORMONE_PROGESTERONE = [
  5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 8,
  15, 30, 50, 65, 80, 90, 100, 95, 85, 70, 55, 40, 20, 8
];
export const HORMONE_LH = [
  10, 10, 10, 12, 12, 14, 16, 18, 22, 30, 45, 70, 95, 100,
  40, 15, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10
];
export const HORMONE_FSH = [
  35, 40, 50, 55, 60, 65, 70, 65, 55, 45, 40, 50, 70, 80,
  40, 25, 20, 18, 16, 15, 14, 13, 12, 12, 15, 20, 25, 30
];

// ---------------------------------------------------------------------------
// Utility Functions
// ---------------------------------------------------------------------------

export function getRealWorldSeason(): WorldState["season"] {
  const month = new Date().getMonth() + 1;
  if (month >= 3 && month <= 5) return "spring";
  if (month >= 6 && month <= 8) return "summer";
  if (month >= 9 && month <= 11) return "autumn";
  return "winter";
}

export function getEstimatedWeather(season: WorldState["season"]): { weather: WorldState["weather"], temp: number } {
  const rand = Math.random();
  switch (season) {
    case "summer":
      return rand > 0.3 ? { weather: "sunny", temp: 25 + Math.round(rand * 10) } : { weather: "cloudy", temp: 20 };
    case "winter":
      return rand > 0.5 ? { weather: "snowy", temp: -2 - Math.round(rand * 5) } : { weather: "cloudy", temp: 2 };
    case "autumn":
      return rand > 0.4 ? { weather: "rainy", temp: 10 } : { weather: "stormy", temp: 8 };
    default:
      return { weather: "sunny", temp: 18 };
  }
}

export function getSkillMultiplier(skillState: SkillState | null, skillName: string, base: number = 20): number {
  if (!skillState?.skills) return 1.0;
  const skill = skillState.skills.find(s => s.name.toLowerCase() === skillName.toLowerCase());
  if (!skill) return 1.0;
  return 1 + (skill.level / base);
}

/**
 * Get a sensory description for a need value.
 */
export function getSensation(value: number, type: string): string | null {
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

export function getCycleHormones(day: number): CycleState["hormones"] {
  const i = Math.max(0, Math.min(27, day - 1));
  return {
    estrogen: HORMONE_ESTROGEN[i],
    progesterone: HORMONE_PROGESTERONE[i],
    lh: HORMONE_LH[i],
    fsh: HORMONE_FSH[i],
  };
}

export function getAgeSensation(ageDays: number, stage: LifeStage): string | null {
  const years = Math.floor(ageDays / 365.25);

  if (stage === "infant") {
    return "Your senses are new and overwhelming. Everything is bright and loud.";
  }
  if (stage === "child") {
    return "You're full of curiosity. The world is fascinating.";
  }
  if (stage === "teen") {
    return "Hormones surge through you. Emotions feel intense and all-consuming.";
  }
  if (stage === "adult") {
    return "You feel in your prime, capable and focused.";
  }
  if (stage === "middle_adult") {
    if (years >= 65) {
      return "You notice subtle changes in your energy levels.";
    }
    return null;
  }
  if (stage === "senior") {
    return "Your body moves slower. Wisdom fills the spaces where energy once did.";
  }
  return null;
}
