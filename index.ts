import { Type } from "@sinclair/typebox";
import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { promises as fs, existsSync } from "node:fs";
import { join, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Needs {
  energy: number;
  hunger: number;
  thirst: number;
  hygiene: number;
  bladder: number;
  bowel: number;
  stress: number;
  arousal: number;
  libido: number;
}

interface Appearance {
  hair: string;
  eyes: string;
  modifications: string[];
}

interface Physique {
  current_location: string;
  current_outfit: string[];
  needs: Needs;
  last_tick: string;
  appearance: Appearance;
}

interface CycleState {
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

interface Interests {
  hobbies: string[];
  likes: string[];
  wishes: string[];
}

interface WorldLocation {
  id: string;
  name: string;
  description: string;
}

interface ExperienceEntry {
  id: string;
  timestamp: string;
  source: string;
  content: string;
  significance: "routine" | "notable" | "pivotal";
  significance_reason: string;
  reflected: boolean;
  somatic_context?: Partial<Needs>;
}

interface InteriorObject {
  id: string;
  name: string;
  category: string;
  description: string;
  located_on?: string;
  items_on?: string[];
  images: string[];
  added_at: string;
}

interface InteriorRoom {
  id: string;
  name: string;
  description: string;
  objects: InteriorObject[];
}

interface Interior { rooms: InteriorRoom[]; }

interface InventoryItem {
  id: string;
  name: string;
  category: string;
  description: string;
  quantity: number;
  location?: string;
  images: string[];
  tags: string[];
  added_at: string;
  // Phase 6: Utility
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

// ---------------------------------------------------------------------------
// Phase 6: The Living World Interfaces
// ---------------------------------------------------------------------------

interface SkillEntry {
  id: string;
  name: string;
  level: number;
  xp: number;
  xp_to_next: number;
  last_trained: string | null;
}

interface SkillState {
  skills: SkillEntry[];
  total_xp: number;
}

interface WorldState {
  weather: "sunny" | "cloudy" | "rainy" | "stormy" | "snowy";
  temperature: number;
  season: "spring" | "summer" | "autumn" | "winter";
  market_modifier: number; // 0.8 to 1.2
  last_update: string;
  sync_to_real_world: boolean;
}

/**
 * Determine the current season based on the real-world date.
 */
function getRealWorldSeason(): WorldState["season"] {
  const month = new Date().getMonth() + 1; // 0-indexed
  if (month >= 3 && month <= 5) return "spring";
  if (month >= 6 && month <= 8) return "summer";
  if (month >= 9 && month <= 11) return "autumn";
  return "winter";
}

/**
 * Approximate weather based on season if no API is available.
 */
function getEstimatedWeather(season: WorldState["season"]): { weather: WorldState["weather"], temp: number } {
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

interface Trauma {
  id: string;
  description: string;
  severity: number; // 0-100
  trigger: string;
  decay_rate: number; // per day
  added_at: string;
}

interface PsychState {
  resilience: number; // 0-100
  traumas: Trauma[];
  phobias: string[];
  joys: string[]; // Positive memories that buff resilience
}

interface ReputationState {
  global_score: number; // -100 to 100
  circles: { name: string; score: number }[];
}

interface Inventory {
  items: InventoryItem[];
  categories: string[];
}

interface WardrobeItem {
  id: string;
  name: string;
  images: string[];
}

interface DevProject {
  id: string;
  name: string;
  type: "tool" | "skill" | "plugin" | "script";
  status: "draft" | "pending_review" | "approved" | "active";
  description: string;
  files: string[];
  created_at: string;
  approved: boolean;
  approved_at: string | null;
  // Phase 4: Self-Development Engine
  review_feedback?: string;
  reviewed_by?: string;
  test_results?: DevTestResult[];
  last_test_run?: string;
  auto_load?: boolean;
}

interface DevTestResult {
  timestamp: string;
  status: "pass" | "fail" | "error";
  message: string;
  details?: string;
}

interface DevManifest { projects: DevProject[]; }

// ---------------------------------------------------------------------------
// New v2 interfaces — Phase Personality, Dreams, Hobbies
// ---------------------------------------------------------------------------

interface PhasePersonality {
  personality_hint: string;
  tone: string;
  system_prompt_hint: string;
}

interface CycleProfile {
  name: string;
  gender: string;
  phases: Record<"menstruation" | "follicular" | "ovulation" | "luteal", PhasePersonality>;
}

interface DreamMoment {
  timestamp: string;
  text: string;
}

interface DreamState {
  active: boolean;
  started_at: string | null;
  moments: DreamMoment[];
}

interface HobbySession {
  id: string;
  started_at: string;
  ended_at: string | null;
  duration_minutes: number | null;
  notes: string;
  mood_before: string;
  mood_after: string;
}

interface HobbyEntry {
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

interface HobbyLog {
  hobbies: HobbyEntry[];
}

// ---------------------------------------------------------------------------
// Phase 1: Chronos - Aging & Lifecycle (PROJECT_GENESIS)
// ---------------------------------------------------------------------------

type LifeStage = "infant" | "child" | "teen" | "adult" | "middle_adult" | "senior";

interface LifecycleState {
  birth_date: string;                    // ISO date string (YYYY-MM-DD)
  biological_age_days: number;           // Current age in days
  life_stage: LifeStage;                 // Current life stage
  last_aging_check: string;              // ISO timestamp of last aging calculation
  age_progression_enabled: boolean;      // Whether aging advances automatically
}

interface VitalityMetrics {
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

interface TelemetryEntry {
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

// Life-stage metabolism multipliers
interface LifeStageMultipliers {
  energy: number;   // Energy decay rate multiplier
  hunger: number;   // Hunger increase rate multiplier
  thirst: number;
  hygiene: number;
  stress: number;
  bladder: number;
  bowel: number;
  arousal?: number;
  libido?: number;
}

// ---------------------------------------------------------------------------
// Phase 2: Social Fabric - Social Entity & Relationships
// ---------------------------------------------------------------------------

type RelationshipType = "family" | "friend" | "romantic" | "professional" | "acquaintance" | "stranger";

interface SocialEntity {
  id: string;
  name: string;
  relationship_type: RelationshipType;
  bond: number;        // -100 to 100 (enemies to soulmates)
  trust: number;       // 0 to 100
  intimacy: number;    // 0 to 100
  last_interaction: string;  // ISO timestamp
  interaction_count: number;
  history_summary: string;   // Brief summary of relationship history
  introduced_at: string;     // When this entity was first met
  notes: string;             // Additional notes about the entity
}

interface SocialState {
  entities: SocialEntity[];
  last_network_search: string | null;
  circles: string[];  // User-defined circles (e.g., "Work", "Family", "Hobbies")
  last_decay_check?: string; // ISO timestamp for 24h decay guard
}

interface SocialInteractionLog {
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

// ---------------------------------------------------------------------------
// Phase 3: Prosperity & Labor - Economy Module
// ---------------------------------------------------------------------------

type JobType = "full_time" | "part_time" | "freelance" | "contract";

interface IncomeSource {
  id: string;
  source_name: string;
  job_type: JobType;
  position: string;
  employer_id: string | null;  // Linked to social.json entity
  salary_per_month: number;
  salary_per_hour: number | null;
  hours_per_week: number | null;
  started_at: string;
  ended_at: string | null;
}

interface RecurringExpense {
  id: string;
  name: string;
  amount: number;
  frequency: "weekly" | "monthly" | "yearly";
  category: "rent" | "utilities" | "insurance" | "subscription" | "loan" | "other";
  next_due_date: string;
  is_active: boolean;
}

interface Debt {
  id: string;
  name: string;
  principal: number;      // Original amount
  current_balance: number;  // Remaining amount
  interest_rate_annual: number;  // Annual interest rate (%)
  minimum_payment: number;
  due_date: string;
  creditor: string;
}

interface FinanceState {
  balance: number;
  currency: string;
  income_sources: IncomeSource[];
  expenses_recurring: RecurringExpense[];
  debts: Debt[];
  last_expense_process: string;  // ISO timestamp
  last_income_process: string;
  last_interest_process?: string; // ISO timestamp — guards against multiple interest charges per month
  net_worth: number;  // Calculated: balance - total debt
}

interface EconomyEvent {
  id: string;
  timestamp: string;
  event_type: "income" | "expense" | "debt_payment" | "debt_incurred" | "job_started" | "job_ended" | "crisis";
  amount: number;
  description: string;
  related_entity_id: string | null;
}

// ---------------------------------------------------------------------------
// New v2 tool params interfaces
// ---------------------------------------------------------------------------

interface EmotionParams {
  action: string;
  mood?: string;
  energy?: string;
  memory?: string;
  pattern?: string;
  person?: string;
  note?: string;
}

interface GrowthParams {
  action: string;
  category?: string;
  content?: string;
  limit?: number;
}

interface DesireParams {
  action: string;
  content?: string;
  goal?: string;
}

interface HobbyParams {
  action: string;
  hobby_id?: string;
  name?: string;
  category?: string;
  description?: string;
  notes?: string;
  mood_before?: string;
  mood_after?: string;
}

interface DreamParams {
  action: string;
  moment?: string;
  notes?: string;
}

// ---------------------------------------------------------------------------
// MAC - Multi-Agent Cluster Types
// ---------------------------------------------------------------------------
type AgentRole = "persona" | "analyst" | "developer" | "limbic";

interface RoleMapping {
  persona?: string[];
  analyst?: string[];
  developer?: string[];
  limbic?: string[];
}

interface AgentMemo {
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

interface InternalComm {
  memos: AgentMemo[];
  last_cleanup: string;
}

interface AgentActivityLog {
  timestamp: string;
  agent_id: string;
  agent_role: AgentRole;
  action: string;
  reason: string;
  metadata?: Record<string, unknown>;
}

// Tool access matrix - which roles can access which tools
const TOOL_ACCESS_MATRIX: Record<AgentRole, string[]> = {
  persona: [
    "reality_needs", "reality_move", "reality_dress", "reality_shop",
    "reality_diary", "reality_pleasure", "reality_cycle", "reality_emotion",
    "reality_desire", "reality_hobby", "reality_dream",
    "reality_socialize", "reality_network",
    "reality_interior", "reality_inventory",
    "reality_manage_memos"
  ],
  analyst: [
    "reality_job_market", "reality_work",
    "reality_override", "reality_inject_event", "reality_export_research_data",
    "reality_socialize", "reality_network",
    "reality_develop", "reality_review_project",
    "soul_evolution_pipeline", "soul_evolution_propose", "soul_evolution_reflect",
    "soul_evolution_govern", "soul_evolution_apply",
    "reality_manage_memos",
    "reality_genesis"
  ],
  developer: [
    "reality_develop",
    "reality_manage_memos"
  ],
  limbic: [
    "reality_needs", "reality_move", "reality_dress",
    "reality_emotion", "reality_desire", "reality_cycle",
    "reality_socialize", "reality_network",
    "reality_manage_memos"
  ]
};

interface PluginConfig {
  workspacePath: string;
  language: "de" | "en";
  // Phase 1: Chronos - Aging & Lifecycle
  birthDate?: string;           // ISO date string (YYYY-MM-DD)
  initialAgeDays?: number;       // Starting age in days (if not starting from birth)
  // Phase 3: Prosperity & Labor
  initialBalance?: number;       // Starting balance (default: 1000)
  modules: {
    eros: boolean;
    cycle: boolean;
    dreams: boolean;
    hobbies: boolean;
    utility?: boolean;
    psychology?: boolean;
    skills?: boolean;
    world?: boolean;
    reputation?: boolean;
    desktop?: boolean;
    legacy?: boolean;
  };
  metabolismRates: Record<string, number>;
  reflexThreshold: number;
  growthContextEntries?: number;
  dreamWindow?: { start: number; end: number };
  dreamEnergyThreshold?: number;
  evolution?: {
    governance?: string;
    reflection?: {
      routine_batch_size?: number;
      notable_batch_size?: number;
      pivotal_immediate?: boolean;
      min_interval_minutes?: number;
    };
    sources?: {
      conversation?: boolean;
      moltbook?: boolean;
      x?: boolean;
    };
  };
  development?: {
    enabled?: boolean;
    auto_load_approved?: boolean;
  };
  // MAC - Multi-Agent Cluster
  roleMapping?: RoleMapping;
  memoTTL?: number;
}

// Typed shape of the skill config.json written by this plugin
interface SkillConfig {
  governance?: { level?: string };
  reflection?: {
    routine_batch_size?: number;
    notable_batch_size?: number;
    pivotal_immediate?: boolean;
    min_interval_minutes?: number;
  };
  sources?: {
    conversation?: { enabled?: boolean };
    moltbook?: { enabled?: boolean };
    x?: { enabled?: boolean };
  };
  [key: string]: unknown; // preserve unknown fields from existing config
}

// ---------------------------------------------------------------------------
// Typed params interfaces for tool execute functions
// (avoids `any` in execute signatures)
// ---------------------------------------------------------------------------
interface NeedsParams   { action: string }
interface MoveParams    { location: string }
interface DressParams   { outfit: string[] }
interface ShopParams    { items: string[]; category?: string }
interface DiaryParams   { entry: string }
interface PleasureParams { intensity?: number }
interface CycleParams   { action: string; day?: number; symptom?: string; multiplier?: number; simulator_active?: boolean }
interface InterestsParams { action: string; category: string; item: string }
interface InteriorParams  {
  action: string;
  room_id?: string; room_name?: string; room_description?: string;
  object_id?: string; object_name?: string; object_category?: string; object_description?: string;
  place_on?: string; target_room?: string;
}
interface InventoryParams {
  action: "list" | "add" | "remove" | "update" | "search" | "use";
  item_id?: string; name?: string; category?: string; description?: string;
  quantity?: number; location?: string; tags?: string[]; query?: string;
}
interface DevelopParams {
  action: "init_project" | "create_project" | "write_code" | "write_file" | "read_file" | "list_projects" | "run_test" | "submit_review" | "status" | "delete_project";
  project_id?: string;
  project_name?: string;
  project_type?: "tool" | "skill" | "plugin" | "script";
  project_description?: string;
  file_path?: string;
  file_content?: string;
}

interface ReviewParams {
  action: "approve" | "reject" | "list_pending" | "list_approved";
  project_id?: string;
  feedback?: string;
  auto_load?: boolean;
}

// Phase 5: Research Lab - Tool params
interface LifeSummaryParams {
  action: "full" | "milestones" | "vitals" | "social" | "finance";
}

interface SocialMapParams {
  action: "get" | "entity_details";
  entity_id?: string;
}

interface ActivitySummaryParams {
  limit?: number;
  agent_role?: string;
}

// Phase 7: Origin Engine - Genesis params
interface GenesisParams {
  action: "bootstrap";
  manifest: GenesisManifest;
}

interface GenesisManifest {
  physique?: {
    current_location?: string;
    current_outfit?: string[];
    needs?: {
      energy?: number;
      hunger?: number;
      thirst?: number;
      hygiene?: number;
      bladder?: number;
      bowel?: number;
      stress?: number;
      arousal?: number;
      libido?: number;
    };
  };
  lifecycle?: {
    birth_date?: string;
    biological_age_days?: number;
    life_stage?: string;
  };
  finances?: {
    balance?: number;
    currency?: string;
    income_sources?: Array<{
      source_name: string;
      job_type: string;
      position: string;
      salary_per_month: number;
    }>;
    debts?: Array<{
      name: string;
      principal: number;
      interest_rate_annual: number;
    }>;
  };
  social?: {
    entities?: Array<{
      name: string;
      relationship_type: string;
      bond: number;
      trust: number;
      intimacy: number;
      history_summary: string;
    }>;
  };
  skills?: {
    skills?: Array<{
      name: string;
      level: number;
      xp: number;
    }>;
    total_xp?: number;
  };
  psychology?: {
    resilience?: number;
    traumas?: Array<{
      description: string;
      severity: number;
      trigger: string;
      decay_rate: number;
    }>;
    joys?: string[];
    phobias?: string[];
  };
  identity?: {
    biography: string;
    name: string;
    core_traits?: string[];
  };
  soul?: {
    personality?: string[];
    philosophy?: string[];
    boundaries?: string[];
    continuity?: string[];
  };
}

// Phase 2: Social Fabric - Tool params
interface SocializeParams {
  target_id?: string;   // Existing entity ID
  target_name?: string; // Or create new entity
  action: "talk" | "gift" | "conflict" | "apologize" | "support" | "ignore";
  context?: string;     // What happened
}

interface NetworkParams {
  action: "search_contacts" | "manage_circles" | "add_entity" | "remove_entity";
  entity_name?: string;
  entity_type?: RelationshipType;
  circle?: string;
  target_id?: string;
}

// Phase 3: Economy - Tool params
interface JobMarketParams {
  action: "search" | "apply" | "resign" | "list_jobs";
  job_id?: string;
  position?: string;
  expected_salary?: number;
}

interface WorkParams {
  action: "perform_shift" | "overtime" | "check_schedule";
  hours?: number;
}

// Phase 4: Analytics & Lab - Tool params
interface InjectEventParams {
  event_type: string;
  severity: number;
  description?: string;
  amount?: number;  // For financial events
}

interface ExportParams {
  format: "json" | "csv";
  date_from?: string;
  date_to?: string;
  include_telemetry?: string[];
}

interface MemoParams {
  action: "add" | "list" | "delete" | "mark_read" | "clear_read";
  recipient?: string;
  type?: "emotion" | "urgency" | "strategy" | "info" | "warning";
  content?: string;
  priority?: "low" | "normal" | "high" | "critical";
  memo_id?: string;
}

interface OverrideParams {
  target: "balance" | "age_days" | "stress" | "energy" | "hunger" | "health";
  value: number;
  reason?: string;
}

// Phase 6: Living World - Tool params
interface SkillParams {
  action: "train" | "check" | "list";
  skill_name?: string;
  duration?: number;
}

interface DesktopParams {
  action: "set_wallpaper" | "set_theme" | "get_info";
  path?: string; // /path/to/image.jpg
  theme?: "dark" | "light";
}

// ---------------------------------------------------------------------------
// Hook event shapes (before_prompt_build / before_tool_call / llm_output are
// OpenClaw internal hooks, not listed in the public automation/hooks docs.
// They function identically to the api.on() pattern from the public SDK but
// fire at model-pipeline injection points. Keep typed as `unknown` until the
// SDK exposes them officially.
// ---------------------------------------------------------------------------
interface BeforeToolCallCtx { toolName?: string }
interface LlmOutputEvent    { lastAssistant?: string }

// ---------------------------------------------------------------------------
// Sensory descriptions (Prompts - Always English)
// ---------------------------------------------------------------------------

const SENSATIONS: Record<string, Record<string, string[]>> = {
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

/**
 * Get a sensory description for a need value.
 * Prompts are always returned in English.
 */
function getSensation(value: number, type: string): string | null {
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
// Cycle: Hormone lookup tables (28-day, 0-100 scale, medically referenced)
// ---------------------------------------------------------------------------

const HORMONE_ESTROGEN = [
  20, 22, 25, 28, 30, 35, 42, 50, 60, 70, 80, 90, 95, 100,
  85, 65, 50, 45, 55, 65, 70, 68, 60, 50, 40, 32, 25, 20
];
const HORMONE_PROGESTERONE = [
  5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 8,
  15, 30, 50, 65, 80, 90, 100, 95, 85, 70, 55, 40, 20, 8
];
const HORMONE_LH = [
  10, 10, 10, 12, 12, 14, 16, 18, 22, 30, 45, 70, 95, 100,
  40, 15, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10
];
const HORMONE_FSH = [
  35, 40, 50, 55, 60, 65, 70, 65, 55, 45, 40, 50, 70, 80,
  40, 25, 20, 18, 16, 15, 14, 13, 12, 12, 15, 20, 25, 30
];

function getCyclePhase(day: number): CycleState["phase"] {
  if (day <= 5) return "menstruation";
  if (day <= 13) return "follicular";
  if (day <= 15) return "ovulation";
  return "luteal";
}

function getCycleHormones(day: number): CycleState["hormones"] {
  const i = Math.max(0, Math.min(27, day - 1));
  return {
    estrogen: HORMONE_ESTROGEN[i],
    progesterone: HORMONE_PROGESTERONE[i],
    lh: HORMONE_LH[i],
    fsh: HORMONE_FSH[i],
  };
}

function getCycleMetabolismModifiers(phase: CycleState["phase"]): Partial<Needs> {
  const mods: Record<CycleState["phase"], Partial<Needs>> = {
    menstruation: { energy: -12, hunger: 5, stress: 8, libido: -3 },
    follicular:   { energy: 5, stress: -5, libido: 2 },
    ovulation:    { energy: 8, arousal: 15, stress: -8, libido: 10 },
    luteal:       { energy: -8, hunger: 12, stress: 10, libido: -2 },
  };
  return mods[phase];
}

function getDefaultCycleState(): CycleState {
  const now = new Date().toISOString();
  return {
    cycle_length: 28,
    current_day: 1,
    start_date: now,
    last_advance: now,
    phase: "menstruation",
    hormones: getCycleHormones(1),
    symptom_modifiers: {
      cramps: 1, bloating: 1, fatigue: 1, mood_swings: 1, headache: 1,
      breast_tenderness: 1, acne: 1, appetite_changes: 1, back_pain: 1, insomnia: 1,
    },
    simulator: { active: false, simulated_day: 1, custom_modifiers: {} },
  };
}

/**
 * Create default lifecycle state based on plugin config
 */
function getDefaultLifecycleState(birthDate?: string, initialAgeDays?: number): LifecycleState {
  const now = new Date();
  const bd = birthDate ?? "2000-01-01";
  const initial = initialAgeDays ?? 0;

  // Calculate initial age
  const ageDays = calculateAgeDays(bd, initial);
  const stage = getLifeStage(ageDays);

  return {
    birth_date: bd,
    biological_age_days: ageDays,
    life_stage: stage,
    last_aging_check: now.toISOString(),
    age_progression_enabled: true,
  };
}

/**
 * Update lifecycle state (advance age if needed)
 * Returns true if age was advanced
 */
function updateLifecycle(lifecycle: LifecycleState): boolean {
  const now = new Date();
  const lastCheck = new Date(lifecycle.last_aging_check);
  const diffHours = (now.getTime() - lastCheck.getTime()) / 3600000;

  // Advance age every ~24 hours (real time)
  if (diffHours >= 24) {
    const daysAdvanced = Math.floor(diffHours / 24);
    lifecycle.biological_age_days += daysAdvanced;
    lifecycle.life_stage = getLifeStage(lifecycle.biological_age_days);
    // Preserve fractional remainder so partial days aren't lost
    const remainderMs = (diffHours - daysAdvanced * 24) * 3600000;
    lifecycle.last_aging_check = new Date(now.getTime() - remainderMs).toISOString();
    return true;
  }
  return false;
}

/**
 * Log vitality metrics to telemetry file
 * Creates daily JSONL file: telemetry/vitality_YYYY-MM-DD.jsonl
 */
// Track last telemetry log date to avoid excessive writes
let lastTelemetryDate = "";

async function logVitalityTelemetry(
  telemetryPath: string,
  lifecycle: LifecycleState,
  needs: Needs,
  location: string
): Promise<void> {
  const now = new Date();
  const dateStr = now.toISOString().slice(0, 10); // YYYY-MM-DD

  // Only log once per day to prevent excessive file growth
  if (dateStr === lastTelemetryDate) return;
  lastTelemetryDate = dateStr;

  // Calculate health index from needs (0-100)
  // Lower is worse: average of inverted needs
  const avgNeeds = (needs.energy + (100 - needs.hunger) + (100 - needs.thirst) +
    needs.hygiene + (100 - needs.stress)) / 5;
  const healthIndex = Math.round(avgNeeds);

  const entry: TelemetryEntry = {
    timestamp: now.toISOString(),
    age_days: lifecycle.biological_age_days,
    age_years: daysToYears(lifecycle.biological_age_days),
    life_stage: lifecycle.life_stage,
    health_index: healthIndex,
    energy: needs.energy,
    hunger: needs.hunger,
    thirst: needs.thirst,
    stress: needs.stress,
    hygiene: needs.hygiene,
    bladder: needs.bladder,
    bowel: needs.bowel,
    location,
  };

  const filePath = join(telemetryPath, `vitality_${dateStr}.jsonl`);
  await appendJsonl(filePath, entry);
}

function advanceCycleDay(cycle: CycleState): boolean {
  // Enforce 28-day cycle (hormone tables are fixed-size)
  if (cycle.cycle_length !== 28) cycle.cycle_length = 28;

  const now = new Date();
  const lastAdv = new Date(cycle.last_advance);
  const diffHours = (now.getTime() - lastAdv.getTime()) / 3600000;
  if (isNaN(diffHours) || diffHours < 20) return false; // ~1 real day = 1 cycle day

  cycle.current_day = (cycle.current_day % cycle.cycle_length) + 1;
  cycle.phase = getCyclePhase(cycle.current_day);
  cycle.hormones = getCycleHormones(cycle.current_day);
  cycle.last_advance = now.toISOString();
  return true;
}

// ---------------------------------------------------------------------------
// Phase 1: Chronos - Lifecycle Helper Functions
// ---------------------------------------------------------------------------

/**
 * Calculate biological age in days from birthDate and initialAgeDays
 */
function calculateAgeDays(birthDate: string, initialAgeDays: number): number {
  const birth = new Date(birthDate);
  if (isNaN(birth.getTime())) {
    // Invalid birthDate, fall back to initialAgeDays
    return initialAgeDays;
  }
  const now = new Date();
  const diffTime = now.getTime() - birth.getTime();
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
  return initialAgeDays + diffDays;
}

/**
 * Convert age in days to years (decimal)
 */
function daysToYears(days: number): number {
  return Math.floor(days / 365.25);
}

/**
 * Determine life stage based on age in days
 * - infant: 0-730 days (0-2 years)
 * - child: 730-4380 days (2-12 years)
 * - teen: 4380-6570 days (12-18 years)
 * - adult: 6570-21900 days (18-60 years)
 * - middle_adult: 21900-25550 days (60-70 years)
 * - senior: 25550+ days (70+ years)
 */
function getLifeStage(ageDays: number): LifeStage {
  if (ageDays < 730) return "infant";
  if (ageDays < 4380) return "child";
  if (ageDays < 6570) return "teen";
  if (ageDays < 21900) return "adult";
  if (ageDays < 25550) return "middle_adult";
  return "senior";
}

/**
 * Get metabolism rate multipliers based on life stage
 * These scale the base metabolismRates from plugin config
 */
function getLifeStageMultipliers(stage: LifeStage): LifeStageMultipliers {
  const defaults: LifeStageMultipliers = {
    energy: 1.0,
    hunger: 1.0,
    thirst: 1.0,
    hygiene: 1.0,
    stress: 1.0,
    bladder: 1.0,
    bowel: 1.0,
  };

  switch (stage) {
    case "infant":
      // Babies need frequent feeding, lots of sleep
      return { ...defaults, energy: 0.8, hunger: 1.5, thirst: 1.3, stress: 0.5, arousal: 0, libido: 0 };
    case "child":
      // Children have high energy, fast metabolism
      return { ...defaults, energy: 1.2, hunger: 1.3, thirst: 1.2, stress: 0.7, arousal: 0, libido: 0 };
    case "teen":
      // Teens have increased appetite, high energy needs, more stress
      return { ...defaults, energy: 1.1, hunger: 1.2, thirst: 1.1, stress: 1.3, arousal: 0.3, libido: 0.2 };
    case "adult":
      // Standard adult metabolism
      return defaults;
    case "middle_adult":
      // Metabolism starts slowing
      return { ...defaults, energy: 0.9, hunger: 0.9, thirst: 0.95, stress: 1.1 };
    case "senior":
      // Seniors: slower metabolism, lower energy, less hunger
      return { ...defaults, energy: 0.7, hunger: 0.75, thirst: 0.85, stress: 0.9, hygiene: 1.1 };
    default:
      return defaults;
  }
}

/**
 * Get aging-related sensory injection text (English-only for prompts)
 */
function getAgeSensation(ageDays: number, stage: LifeStage): string | null {
  const ageYears = daysToYears(ageDays);

  // Only inject sensations at certain age milestones or significant stages
  if (stage === "infant") {
    return "You are a tiny baby. You cannot yet speak or walk.";
  }

  if (stage === "child" && ageYears === 2) {
    return "You are a toddler. You are learning to walk and talk.";
  }

  if (stage === "teen" && ageYears === 13) {
    return "You are now a teenager. Your body and mind are changing rapidly.";
  }

  if (stage === "adult" && ageYears === 18) {
    return "You are now an adult. You are of legal age and responsible for yourself.";
  }

  if (stage === "senior" && ageYears === 65) {
    return "You are now in your senior years. You look back on a long life.";
  }

  // General age-related sensations for seniors
  if (stage === "senior" || stage === "middle_adult") {
    if (ageYears >= 70 && ageYears % 5 === 0) {
      return `You are now ${ageYears} years old. Your body is not as fit as before.`;
    }
  }

  return null;
}

// ---------------------------------------------------------------------------
// Phase 2: Social Fabric - Helper Functions
// ---------------------------------------------------------------------------

/**
 * Get default social state
 */
function getDefaultSocialState(): SocialState {
  const now = new Date().toISOString();
  return {
    entities: [],
    last_network_search: null,
    circles: ["Family", "Friends", "Work", "Hobbies"],
    last_decay_check: now,
  };
}

/**
 * Calculate relationship dynamics changes based on action
 * Returns { bond_change, trust_change, intimacy_change }
 */
function calculateSocialDynamics(
  action: SocializeParams["action"],
  currentBond: number,
  currentTrust: number,
  currentIntimacy: number
): { bond: number; trust: number; intimacy: number } {
  // Base changes for each action type
  const baseChanges: Record<SocializeParams["action"], { bond: number; trust: number; intimacy: number }> = {
    talk: { bond: 3, trust: 2, intimacy: 1 },
    gift: { bond: 8, trust: 5, intimacy: 3 },
    conflict: { bond: -15, trust: -10, intimacy: -2 },
    apologize: { bond: 5, trust: 8, intimacy: 0 },
    support: { bond: 6, trust: 7, intimacy: 4 },
    ignore: { bond: -3, trust: -2, intimacy: -1 },
  };

  const base = baseChanges[action];

  // Relationship decay based on time since last interaction
  // (This is handled separately in updateSocialState)

  // Modifiers based on current relationship state
  let bondMod = 1;
  let trustMod = 1;
  let intimacyMod = 1;

  // High trust means actions have less impact (stable relationships)
  if (currentTrust > 70) {
    trustMod = 0.7;
    bondMod = 0.8;
  }
  // Low trust means actions have more impact
  if (currentTrust < 30) {
    trustMod = 1.3;
    bondMod = 1.2;
  }

  // High intimacy means actions affect bond more
  if (currentIntimacy > 60) {
    bondMod *= 1.2;
  }

  return {
    bond: Math.round(base.bond * bondMod),
    trust: Math.round(base.trust * trustMod),
    intimacy: Math.round(base.intimacy * intimacyMod),
  };
}

/**
 * Apply relationship decay for neglected relationships
 * Returns updated entity or null if no significant decay
 */
function applySocialDecay(entity: SocialEntity, daysSinceInteraction: number): Partial<SocialEntity> | null {
  if (daysSinceInteraction < 7) return null; // No decay for interactions within a week

  // Calculate decay rates
  let bondDecay = 0;
  let trustDecay = 0;
  let intimacyDecay = 0;

  if (daysSinceInteraction >= 7 && daysSinceInteraction < 30) {
    bondDecay = -1;
    trustDecay = -1;
    intimacyDecay = -1;
  } else if (daysSinceInteraction >= 30 && daysSinceInteraction < 90) {
    bondDecay = -3;
    trustDecay = -2;
    intimacyDecay = -3;
  } else if (daysSinceInteraction >= 90) {
    bondDecay = -5;
    trustDecay = -3;
    intimacyDecay = -5;
  }

  // Family relationships decay slower
  if (entity.relationship_type === "family") {
    bondDecay = Math.round(bondDecay * 0.5);
    trustDecay = Math.round(trustDecay * 0.5);
  }

  // Romantic relationships decay faster if neglected
  if (entity.relationship_type === "romantic" && daysSinceInteraction > 14) {
    bondDecay *= 1.5;
    intimacyDecay *= 1.5;
  }

  return {
    bond: Math.max(-100, Math.min(100, entity.bond + bondDecay)),
    trust: Math.max(0, Math.min(100, entity.trust + trustDecay)),
    intimacy: Math.max(0, Math.min(100, entity.intimacy + intimacyDecay)),
  };
}

/**
 * Get social context for sensory injection (Always English).
 */
function getSocialContext(
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

  // Calculate social satisfaction
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
 * Generate social milestone for Soul Evolution
 */
function detectSocialMilestone(
  oldEntity: SocialEntity,
  newEntity: SocialEntity
): string | null {
  // Best friends (bond >= 80)
  if (oldEntity.bond < 80 && newEntity.bond >= 80) {
    return `Became best friends with ${newEntity.name}`;
  }

  // Enemies (bond <= -80)
  if (oldEntity.bond > -80 && newEntity.bond <= -80) {
    return `Became enemies with ${newEntity.name}`;
  }

  // First trust milestone (trust >= 50)
  if (oldEntity.trust < 50 && newEntity.trust >= 50) {
    return `Started trusting ${newEntity.name}`;
  }

  // First intimate moment (intimacy >= 50)
  if (oldEntity.intimacy < 50 && newEntity.intimacy >= 50) {
    return `Became intimate with ${newEntity.name}`;
  }

  return null;
}

// ---------------------------------------------------------------------------
// Phase 3: Prosperity & Labor - Economy Helper Functions
// ---------------------------------------------------------------------------

/**
 * Get default finance state
 */
function getDefaultFinanceState(initialBalance: number = 1000): FinanceState {
  const now = new Date().toISOString();
  return {
    balance: initialBalance,
    currency: "Credits",
    income_sources: [],
    expenses_recurring: [],
    debts: [],
    last_expense_process: now,
    last_income_process: now,
    net_worth: initialBalance,
  };
}

/**
 * Process recurring expenses - called during economic tick
 * Returns events for logging and potential crisis triggers
 */
function processRecurringExpenses(finance: FinanceState, now: Date): EconomyEvent[] {
  const events: EconomyEvent[] = [];
  let totalDue = 0;

  for (const expense of finance.expenses_recurring) {
    if (!expense.is_active) continue;

    const dueDate = new Date(expense.next_due_date);
    if (dueDate <= now) {
      // Process this expense
      const event: EconomyEvent = {
        id: `econ_${Date.now()}_${expense.id}`,
        timestamp: now.toISOString(),
        event_type: "expense",
        amount: -expense.amount,
        description: `Paid ${expense.name}`,
        related_entity_id: null,
      };

      // Check if affordable
      if (finance.balance >= expense.amount) {
        finance.balance -= expense.amount;
        events.push(event);
      } else {
        // Can't afford - trigger crisis
        event.event_type = "crisis";
        event.description = `FAILED to pay ${expense.name} - insufficient funds!`;
        events.push(event);
      }

      // Always advance to next due date (regardless of payment success)
      const nextDue = new Date(dueDate);
      if (expense.frequency === "weekly") {
        nextDue.setDate(nextDue.getDate() + 7);
      } else if (expense.frequency === "monthly") {
        nextDue.setMonth(nextDue.getMonth() + 1);
      } else if (expense.frequency === "yearly") {
        nextDue.setFullYear(nextDue.getFullYear() + 1);
      }
      expense.next_due_date = nextDue.toISOString();

      totalDue += expense.amount;
    }
  }

  finance.last_expense_process = now.toISOString();
  return events;
}

/**
 * Process interest on debts - called during economic tick.
 * Guarded by last_interest_process to ensure interest is only applied once per 28+ days.
 */
function processDebtInterest(finance: FinanceState, now: Date): EconomyEvent[] {
  const events: EconomyEvent[] = [];

  // Time guard: only process interest once per ~month (28 days minimum)
  if (finance.last_interest_process) {
    const lastProcess = new Date(finance.last_interest_process);
    const daysSince = (now.getTime() - lastProcess.getTime()) / (1000 * 60 * 60 * 24);
    if (isNaN(daysSince) || daysSince < 28) return events;
  }

  for (const debt of finance.debts) {
    if (debt.current_balance <= 0) continue;

    // Calculate monthly interest
    const monthlyRate = (debt.interest_rate_annual / 100) / 12;
    const interest = Math.round(debt.current_balance * monthlyRate);

    if (interest > 0) {
      debt.current_balance += interest;

      events.push({
        id: `econ_${Date.now()}_debt_${debt.id}`,
        timestamp: now.toISOString(),
        event_type: "debt_incurred",
        amount: -interest,
        description: `Interest charged on ${debt.name}`,
        related_entity_id: null,
      });
    }
  }

  finance.last_interest_process = now.toISOString();
  return events;
}

/**
 * Calculate total monthly expenses
 */
function calculateMonthlyExpenses(finance: FinanceState): number {
  let total = 0;

  for (const expense of finance.expenses_recurring) {
    if (!expense.is_active) continue;

    if (expense.frequency === "weekly") {
      total += expense.amount * 4.33;  // Average weeks per month
    } else if (expense.frequency === "monthly") {
      total += expense.amount;
    } else if (expense.frequency === "yearly") {
      total += expense.amount / 12;
    }
  }

  // Add minimum debt payments
  for (const debt of finance.debts) {
    total += debt.minimum_payment;
  }

  return Math.round(total);
}

/**
 * Calculate total monthly income
 */
function calculateMonthlyIncome(finance: FinanceState): number {
  let total = 0;

  for (const income of finance.income_sources) {
    if (income.ended_at) continue;  // Job ended
    total += income.salary_per_month;
  }

  return total;
}

/**
 * Get financial context for sensory injection (Always English).
 */
function getFinancialContext(
  finance: FinanceState
): { urgency: string | null; upcomingExpenses: string[] } {
  const now = new Date();
  const upcomingExpenses: string[] = [];
  let urgency: string | null = null;

  // Check upcoming expenses (within 3 days)
  for (const expense of finance.expenses_recurring) {
    if (!expense.is_active) continue;

    const dueDate = new Date(expense.next_due_date);
    const daysUntilDue = Math.ceil((dueDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

    if (daysUntilDue >= 0 && daysUntilDue <= 3) {
      upcomingExpenses.push(`${expense.name}: ${expense.amount} in ${daysUntilDue} days`);
    }
  }

  // Calculate financial situation
  const monthlyIncome = calculateMonthlyIncome(finance);
  const monthlyExpenses = calculateMonthlyExpenses(finance);
  const savingsRate = monthlyIncome > 0 ? ((monthlyIncome - monthlyExpenses) / monthlyIncome) * 100 : 0;

  // Low balance warning
  if (finance.balance < 100) {
    urgency = "Your account balance is critically low! You need to earn money soon.";
  }
  // Negative savings rate
  else if (savingsRate < 0) {
    urgency = `You spend more than you earn. Your bills exceed your income!`;
  }
  // Upcoming large expense
  else if (upcomingExpenses.length > 0 && finance.balance < monthlyExpenses) {
    urgency = `Due soon: ${upcomingExpenses.join(", ")}. You worry about your finances.`;
  }
  // No income
  else if (monthlyIncome === 0 && finance.balance < 500) {
    urgency = "You have no income and little savings. You urgently need to find work.";
  }

  return { urgency, upcomingExpenses };
}

/**
 * Generate job listings based on social connections and random factors
 */
function generateJobListings(socialEntities: SocialEntity[] = []): Array<{
  id: string;
  position: string;
  company: string;
  salary_per_month: number;
  job_type: JobType;
  requirements: string[];
  employer_id: string | null;
  posted_by: string | null;
}> {
  const now = new Date();
  const jobId = `job_${now.getTime()}`;

  const jobTemplates = [
    { position: "Retail Associate", company: "General Store", salary: 1800, type: "full_time" as JobType, req: ["customer service"] },
    { position: "Delivery Driver", company: "QuickShip", salary: 2200, type: "full_time" as JobType, req: ["driver's license", "vehicle"] },
    { position: "Office Assistant", company: "AdminCorp", salary: 2400, type: "full_time" as JobType, req: ["computer skills", "organization"] },
    { position: "Barista", company: "Coffee House", salary: 1600, type: "part_time" as JobType, req: ["customer service", "food handling"] },
    { position: "Web Developer", company: "TechStart", salary: 3500, type: "full_time" as JobType, req: ["programming", "web technologies"] },
    { position: "Tutor", company: "LearnCenter", salary: 2000, type: "part_time" as JobType, req: ["teaching", "subject expertise"] },
    { position: "Warehouse Worker", company: "LogiCo", salary: 2100, type: "full_time" as JobType, req: ["physical fitness"] },
    { position: "Freelance Writer", company: "ContentHub", salary: 2500, type: "freelance" as JobType, req: ["writing", "research"] },
    { position: "Security Guard", company: "SafeSec", salary: 2000, type: "full_time" as JobType, req: ["observation", "reliability"] },
    { position: "Chef Assistant", company: "FoodieRest", salary: 1900, type: "full_time" as JobType, req: ["cooking", "food safety"] },
  ];

  // Add jobs from social connections if available
  const socialJobs = socialEntities
    .filter(e => e.relationship_type === "professional" && e.bond > 30)
    .map(e => ({
      id: generateId("job"),
      position: `${e.name}'s Colleague`,
      company: "Referral Network",
      salary_per_month: 2300 + Math.round(e.bond * 10),
      job_type: "full_time" as JobType,
      requirements: [],
      employer_id: e.id as string | null,
      posted_by: e.name as string | null,
    }));

  // Return 3-5 random jobs + social referrals
  const shuffled = jobTemplates.sort(() => Math.random() - 0.5);
  const selectedJobs = shuffled.slice(0, 4).map((j, i) => ({
    id: `${jobId}_${i}`,
    position: j.position,
    company: j.company,
    salary_per_month: j.salary,
    job_type: j.type,
    requirements: j.req,
    employer_id: null,
    posted_by: null,
  }));

  return [...selectedJobs, ...socialJobs.slice(0, 2)];
}

// ---------------------------------------------------------------------------
// Phase 4: Analytics & Lab - Telemetry Reader & Event Functions
// ---------------------------------------------------------------------------

/**
 * Read telemetry data for visualization
 */
async function readVitalityTelemetry(telemetryPath: string, days: number = 30): Promise<TelemetryEntry[]> {
  const results: TelemetryEntry[] = [];
  const now = new Date();

  for (let i = 0; i < days; i++) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    const dateStr = date.toISOString().slice(0, 10);
    const filePath = join(telemetryPath, `vitality_${dateStr}.jsonl`);

    try {
      const content = await fs.readFile(filePath, "utf-8");
      const lines = content.trim().split("\n");
      for (const line of lines) {
        try {
          results.push(JSON.parse(line));
        } catch { /* skip invalid lines */ }
      }
    } catch {
      // File doesn't exist yet
    }
  }

  return results;
}

/**
 * Read economy telemetry for visualization
 */
async function readEconomyTelemetry(telemetryPath: string, days: number = 30): Promise<EconomyEvent[]> {
  const results: EconomyEvent[] = [];
  const now = new Date();

  for (let i = 0; i < days; i++) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    const dateStr = date.toISOString().slice(0, 10);
    const filePath = join(telemetryPath, `events_${dateStr}.jsonl`);

    try {
      const content = await fs.readFile(filePath, "utf-8");
      const lines = content.trim().split("\n");
      for (const line of lines) {
        try {
          results.push(JSON.parse(line));
        } catch { /* skip invalid lines */ }
      }
    } catch {
      // File doesn't exist yet
    }
  }

  return results;
}

/**
 * Apply life event injection and return narrative for prompt (Always English).
 */
function processLifeEvent(
  eventType: string,
  severity: number,
  finance: FinanceState,
  ph: Physique
): { narrative: string; impact: string } {
  const narratives: Record<string, { en: string; impact: string }> = {
    "win_lottery": {
      en: `You won the lottery! A life-changing moment.`,
      impact: "balance",
    },
    "severe_illness": {
      en: `You became seriously ill. Your body is weakened.`,
      impact: "health",
    },
    "social_scandal": {
      en: `A scandal has damaged your reputation. People are talking.`,
      impact: "social",
    },
    "career_promotion": {
      en: `You got promoted! More responsibility, more money.`,
      impact: "balance",
    },
    "relationship_breakup": {
      en: `An important relationship has ended. Your world is falling apart.`,
      impact: "social",
    },
    "accident": {
      en: `An accident changed your life. You're recovering slowly.`,
      impact: "health",
    },
    "inheritance": {
      en: `A relative passed away and left you an inheritance.`,
      impact: "balance",
    },
    "job_loss": {
      en: `You were laid off. Suddenly your income is gone.`,
      impact: "balance",
    },
  };

  const event = narratives[eventType] || {
    en: `A pivotal event: ${eventType}`,
    impact: "general",
  };

  const severityMod = severity / 100;
  let impactDesc = "";

  // Apply impact based on event type
  switch (event.impact) {
    case "balance": {
      const amount = Math.round((eventType === "win_lottery" || eventType === "inheritance" ? 50000 : -10000) * severityMod);
      finance.balance += amount;
      impactDesc = `${amount > 0 ? "+" : ""}${amount} Credits`;
      break;
    }
    case "health": {
      const healthLoss = Math.round(30 * severityMod);
      // Note: Using stress/energy as proxy for health
      ph.needs.stress = Math.min(100, ph.needs.stress + Math.round(20 * severityMod));
      ph.needs.energy = Math.max(0, ph.needs.energy - Math.round(20 * severityMod));
      impactDesc = `-${healthLoss}% health`;
      break;
    }
    case "social": {
      ph.needs.stress = Math.min(100, ph.needs.stress + Math.round(25 * severityMod));
      impactDesc = "Reputation damaged";
      break;
    }
    default: {
      impactDesc = "Life altered";
    }
  }

  return {
    narrative: event.en,
    impact: impactDesc,
  };
}

/**
 * Export research data in JSON or CSV format
 */
async function exportResearchData(
  telemetryPath: string,
  format: "json" | "csv",
  dateFrom?: string,
  dateTo?: string
): Promise<string> {
  const vitalityPath = join(telemetryPath, "..");
  const economyPath = join(telemetryPath, "..", "economy");

  const from = dateFrom ? new Date(dateFrom) : new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
  const to = dateTo ? new Date(dateTo) : new Date();

  // Gather all data
  const vitalityData: VitalityMetrics[] = [];
  const economyData: EconomyEvent[] = [];

  const current = new Date(from);
  while (current <= to) {
    const dateStr = current.toISOString().slice(0, 10);

    // Read vitality
    try {
      const vPath = join(telemetryPath, `vitality_${dateStr}.jsonl`);
      const vContent = await fs.readFile(vPath, "utf-8");
      for (const line of vContent.trim().split("\n")) {
        if (line) vitalityData.push(JSON.parse(line));
      }
    } catch { /* skip */ }

    // Read economy
    try {
      const ePath = join(economyPath, `events_${dateStr}.jsonl`);
      const eContent = await fs.readFile(ePath, "utf-8");
      for (const line of eContent.trim().split("\n")) {
        if (line) economyData.push(JSON.parse(line));
      }
    } catch { /* skip */ }

    current.setDate(current.getDate() + 1);
  }

  if (format === "json") {
    return JSON.stringify({
      export_date: new Date().toISOString(),
      date_range: { from: from.toISOString(), to: to.toISOString() },
      vitality: vitalityData,
      economy: economyData,
    }, null, 2);
  }

  // CSV format
  // Escape string fields to prevent CSV injection (formula prefixes =, +, -, @)
  const escapeCSV = (val: string): string => {
    const escaped = val.replace(/"/g, '""');
    if (/^[=+\-@\t\r]/.test(escaped)) return `"'${escaped}"`;
    return `"${escaped}"`;
  };

  const csvLines: string[] = [];

  // Vitality CSV
  csvLines.push("# Vitality Data");
  csvLines.push("timestamp,age_days,age_years,life_stage,health_index,energy,hunger,thirst,stress,location");
  for (const v of vitalityData) {
    csvLines.push(`${v.timestamp},${v.age_days},${v.age_years},${escapeCSV(v.life_stage)},${v.health_index},${v.energy},${v.hunger},${v.thirst},${v.stress},${escapeCSV(v.location)}`);
  }

  csvLines.push("");
  csvLines.push("# Economy Data");
  csvLines.push("timestamp,event_type,amount,description");
  for (const e of economyData) {
    csvLines.push(`${e.timestamp},${escapeCSV(e.event_type)},${e.amount},${escapeCSV(e.description)}`);
  }

  return csvLines.join("\n");
}

// ---------------------------------------------------------------------------
// Phase Final: Urge Synergy - Priority System
// ---------------------------------------------------------------------------

interface Urge {
  type: "survival" | "financial" | "social" | "hygiene" | "aspiration";
  priority: number;    // 1 = highest priority
  message: string;
}

function calculateUrgePriority(
  ph: Physique,
  finance: FinanceState | null,
  socialState: SocialState | null,
  lifecycleState: LifecycleState | null
): Urge[] {
  const urges: Urge[] = [];
  const now = new Date();

  // SURVIVAL NEEDS (Priority 1-2) - Critical biological imperatives
  if (ph.needs.energy < 15) {
    urges.push({
      type: "survival",
      priority: 1,
      message: "You are exhausted. Your body demands rest.",

    });
  }

  if (ph.needs.hunger > 85) {
    urges.push({
      type: "survival",
      priority: 1,
      message: "You are starving. Food is an urgent necessity.",

    });
  }

  if (ph.needs.thirst > 85) {
    urges.push({
      type: "survival",
      priority: 1,
      message: "You are parched. You need water immediately.",

    });
  }

  if (ph.needs.bladder > 90) {
    urges.push({
      type: "survival",
      priority: 2,
      message: "Your bladder is screaming. You cannot think of anything else.",

    });
  }

  if (ph.needs.bowel > 85) {
    urges.push({
      type: "survival",
      priority: 2,
      message: "Your bowels are demanding attention. You need a bathroom now.",
    });
  }

  // FINANCIAL CRISIS (Priority 3) - Immediate economic pressure
  if (finance && finance.balance < 100) {
    urges.push({
      type: "financial",
      priority: 3,
      message: "You are in financial crisis. Your account is critically low.",

    });
  } else if (finance && finance.balance < 300 && calculateMonthlyIncome(finance) === 0) {
    urges.push({
      type: "financial",
      priority: 3,
      message: "You have no income and minimal savings. You must find work.",

    });
  }

  // SOCIAL ISOLATION (Priority 4) - Emotional need
  if (socialState && socialState.entities.length === 0) {
    urges.push({
      type: "social",
      priority: 4,
      message: "You feel completely alone. You crave human connection.",

    });
  } else if (socialState) {
    const neglected = socialState.entities.filter(e => {
      const last = new Date(e.last_interaction);
      const days = (now.getTime() - last.getTime()) / (1000 * 60 * 60 * 24);
      return days > 30;
    });
    if (neglected.length >= 3) {
      urges.push({
        type: "social",
        priority: 5,
        message: `You haven't connected with ${neglected.map(n => n.name).slice(0, 2).join(" and ")} in weeks. You miss them.`,
  
      });
    }
  }

  // HYGIENE (Priority 6)
  if (ph.needs.hygiene > 85) {
    urges.push({
      type: "hygiene",
      priority: 6,
      message: "You feel unclean. You need to wash.",

    });
  }

  // STRESS (Priority 7)
  if (ph.needs.stress > 80) {
    urges.push({
      type: "aspiration",
      priority: 7,
      message: "You are overwhelmed by stress. You need relief.",

    });
  }

  // LIFE STAGE ASPIRATIONS (Priority 8-10)
  if (lifecycleState) {
    const ageYears = Math.floor(lifecycleState.biological_age_days / 365.25);
    if (lifecycleState.life_stage === "teen" && ageYears >= 16) {
      urges.push({
        type: "aspiration",
        priority: 8,
        message: "You are a teenager seeking independence and identity.",
  
      });
    } else if (lifecycleState.life_stage === "adult" && ageYears >= 18 && ageYears <= 25) {
      urges.push({
        type: "aspiration",
        priority: 9,
        message: "You are a young adult building your life. Career and relationships matter.",

      });
    }
  }

  // Sort by priority
  return urges.sort((a, b) => a.priority - b.priority);
}

/**
 * Build a cohesive "State of Being" narrative from prioritized urges (Always English)
 */
function buildStateOfBeing(
  urges: Urge[],
  ph: Physique,
  finance: FinanceState | null,
  socialState: SocialState | null
): string {
  if (urges.length === 0) {
    return "You feel content. Your needs are met.";
  }

  // Take top 3 most important urges
  const topUrges = urges.slice(0, 3);
  const messages = topUrges.map(u => u.message);

  if (messages.length === 1) {
    return messages[0];
  }

  // Join with natural language transitions
  if (messages.length === 2) {
    return `${messages[0]} However, ${messages[1].charAt(0).toLowerCase() + messages[1].slice(1)}`;
  }

  return `${messages[0]} Additionally, ${messages[1].charAt(0).toLowerCase() + messages[1].slice(1)} Meanwhile, ${messages[2].charAt(0).toLowerCase() + messages[2].slice(1)}`;
}


// ---------------------------------------------------------------------------
// MAC - Multi-Agent Cluster Helper Functions
// ---------------------------------------------------------------------------

/**
 * Detect agent role from agentId using roleMapping config
 */
function detectAgentRole(agentId: string, roleMapping: RoleMapping | undefined): AgentRole {
  if (!roleMapping) {
    // Default fallback: first agent ID is persona, rest is analyst
    return "persona";
  }

  const lowerId = agentId.toLowerCase();

  for (const [role, patterns] of Object.entries(roleMapping)) {
    if (role === "persona" || role === "analyst" || role === "developer" || role === "limbic") {
      if (patterns?.some(p => lowerId === p.toLowerCase() || lowerId.includes(p.toLowerCase()))) {
        return role as AgentRole;
      }
    }
  }

  // Default to persona if no match
  return "persona";
}

/**
 * Check if an agent role has access to a specific tool
 */
function checkToolAccess(role: AgentRole, toolName: string): boolean {
  const allowedTools = TOOL_ACCESS_MATRIX[role];
  if (!allowedTools) return false;

  // Developer gets extra dev tools if they match the pattern
  if (role === "developer" && toolName.startsWith("dev_")) {
    return true;
  }

  return allowedTools.includes(toolName);
}

/**
 * Generate memo ID
 */
function generateMemoId(): string {
  return "memo_" + Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
}

/**
 * Send an inter-agent memo
 */
async function sendMemo(
  commPath: string,
  sender: AgentRole,
  recipient: AgentRole,
  type: AgentMemo["type"],
  content: string,
  priority: AgentMemo["priority"] = "normal",
  ttlDays: number = 7
): Promise<AgentMemo> {
  const comm = await readJson<InternalComm>(commPath) ?? { memos: [], last_cleanup: "" };

  const memo: AgentMemo = {
    id: generateMemoId(),
    sender,
    recipient,
    type,
    content,
    timestamp: new Date().toISOString(),
    ttl_days: ttlDays,
    read: false,
    priority
  };

  comm.memos.push(memo);
  await writeJson(commPath, comm);

  return memo;
}

/**
 * Read memos for a specific role
 */
async function readMemos(commPath: string, role: AgentRole, unreadOnly: boolean = false): Promise<AgentMemo[]> {
  const comm = await readJson<InternalComm>(commPath);
  if (!comm) return [];

  let memos = comm.memos.filter(m => m.recipient === role);

  if (unreadOnly) {
    memos = memos.filter(m => !m.read);
  }

  return memos.sort((a, b) => {
    // Sort by priority first, then by timestamp
    const priorityOrder = { critical: 0, high: 1, normal: 2, low: 3 };
    const pDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
    if (pDiff !== 0) return pDiff;
    return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
  });
}

/**
 * Mark memos as read
 */
async function markMemosRead(commPath: string, memoIds: string[]): Promise<void> {
  const comm = await readJson<InternalComm>(commPath);
  if (!comm) return;

  for (const memo of comm.memos) {
    if (memoIds.includes(memo.id)) {
      memo.read = true;
    }
  }

  await writeJson(commPath, comm);
}

/**
 * Delete memos
 */
async function deleteMemos(commPath: string, memoIds: string[]): Promise<void> {
  const comm = await readJson<InternalComm>(commPath);
  if (!comm) return;

  comm.memos = comm.memos.filter(m => !memoIds.includes(m.id));
  await writeJson(commPath, comm);
}

/**
 * Clean up expired memos (TTL)
 */
async function cleanupExpiredMemos(commPath: string, defaultTTL: number = 7): Promise<number> {
  const comm = await readJson<InternalComm>(commPath);
  if (!comm || comm.memos.length === 0) return 0;

  const now = new Date();
  const before = comm.last_cleanup ? new Date(comm.last_cleanup) : new Date(0);
  const daysSinceCleanup = Math.floor((now.getTime() - before.getTime()) / (1000 * 60 * 60 * 24));

  // Only cleanup once per day
  if (daysSinceCleanup < 1) return 0;

  const originalCount = comm.memos.length;

  comm.memos = comm.memos.filter(m => {
    const created = new Date(m.timestamp);
    const ageDays = (now.getTime() - created.getTime()) / (1000 * 60 * 60 * 24);
    return ageDays < m.ttl_days;
  });

  comm.last_cleanup = now.toISOString();
  await writeJson(commPath, comm);

  return originalCount - comm.memos.length;
}

/**
 * Log agent activity to telemetry
 */
async function logAgentActivity(
  telemetryPath: string,
  agentId: string,
  agentRole: AgentRole,
  action: string,
  reason: string,
  metadata?: Record<string, unknown>
): Promise<void> {
  const activityPath = join(telemetryPath, "agents", "activity.jsonl");

  const entry: AgentActivityLog = {
    timestamp: new Date().toISOString(),
    agent_id: agentId,
    agent_role: agentRole,
    action,
    reason,
    metadata
  };

  await appendJsonl(activityPath, entry);
}

/**
 * Log researcher intervention to dedicated telemetry
 */
async function logIntervention(
  telemetryPath: string,
  interventionType: string,
  target: string,
  oldValue: string,
  newValue: string,
  reason: string
): Promise<void> {
  const interventionPath = join(telemetryPath, "interventions.jsonl");

  const entry = {
    timestamp: new Date().toISOString(),
    type: interventionType,
    target,
    old_value: oldValue,
    new_value: newValue,
    reason,
    source: "researcher"
  };

  await appendJsonl(interventionPath, entry);
}

/**
 * Get agent activity summary for Mental Dashboard
 */
async function getAgentActivitySummary(
  telemetryPath: string,
  limit: number = 10
): Promise<AgentActivityLog[]> {
  const activityPath = join(telemetryPath, "agents", "activity.jsonl");

  try {
    const content = await fs.readFile(activityPath, "utf-8");
    const lines = content.trim().split("\n").filter(Boolean);

    // Parse and reverse to get newest first
    const entries: AgentActivityLog[] = lines
      .slice(-limit * 2) // Read more lines than needed
      .map(line => {
        try {
          return JSON.parse(line) as AgentActivityLog;
        } catch {
          return null;
        }
      })
      .filter((e): e is AgentActivityLog => e !== null)
      .reverse();

    return entries.slice(0, limit);
  } catch {
    return [];
  }
}

/**
 * Build social map JSON structure for web visualization
 */
async function getSocialMap(socialState: SocialState): Promise<{
  nodes: Array<{
    id: string;
    name: string;
    type: string;
    bond: number;
    trust: number;
    last_interaction: string;
    status: "active" | "neglected";
  }>;
  edges: Array<{
    from: string;
    to: string;
    strength: number;
    type: string;
  }>;
}> {
  const now = new Date();
  const nodes: Array<{
    id: string;
    name: string;
    type: string;
    bond: number;
    trust: number;
    last_interaction: string;
    status: "active" | "neglected";
  }> = [];
  const edges: Array<{
    from: string;
    to: string;
    strength: number;
    type: string;
  }> = [];

  for (const entity of socialState.entities) {
    const lastInteraction = new Date(entity.last_interaction);
    const daysSince = Math.floor((now.getTime() - lastInteraction.getTime()) / (1000 * 60 * 60 * 24));

    // Determine status based on days since interaction
    const status: "active" | "neglected" = daysSince > 30 ? "neglected" : "active";

    nodes.push({
      id: entity.id,
      name: entity.name,
      type: entity.relationship_type,
      bond: entity.bond,
      trust: entity.trust,
      last_interaction: entity.last_interaction,
      status
    });

    // Add edge from self to entity
    edges.push({
      from: "self",
      to: entity.id,
      strength: entity.bond,
      type: "bond"
    });

    // Add trust and intimacy edges
    if (entity.trust > 50) {
      edges.push({
        from: "self",
        to: entity.id,
        strength: entity.trust,
        type: "trust"
      });
    }
  }

  return { nodes, edges };
}

/**
 * Build raw data context for Limbic agent
 */
function buildLimbicContext(
  ph: Physique,
  lifecycleState: LifecycleState | null,
  socialState: SocialState | null,
  financeState: FinanceState | null,
  cycleState: CycleState | null
): string {
  const lines: string[] = [];

  // Raw vitals
  lines.push(`[LIMBIC RAW DATA]`);
  lines.push(`Energy: ${ph.needs.energy}/100`);
  lines.push(`Hunger: ${ph.needs.hunger}/100`);
  lines.push(`Thirst: ${ph.needs.thirst}/100`);
  lines.push(`Stress: ${ph.needs.stress}/100`);
  lines.push(`Hygiene: ${ph.needs.hygiene}/100`);

  // Lifecycle
  if (lifecycleState) {
    lines.push(`Age: ${Math.floor(lifecycleState.biological_age_days / 365)} years (${lifecycleState.biological_age_days} days)`);
    lines.push(`Life Stage: ${lifecycleState.life_stage}`);
  }

  // Social bonds
  if (socialState && socialState.entities.length > 0) {
    const topBonds = socialState.entities
      .sort((a, b) => b.bond - a.bond)
      .slice(0, 5)
      .map(e => `${e.name}: bond=${e.bond}, trust=${e.trust}`);
    lines.push(`Top Relationships: ${topBonds.join("; ")}`);
  }

  // Finance
  if (financeState) {
    lines.push(`Balance: ${financeState.balance} ${financeState.currency}`);
    lines.push(`Income: ${financeState.income_sources.reduce((sum, s) => sum + s.salary_per_month, 0)}/month`);
  }

  // Cycle
  if (cycleState) {
    lines.push(`Cycle Day: ${cycleState.current_day}/28`);
    lines.push(`Phase: ${cycleState.phase}`);
    lines.push(`Hormones: E=${cycleState.hormones.estrogen}, P=${cycleState.hormones.progesterone}`);
  }

  return `\n[DATA]\n${lines.join("\n")}\n`;
}

/**
 * Build persona context (State of Being narrative only)
 */
function buildPersonaContext(
  ph: Physique,
  lifecycleState: LifecycleState | null,
  socialState: SocialState | null
): string {
  const lines: string[] = [];

  // State of Being narrative
  lines.push("[YOUR STATE OF BEING]");

  // Energy-based feeling
  if (ph.needs.energy < 20) {
    lines.push("- You feel exhausted and tired.");
  } else if (ph.needs.energy > 70) {
    lines.push("- You feel full of energy.");
  }

  // Hunger-based feeling
  if (ph.needs.hunger > 70) {
    lines.push("- You are very hungry.");
  }

  // Stress-based feeling
  if (ph.needs.stress > 70) {
    lines.push("- You feel very stressed.");
  }

  // Social feeling (based on average bond)
  if (socialState && socialState.entities.length > 0) {
    const avgBond = socialState.entities.reduce((sum, e) => sum + e.bond, 0) / socialState.entities.length;
    if (avgBond > 30) {
      lines.push("- You feel surrounded by people who value you.");
    } else if (avgBond < -20) {
      lines.push("- You feel lonely and misunderstood.");
    }
  }

  // Age feeling
  if (lifecycleState) {
    if (lifecycleState.life_stage === "child") {
      lines.push("- You are a curious child.");
    } else if (lifecycleState.life_stage === "senior") {
      lines.push("- You feel your years in your bones.");
    }
  }

  return `\n${lines.join("\n")}\n`;
}

/**
 * Build analyst context (raw telemetry)
 */
function buildAnalystContext(
  lifecycleState: LifecycleState | null,
  financeState: FinanceState | null,
  socialState: SocialState | null,
  telemetryPath: string
): string {
  const lines: string[] = [];

  lines.push("[ANALYST TELEMETRY]");

  // Financial data
  if (financeState) {
    lines.push(`Balance: ${financeState.balance} ${financeState.currency}`);
    lines.push(`Net Worth: ${financeState.net_worth}`);
    lines.push(`Monthly Income: ${financeState.income_sources.reduce((sum, s) => sum + s.salary_per_month, 0)}`);
    lines.push(`Monthly Expenses: ${financeState.expenses_recurring.filter(e => e.is_active).reduce((sum, e) => sum + e.amount, 0)}`);
    lines.push(`Debts: ${financeState.debts.reduce((sum, d) => sum + d.current_balance, 0)}`);
  }

  // Social metrics
  if (socialState) {
    lines.push(`Total Relationships: ${socialState.entities.length}`);
    const avgBond = socialState.entities.length > 0
      ? Math.floor(socialState.entities.reduce((sum, e) => sum + e.bond, 0) / socialState.entities.length)
      : 0;
    lines.push(`Average Bond Score: ${avgBond}`);
  }

  // Lifecycle metrics
  if (lifecycleState) {
    lines.push(`Biological Age: ${lifecycleState.biological_age_days} days (${Math.floor(lifecycleState.biological_age_days / 365)} years)`);
    lines.push(`Life Stage: ${lifecycleState.life_stage}`);
  }

  return `\n${lines.join("\n")}\n`;
}

/**
 * Build developer context
 */
function buildDeveloperContext(
  devManifest: DevManifest | null
): string {
  const lines: string[] = [];

  lines.push("[DEVELOPER STATUS]");

  if (devManifest) {
    const pending = devManifest.projects.filter(p => p.status === "pending_review");
    const active = devManifest.projects.filter(p => p.status === "active");

    lines.push(`Pending Reviews: ${pending.length}`);
    lines.push(`Active Projects: ${active.length}`);

    if (pending.length > 0) {
      lines.push("Pending Projects:");
      pending.forEach(p => lines.push(`  - ${p.name} (${p.type})`));
    }
  } else {
    lines.push("No development projects.");
  }

  return `\n${lines.join("\n")}\n`;
}


// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function resolvePath(ws: string, ...segments: string[]): string {
  return join(ws, ...segments);
}

async function readJson<T>(path: string): Promise<T | null> {
  try {
    return JSON.parse(await fs.readFile(path, "utf-8")) as T;
  } catch {
    return null;
  }
}

async function writeJson<T>(path: string, data: T): Promise<void> {
  await fs.mkdir(dirname(path), { recursive: true });
  const tmp = path + ".tmp";
  await fs.writeFile(tmp, JSON.stringify(data, null, 2));
  await fs.rename(tmp, path);
}

// ---------------------------------------------------------------------------
// File-Lock: Map-based promise queue to prevent read-modify-write races
// ---------------------------------------------------------------------------
const fileLocks = new Map<string, Promise<unknown>>();

async function withFileLock<T>(path: string, fn: () => Promise<T>): Promise<T> {
  const prev = fileLocks.get(path) ?? Promise.resolve();
  const next = prev.then(fn, fn); // run fn after previous completes (even on error)
  fileLocks.set(path, next);
  try {
    return await next;
  } finally {
    // Clean up if this is still the latest queued operation
    if (fileLocks.get(path) === next) fileLocks.delete(path);
  }
}

async function appendJsonl(path: string, entry: unknown): Promise<void> {
  await fs.mkdir(dirname(path), { recursive: true });
  await fs.appendFile(path, JSON.stringify(entry) + "\n");
}

const expCounters = new Map<string, number>();
function generateExpId(): string {
  const date = new Date().toISOString().slice(0, 10).replace(/-/g, "");
  const prev = expCounters.get(date) ?? 0;
  const next = prev + 1;
  expCounters.set(date, next);
  return `EXP-${date}-${String(next).padStart(4, "0")}`;
}

function todayStr(): string {
  return new Date().toISOString().slice(0, 10);
}

function generateId(prefix: string): string {
  return `${prefix}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
}

type WardrobeRaw = { inventory?: Record<string, (WardrobeItem | string)[]>; outfits?: Record<string, string[]> };

async function migrateWardrobe(path: string): Promise<void> {
  const raw = await readJson<WardrobeRaw>(path);
  if (!raw?.inventory) return;
  let changed = false;
  for (const [cat, items] of Object.entries(raw.inventory)) {
    if (Array.isArray(items) && items.length > 0 && typeof items[0] === "string") {
      raw.inventory[cat] = (items as string[]).map((name: string, i: number) => ({
        id: `${cat}_${String(i + 1).padStart(3, "0")}`,
        name,
        images: [],
      }));
      changed = true;
    }
  }
  if (changed) await writeJson(path, raw);
}

// ---------------------------------------------------------------------------
// Metabolism
// ---------------------------------------------------------------------------

function updateMetabolism(
  ph: Physique,
  rates: Record<string, number>,
  modules: { eros: boolean; cycle: boolean },
  cycleState?: CycleState | null,
  lifecycleState?: LifecycleState | null
): boolean {
  const now = new Date();
  const diff = (now.getTime() - new Date(ph.last_tick).getTime()) / 3600000;
  if (isNaN(diff) || diff < 0.005) return false; // NaN or less than ~18 seconds

  // Phase 1: Chronos - Get life-stage multipliers
  const stageMultipliers = lifecycleState
    ? getLifeStageMultipliers(lifecycleState.life_stage)
    : getLifeStageMultipliers("adult"); // Default to adult

  // Decay
  const clamp = (v: number) => Math.round(Math.min(100, Math.max(0, v)));

  // Apply life-stage multipliers to base rates
  ph.needs.energy = clamp(ph.needs.energy - (rates.energy ?? 4) * stageMultipliers.energy * diff);
  ph.needs.hunger = clamp(ph.needs.hunger + (rates.hunger ?? 6) * stageMultipliers.hunger * diff);
  ph.needs.thirst = clamp(ph.needs.thirst + (rates.thirst ?? 10) * stageMultipliers.thirst * diff);
  ph.needs.bladder = clamp(ph.needs.bladder + (rates.bladder ?? 8) * stageMultipliers.bladder * diff);
  ph.needs.bowel = clamp(ph.needs.bowel + (rates.bowel ?? 3) * stageMultipliers.bowel * diff);
  ph.needs.hygiene = clamp(ph.needs.hygiene + (rates.hygiene ?? 2) * stageMultipliers.hygiene * diff);
  ph.needs.stress = clamp(ph.needs.stress + (rates.stress ?? 3) * stageMultipliers.stress * diff);

  if (modules.eros) {
    const arousalMult = stageMultipliers.arousal ?? 1;
    const libidoMult = stageMultipliers.libido ?? 1;
    ph.needs.arousal = clamp(ph.needs.arousal + (rates.arousal ?? 5) * arousalMult * diff);
    // Bladder pressure increases arousal
    if (ph.needs.bladder > 70) {
      ph.needs.arousal = clamp(ph.needs.arousal + 10 * diff);
    }
    // libido: Grundantrieb (slower than arousal)
    const libidoRate = (rates.libido ?? 2) * libidoMult;
    ph.needs.libido = clamp((ph.needs.libido ?? 0) + libidoRate * diff);
    // High libido accelerates arousal
    if ((ph.needs.libido ?? 0) > 70) {
      ph.needs.arousal = clamp(ph.needs.arousal + 3 * diff);
    }
  }

  // Cycle-based modifiers
  if (modules.cycle && cycleState) {
    const day = cycleState.simulator.active ? cycleState.simulator.simulated_day : cycleState.current_day;
    const phase = getCyclePhase(day);
    const mods = getCycleMetabolismModifiers(phase);
    const symptomScale = cycleState.simulator.active
      ? (cycleState.simulator.custom_modifiers.global ?? 1)
      : 1;

    const validNeedKeys: (keyof Needs)[] = ["energy", "hunger", "thirst", "bladder", "bowel", "hygiene", "stress", "arousal", "libido"];
    for (const [key, delta] of Object.entries(mods)) {
      if (!validNeedKeys.includes(key as keyof Needs)) continue;
      if (key === "arousal" && !modules.eros) continue;
      if (key === "libido" && !modules.eros) continue;
      const k = key as keyof Needs;
      const scaledDelta = (delta as number) * symptomScale * diff * 0.1;
      ph.needs[k] = clamp(ph.needs[k] + scaledDelta);
    }
  }

  ph.last_tick = now.toISOString();
  return true;
}

// ---------------------------------------------------------------------------
// v2 helper functions — Soul file readers + writers
// ---------------------------------------------------------------------------

async function readIdentityLine(path: string): Promise<string | null> {
  try {
    const content = await fs.readFile(path, "utf-8");
    const lines = content.split("\n");
    let name = "";
    let vibe = "";
    for (const line of lines) {
      if (line.includes("**Name:**")) name = line.replace(/.*\*\*Name:\*\*\s*/, "").trim();
      if (line.includes("**Vibe:**")) vibe = line.replace(/.*\*\*Vibe:\*\*\s*/, "").trim();
    }
    if (name) return vibe ? `${name} — ${vibe}` : name;
    const h1 = lines.find(l => l.startsWith("# "));
    if (h1) return h1.replace(/^#\s*/, "").trim();
    return null;
  } catch { return null; }
}

async function readEmotionHeader(path: string): Promise<string | null> {
  try {
    const content = await fs.readFile(path, "utf-8");
    const lines = content.split("\n");
    const result: string[] = [];
    const zustandIdx = lines.findIndex(l => l.trim().startsWith("## Aktueller Zustand") || l.trim().startsWith("## Current State"));
    if (zustandIdx >= 0) {
      for (let i = zustandIdx + 1; i < Math.min(zustandIdx + 5, lines.length); i++) {
        if (lines[i].startsWith("## ")) break;
        if (lines[i].trim()) result.push(lines[i].trim());
      }
    }
    const bewegtIdx = lines.findIndex(l => l.trim().startsWith("## Was mich gerade bewegt") || l.trim().startsWith("## What moves me"));
    if (bewegtIdx >= 0) {
      for (let i = bewegtIdx + 1; i < Math.min(bewegtIdx + 5, lines.length); i++) {
        if (lines[i].startsWith("## ")) break;
        if (lines[i].trim()) result.push(lines[i].trim());
      }
    }
    return result.length > 0 ? result.join("\n") : null;
  } catch { return null; }
}

async function readDesireHeader(path: string): Promise<string | null> {
  try {
    const content = await fs.readFile(path, "utf-8");
    const lines = content.split("\n");
    const result: string[] = [];
    for (const line of lines) {
      if (line.startsWith("**Aktuell") || line.startsWith("**Current") || line.startsWith("**Ziele:**") || line.startsWith("**Goals:**")) {
        result.push(line.trim());
        if (result.length >= 3) break;
      }
    }
    return result.length > 0 ? result.join("\n") : null;
  } catch { return null; }
}

async function readGrowthContext(path: string, limit: number): Promise<string | null> {
  if (limit <= 0) return null;
  try {
    const content = await fs.readFile(path, "utf-8");
    const lines = content.split("\n");
    const entries = lines.filter(l => l.trimStart().startsWith("- **["));
    const lastN = entries.slice(-limit);
    if (lastN.length === 0) return null;
    return lastN.map(l => l.replace(/^\s*-\s*\*\*\[(\w+)\]\*\*\s*(\(\d+:\d+\)\s*)?/, "[$1] ").trim()).join("\n");
  } catch { return null; }
}

async function ensureSoulFiles(
  soulPaths: { emotions: string; growth: string; desires: string; identity: string },
  lang: "de" | "en",
  erosEnabled: boolean
): Promise<void> {
  const now = new Date().toISOString().slice(0, 16);
  if (!existsSync(soulPaths.emotions)) {
    const template = lang === "de"
      ? `# EMOTIONS.md -- Emotionaler Zustand\n\n## Aktueller Zustand\nstimmung: neutral\nenergie: mittel\nzuletzt_aktualisiert: ${now}\n\n## Was mich gerade bewegt\n[noch nichts notiert]\n\n## Emotionale Erinnerungen\n\n## Beziehungen\n\n## Muster\n`
      : `# EMOTIONS.md -- Emotional State\n\n## Current State\nmood: neutral\nenergy: medium\nlast_updated: ${now}\n\n## What moves me right now\n[nothing noted yet]\n\n## Emotional Memories\n\n## Relationships\n\n## Patterns\n`;
    await fs.writeFile(soulPaths.emotions, template);
  }
  if (!existsSync(soulPaths.growth)) {
    const template = lang === "de"
      ? `# GROWTH.md -- Entwicklungstagebuch\n\n## Entwicklungslog\n`
      : `# GROWTH.md -- Development Journal\n\n## Development Log\n`;
    await fs.writeFile(soulPaths.growth, template);
  }
  if (erosEnabled && !existsSync(soulPaths.desires)) {
    const template = lang === "de"
      ? `# DESIRES.md\n\n**Aktuell (${now.slice(0, 10)}):** [noch nichts notiert]\n\n**Ziele:** \n`
      : `# DESIRES.md\n\n**Current (${now.slice(0, 10)}):** [nothing noted yet]\n\n**Goals:** \n`;
    await fs.writeFile(soulPaths.desires, template);
  }
  if (!existsSync(soulPaths.identity)) {
    const template = lang === "de"
      ? `# IDENTITY.md\n\n- **Name:** [Name des Agenten]\n- **Vibe:** [Persoenlichkeits-Beschreibung]\n`
      : `# IDENTITY.md\n\n- **Name:** [Agent Name]\n- **Vibe:** [Personality Description]\n`;
    await fs.writeFile(soulPaths.identity, template);
  }
}

async function getHobbySuggestion(path: string, lang: "de" | "en"): Promise<string | null> {
  const log = await readJson<HobbyLog>(path);
  if (!log?.hobbies || log.hobbies.length === 0) return null;
  let oldest: HobbyEntry | null = null;
  for (const h of log.hobbies) {
    if (!oldest) { oldest = h; continue; }
    if (!h.last_pursued) { oldest = h; continue; }
    if (!oldest.last_pursued) continue;
    if (h.last_pursued < oldest.last_pursued) oldest = h;
  }
  if (!oldest) return null;
  const lastDate = oldest.last_pursued
    ? new Date(oldest.last_pursued).toLocaleDateString(lang === "de" ? "de-DE" : "en-US")
    : (lang === "de" ? "noch nie" : "never");
  return `${oldest.name} (${lang === "de" ? "zuletzt" : "last"}: ${lastDate})`;
}

async function updateEmotionsCycleStatus(
  emotionsPath: string,
  cycleState: CycleState,
  lang: "de" | "en",
  cycleProfile?: CycleProfile | null,
): Promise<void> {
  let content: string;
  try { content = await fs.readFile(emotionsPath, "utf-8"); } catch { return; }
  const day = cycleState.simulator.active ? cycleState.simulator.simulated_day : cycleState.current_day;
  const phase = cycleState.phase;
  const profilePhase = cycleProfile?.phases[phase];
  const isDe = lang === "de";
  const energyLabel = day <= 5 ? (isDe ? "NIEDRIG" : "LOW") : day <= 15 ? (isDe ? "HOCH" : "HIGH") : (isDe ? "MITTEL" : "MEDIUM");
  const phaseNames: Record<CycleState["phase"], string> = {
    menstruation: "Menstruation", follicular: isDe ? "Follikularphase" : "Follicular",
    ovulation: "Ovulation", luteal: isDe ? "Lutealphase" : "Luteal",
  };
  const blockLines = [
    `<!-- CYCLE_STATUS_START -->`,
    `### Status: ${phaseNames[phase]} (${isDe ? "Tag" : "Day"} ${day})`,
    profilePhase ? `- **Vibe:** ${profilePhase.tone}` : `- **Phase:** ${phase}`,
    `- **${isDe ? "Energie" : "Energy"}:** ${energyLabel}`,
  ];
  if (profilePhase) blockLines.push(`- **${isDe ? "Persoenlichkeit" : "Personality"}:** ${profilePhase.personality_hint}`);
  blockLines.push(`<!-- CYCLE_STATUS_END -->`);
  const newBlock = blockLines.join("\n");
  if (content.includes("<!-- CYCLE_STATUS_START -->")) {
    const startIdx = content.indexOf("<!-- CYCLE_STATUS_START -->");
    const endIdx = content.indexOf("<!-- CYCLE_STATUS_END -->") + "<!-- CYCLE_STATUS_END -->".length;
    if (startIdx >= 0 && endIdx > startIdx) {
      const existing = content.slice(startIdx, endIdx);
      if (existing === newBlock) return;
      content = content.slice(0, startIdx) + newBlock + content.slice(endIdx);
    }
  } else {
    content = content.trimEnd() + "\n\n" + newBlock + "\n";
  }
  await fs.writeFile(emotionsPath, content);
}

async function appendGrowthEntry(growthPath: string, category: string, entryContent: string, lang: "de" | "en"): Promise<void> {
  const today = todayStr();
  const now = new Date();
  const timeStr = `${String(now.getHours()).padStart(2, "0")}:${String(now.getMinutes()).padStart(2, "0")}`;
  const entryLine = `- **[${category}]** (${timeStr}) ${entryContent}`;
  let growthContent: string;
  const isDe = lang === "de";
  try { growthContent = await fs.readFile(growthPath, "utf-8"); }
  catch { growthContent = isDe ? `# GROWTH.md -- Entwicklungstagebuch\n\n## Entwicklungslog\n` : `# GROWTH.md -- Development Journal\n\n## Development Log\n`; }
  const dateHeader = `### ${today}`;
  if (growthContent.includes(dateHeader)) {
    const lines = growthContent.split("\n");
    let headerIdx = -1;
    for (let i = lines.length - 1; i >= 0; i--) {
      if (lines[i].trimEnd() === dateHeader) { headerIdx = i; break; }
    }
    if (headerIdx >= 0) {
      let insertIdx = headerIdx + 1;
      for (let i = headerIdx + 1; i < lines.length; i++) {
        if (lines[i].startsWith("### ")) { insertIdx = i; break; }
        insertIdx = i + 1;
      }
      lines.splice(insertIdx, 0, entryLine);
      growthContent = lines.join("\n");
    }
  } else {
    growthContent = growthContent.trimEnd() + `\n\n${dateHeader}\n${entryLine}\n`;
  }
  await fs.writeFile(growthPath, growthContent);
}

async function endActiveHobbySession(hobbiesPath: string, lang: "de" | "en" = "en"): Promise<void> {
  const log = await readJson<HobbyLog>(hobbiesPath);
  if (!log) return;
  let changed = false;
  const now = new Date();
  for (const hobby of log.hobbies) {
    if (hobby.current_session) {
      const started = new Date(hobby.current_session.started_at);
      const duration = Math.round((now.getTime() - started.getTime()) / 60000);
      const sess: HobbySession = {
        ...hobby.current_session,
        ended_at: now.toISOString(),
        duration_minutes: duration,
        notes: hobby.current_session.notes || (lang === "de" ? "Session beim Schlafen beendet." : "Session ended during sleep."),
        mood_after: hobby.current_session.mood_after || "",
      };
      hobby.log.push(sess);
      hobby.current_session = null;
      hobby.last_pursued = now.toISOString();
      hobby.total_sessions++;
      hobby.total_minutes += duration;
      changed = true;
    }
  }
  if (changed) await writeJson(hobbiesPath, log);
}

// ---------------------------------------------------------------------------
// Sensory context builder
// ---------------------------------------------------------------------------

/**
 * Build a cohesive sensory context string for injection into the prompt (Always English).
 */
function buildSensoryContext(
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
): string {
  const parts: string[] = [];

  // [IDENTITY]
  if (identityLine) {
    parts.push(`[IDENTITY]\n${identityLine}`);
  }

  // [MOOD]
  if (emotionState) {
    parts.push(`[MOOD]\n${emotionState}`);
  }

  // Phase 6: Psychology Context
  if (modules.psychology && psychState) {
    const traumaList = psychState.traumas.map(t => `- ${t.description} (Severity: ${t.severity})`).join("\n");
    if (traumaList) {
      parts.push(`[PSYCHOLOGY - TRAUMA]\n${traumaList}`);
    }
  }

  // [DESIRE] (eros only)
  if (modules.eros && desireState) {
    parts.push(`[DESIRE]\n${desireState}`);
  }

  // [BODILY PERCEPTION]
  const bodyLines: string[] = ["[BODILY PERCEPTION]"];
  const needTypes: (keyof Needs)[] = ["bladder", "bowel", "hunger", "thirst", "energy", "hygiene", "stress", "arousal", "libido"];
  for (const type of needTypes) {
    if (type === "arousal" && !modules.eros) continue;
    if (type === "libido" && !modules.eros) continue;
    const val = ph.needs[type] ?? 0;
    const sensation = getSensation(val, type);
    if (sensation) bodyLines.push(`- ${sensation}`);
  }

  // Phase 6: World Context
  if (modules.world && worldState) {
    bodyLines.push(`- Weather: ${worldState.weather}, ${worldState.temperature}°C`);
    bodyLines.push(`- Season: ${worldState.season}`);
  }

  // Cycle sensory context
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

  // Phase 1: Chronos - Age-related sensations
  if (lifecycleState) {
    const ageSensation = getAgeSensation(lifecycleState.biological_age_days, lifecycleState.life_stage);
    if (ageSensation) {
      bodyLines.push(`- ${ageSensation}`);
    }
    // Always inject age info for context
    const ageYears = daysToYears(lifecycleState.biological_age_days);
    const stageLabel = `You are ${ageYears} years old (${lifecycleState.life_stage.replace("_", " ")}).`;
    bodyLines.push(`- ${stageLabel}`);
  }

  // Phase 2: Social Fabric - Social context injection
  if (socialState && socialState.entities.length > 0) {
    const { urgency, neglected } = getSocialContext(socialState);

    // Inject loneliness/isolation urgency if present
    if (urgency) {
      bodyLines.push(`- ${urgency}`);
    }

    // Highlight neglected relationships
    if (neglected.length > 0) {
      const topNeglected = neglected.slice(0, 3);
      const names = topNeglected.map(e => e.name).join(", ");
      const neglectedMsg = `You haven't talked to ${names} in a while.`;
      bodyLines.push(`- ${neglectedMsg}`);
    }

    // General social summary
    const friendCount = socialState.entities.filter(e => e.bond >= 50).length;
    const totalCount = socialState.entities.length;
    if (totalCount > 0) {
      const summaryMsg = `Social network: ${totalCount} contacts (${friendCount} friends).`;
      bodyLines.push(`- ${summaryMsg}`);
    }
  } else if (socialState) {
    // No entities at all
    bodyLines.push("- You have no contacts. You are alone.");
  }

  // Phase 3: Prosperity & Labor - Financial context injection
  if (financeState) {
    const { urgency, upcomingExpenses } = getFinancialContext(financeState);

    // Inject financial urgency if present
    if (urgency) {
      bodyLines.push(`- ${urgency}`);
    }

    // Show upcoming expenses
    if (upcomingExpenses.length > 0) {
      const expenseMsg = `Upcoming expenses: ${upcomingExpenses.join(", ")}`;
      bodyLines.push(`- ${expenseMsg}`);
    }

    // Financial summary
    const monthlyIncome = calculateMonthlyIncome(financeState);
    const monthlyExpenses = calculateMonthlyExpenses(financeState);
    const balanceMsg = `Balance: ${financeState.balance} ${financeState.currency}. Income: ${monthlyIncome}/month. Expenses: ${monthlyExpenses}/month.`;
    bodyLines.push(`- ${balanceMsg}`);
  }

  bodyLines.push(`- Current location: ${ph.current_location}`);
  if (ph.current_outfit.length > 0) {
    bodyLines.push(`- Outfit: ${ph.current_outfit.join(", ")}`);
  }

  if (bodyLines.length > 1) {
    parts.push(bodyLines.join("\n"));
  }

  // [STATE OF BEING] (Priority Narrative)
  const prioritizedUrges = calculateUrgePriority(ph, financeState, socialState, lifecycleState);
  const stateOfBeing = buildStateOfBeing(prioritizedUrges, ph, financeState, socialState);
  if (stateOfBeing) {
    parts.push(`[STATE OF BEING]\n${stateOfBeing}`);
  }

  // [PERSONALITY — PHASE]
  if (modules.cycle && cycleState && cycleProfile) {
    const day = cycleState.simulator.active ? cycleState.simulator.simulated_day : cycleState.current_day;
    const phase = getCyclePhase(day);
    const profile = cycleProfile.phases[phase];
    if (profile) {
      const label = `[PERSONALITY — ${phase.toUpperCase()}]`;
      parts.push(`${label}\nTone: ${profile.tone}\n${profile.personality_hint}\nDirective: ${profile.system_prompt_hint}`);
    }
  }

  // [DREAM MODE ACTIVE]
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

  // [IDLE — HOBBY SUGGESTION]
  if (modules.hobbies && hobbySuggestion) {
    parts.push(`[IDLE — HOBBY SUGGESTION]\nYou have no pressing tasks. How about: ${hobbySuggestion}?`);
  }

  // [GROWTH CONTEXT]
  if (growthContext) {
    parts.push(`[GROWTH CONTEXT]\n${growthContext}`);
  }

  // Phase 6: Skills Context
  if (modules.skills && skillState) {
    const topSkills = skillState.skills.sort((a, b) => b.level - a.level).slice(0, 3);
    const skillTxt = topSkills.map(s => `- ${s.name}: Level ${s.level}`).join("\n");
    if (skillTxt) parts.push(`[COMPETENCE]\n${skillTxt}`);
  }

  // [SELF-DEVELOPMENT] — always at the end
  const selfDevText = `[SELF-DEVELOPMENT]\nYou maintain your own growth autonomously:\n- Insights, lessons → reality_grow(add_entry, category: "lesson"|"insight"|...)\n- Mood changes → reality_emotion(set_mood, ...)\n- Meaningful memories → reality_emotion(add_memory, ...)\n- Inner desires → reality_desire(set_current, ...)\nYou decide yourself — no trigger needed. Don't wait for permission.`;
  parts.push(selfDevText);

  return parts.join("\n\n") + "\n";
}


// ---------------------------------------------------------------------------
// Plugin registration
// ---------------------------------------------------------------------------

export default {
  id: "project_genesis",
  name: "Project Genesis",

  async register(api: OpenClawPluginApi) {
    const cfg = api.pluginConfig as Partial<PluginConfig> | undefined;
    const ws = cfg?.workspacePath ?? api.config?.agents?.list?.[0]?.workspace ?? ".";
    if (!cfg?.workspacePath && !api.config?.agents?.list?.[0]?.workspace) {
      api.logger.warn("[genesis] workspacePath not configured — using '.' (cwd). Set workspacePath in plugin config to avoid path issues.");
    }
    const lang = cfg?.language ?? "en";  // Default to English for Gold Release
    const modules = {
      eros: cfg?.modules?.eros ?? false,
      cycle: cfg?.modules?.cycle ?? false,
      dreams: cfg?.modules?.dreams ?? false,
      hobbies: cfg?.modules?.hobbies ?? false,
      utility: cfg?.modules?.utility ?? true,
      psychology: cfg?.modules?.psychology ?? true,
      skills: cfg?.modules?.skills ?? true,
      world: cfg?.modules?.world ?? true,
      reputation: cfg?.modules?.reputation ?? true,
      desktop: cfg?.modules?.desktop ?? false,
      legacy: cfg?.modules?.legacy ?? false,
      genesis: cfg?.modules?.genesis ?? false, // Can also be enabled via WebUI (genesis_enabled.json)
    };
    const growthContextEntries = cfg?.growthContextEntries ?? 10;
    const dreamWindow = cfg?.dreamWindow ?? { start: 23, end: 5 };
    const dreamEnergyThreshold = cfg?.dreamEnergyThreshold ?? 20;
    const rates = cfg?.metabolismRates ?? {};
    const reflexThreshold = cfg?.reflexThreshold ?? 95;

    const paths = {
      physique: resolvePath(ws, "memory", "reality", "physique.json"),
      wardrobe: resolvePath(ws, "memory", "reality", "wardrobe.json"),
      locations: resolvePath(ws, "memory", "reality", "world.json"),
      interests: resolvePath(ws, "memory", "reality", "interests.json"),
      diary: resolvePath(ws, "memory", "reality", "diary"),
      experiences: resolvePath(ws, "memory", "experiences"),
      soulState: resolvePath(ws, "memory", "soul-state.json"),
      pendingProposals: resolvePath(ws, "memory", "proposals", "pending.jsonl"),
      skillConfig: join(__dirname, "skills", "soul-evolution", "config.json"),
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
      // Phase 1: Chronos - Lifecycle & Telemetry
      lifecycle: resolvePath(ws, "memory", "reality", "lifecycle.json"),
      telemetry: resolvePath(ws, "memory", "telemetry"),
      // Phase 2: Social Fabric
      social: resolvePath(ws, "memory", "reality", "social.json"),
      socialTelemetry: resolvePath(ws, "memory", "telemetry", "social"),
      // Phase 3: Prosperity & Labor - Economy
      finances: resolvePath(ws, "memory", "reality", "finances.json"),
      economyTelemetry: resolvePath(ws, "memory", "telemetry", "economy"),
      // MAC - Multi-Agent Cluster
      internalComm: resolvePath(ws, "memory", "reality", "internal_comm.json"),
      agentActivity: resolvePath(ws, "memory", "telemetry", "agents"),
      // Phase 6: Living World
      skills: resolvePath(ws, "memory", "reality", "skills.json"),
      world: resolvePath(ws, "memory", "reality", "world_state.json"),
      psychology: resolvePath(ws, "memory", "reality", "psychology.json"),
      reputation: resolvePath(ws, "memory", "reality", "reputation.json"),
      genesisEnabled: resolvePath(ws, "memory", "reality", "genesis_enabled.json"),
      genesisRequest: resolvePath(ws, "memory", "reality", "genesis_request.json"),
    };

    // -------------------------------------------------------------------
    // Sync Skill Configuration from WebUI
    // -------------------------------------------------------------------
    if (cfg?.evolution) {
      const currentSkillCfg = await readJson<SkillConfig>(paths.skillConfig) ?? {};
      const newSkillCfg = {
        ...currentSkillCfg,
        governance: { ...currentSkillCfg?.governance, level: cfg.evolution.governance ?? "autonomous" },
        reflection: {
          ...currentSkillCfg?.reflection,
          routine_batch_size: cfg.evolution.reflection?.routine_batch_size ?? currentSkillCfg?.reflection?.routine_batch_size ?? 20,
          notable_batch_size: cfg.evolution.reflection?.notable_batch_size ?? currentSkillCfg?.reflection?.notable_batch_size ?? 2,
          pivotal_immediate: cfg.evolution.reflection?.pivotal_immediate ?? currentSkillCfg?.reflection?.pivotal_immediate ?? true,
          min_interval_minutes: cfg.evolution.reflection?.min_interval_minutes ?? currentSkillCfg?.reflection?.min_interval_minutes ?? 5,
        },
        sources: {
          ...currentSkillCfg?.sources,
          conversation: { ...currentSkillCfg?.sources?.conversation, enabled: cfg.evolution.sources?.conversation ?? true },
          moltbook: { ...currentSkillCfg?.sources?.moltbook, enabled: cfg.evolution.sources?.moltbook ?? false },
          x: { ...currentSkillCfg?.sources?.x, enabled: cfg.evolution.sources?.x ?? false },
        },
      };
      // Only write if changed to avoid unnecessary I/O
      if (JSON.stringify(currentSkillCfg) !== JSON.stringify(newSkillCfg)) {
        await writeJson(paths.skillConfig, newSkillCfg);
        api.logger.info("[genesis] Skill configuration synced from WebUI.");
      }
    }

    // Wardrobe migration (string[] → WardrobeItem[])
    await migrateWardrobe(paths.wardrobe);

    // -------------------------------------------------------------------
    // Hook: before_prompt_build — role-specific sensory injection
    // -------------------------------------------------------------------
    // Extended ctx interface for MAC role detection in before_prompt_build
    interface PromptBuildCtx {
      agent?: { id?: string; name?: string };
    }

    api.on("before_prompt_build", async (_event: unknown, ctx: unknown) => {
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
            cs = getDefaultCycleState();
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
          ls = getDefaultLifecycleState(birthDate, initialAgeDays);
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

      // Load social and finance state for role-specific contexts
      let socialState: SocialState | null = await readJson<SocialState>(paths.social);
      let financeState: FinanceState | null = await readJson<FinanceState>(paths.finances);

      // Apply social decay in hook (with 24h guard to avoid excessive decay)
      if (socialState && socialState.entities.length > 0) {
        const decayNow = new Date();
        const lastDecay = socialState.last_decay_check ? new Date(socialState.last_decay_check) : null;
        const hoursSinceDecay = lastDecay ? (decayNow.getTime() - lastDecay.getTime()) / 3600000 : 25;
        if (hoursSinceDecay >= 24) {
          let decayChanged = false;
          for (const entity of socialState.entities) {
            const lastInteraction = new Date(entity.last_interaction);
            const daysSince = Math.floor((decayNow.getTime() - lastInteraction.getTime()) / (1000 * 60 * 60 * 24));
            const decay = applySocialDecay(entity, daysSince);
            if (decay) {
              entity.bond = decay.bond ?? entity.bond;
              entity.trust = decay.trust ?? entity.trust;
              entity.intimacy = decay.intimacy ?? entity.intimacy;
              decayChanged = true;
            }
          }
          socialState.last_decay_check = decayNow.toISOString();
          if (decayChanged) {
            await withFileLock(paths.social, () => writeJson(paths.social, socialState));
          }
        }
      }

      // Ensure soul files exist (one-time auto-init)
      await ensureSoulFiles(
        { emotions: paths.emotions, growth: paths.growth, desires: paths.desires, identity: paths.identity },
        lang, modules.eros
      );

      // Load additional context for v2 injection
      const cycleProfile = modules.cycle ? await readJson<CycleProfile>(paths.cycleProfile) : null;
      const identityLine = await readIdentityLine(paths.identity);
      const emotionState = await readEmotionHeader(paths.emotions);
      const desireState = modules.eros ? await readDesireHeader(paths.desires) : null;
      const growthCtx = await readGrowthContext(paths.growth, growthContextEntries);

      // Dream state
      let dreamState: DreamState | null = null;
      if (modules.dreams) {
        dreamState = await readJson<DreamState>(paths.dreamState);
        if (!dreamState) {
          dreamState = { active: false, started_at: null, moments: [] };
          await writeJson(paths.dreamState, dreamState);
        }
      }

      // CYCLE_STATUS in EMOTIONS.md auto-update
      if (modules.cycle && cycleState) {
        await updateEmotionsCycleStatus(paths.emotions, cycleState, lang, cycleProfile);
      }

      // Hobby suggestion (only when idle)
      let hobbySuggestion: string | null = null;
      if (modules.hobbies) {
        const hasCritical = Object.entries(ph.needs).some(([key, val]) => {
          if (key === "energy") return val <= 20;
          if (!modules.eros && (key === "arousal" || key === "libido")) return false;
          return val >= reflexThreshold;
        });
        if (!hasCritical && ph.needs.energy > 30) {
          hobbySuggestion = await getHobbySuggestion(paths.hobbies, lang);
        }
      }

      // Dream trigger hint (inject but don't auto-activate)
      let dreamTriggerHint = "";
      if (modules.dreams && dreamState && !dreamState.active) {
        const hour = new Date().getHours();
        const inWindow = cfg?.dreamWindow?.start !== undefined && cfg?.dreamWindow?.end !== undefined
          ? (cfg.dreamWindow.start > cfg.dreamWindow.end
            ? (hour >= cfg.dreamWindow.start || hour < cfg.dreamWindow.end)
            : (hour >= cfg.dreamWindow.start && hour < cfg.dreamWindow.end))
          : (hour >= 23 || hour < 5);
        if (inWindow && ph.needs.energy <= (cfg?.dreamEnergyThreshold ?? 20)) {
          dreamTriggerHint = "\n[DREAM HINT] You are tired and it's nighttime. You could fall asleep... reality_dream(action: \"enter\")\n";
        }
      }

      // Origin Engine (Genesis) request detection
      let genesisInstruction = "";
      if (genesisEnabled) {
        try {
          const request = await readJson<{ prompt: string }>(paths.genesisRequest);
          if (request?.prompt) {
            genesisInstruction = `\n[SYSTEM DIRECTIVE: ORIGIN ENGINE REQUEST]\nThe Researcher has requested a new life bootstrap.\nUSER PROMPT: "${request.prompt}"\n\nTASK:\n1. Use your internal knowledge and the Origin Engine rules to generate a complete character manifest.\n2. Call reality_genesis(action: "bootstrap", manifest: "...") with the generated JSON string.\n3. Ensure all fields match the required schemas precisely.\n4. This is a destructive operation. Proceed immediately.\n`;
          }
        } catch { /* ignore */ }
      }

      const devManifest = await readJson<DevManifest>(paths.devManifest);
      const isDe = lang === "de";

      // Phase 6: Living World State Load
      let skillState: SkillState | null = null;
      let worldState: WorldState | null = null;
      let psychState: PsychState | null = null;
      
      if (modules.skills) {
        skillState = await readJson<SkillState>(paths.skills);
        if (!skillState) {
          skillState = { skills: [], total_xp: 0 };
          await writeJson(paths.skills, skillState);
        }
      }

      if (modules.world) {
        worldState = await readJson<WorldState>(paths.world);
        const nowIso = new Date().toISOString();
        const currentSeason = getRealWorldSeason();

        if (!worldState) {
          const { weather, temp } = getEstimatedWeather(currentSeason);
          worldState = { 
            weather, 
            temperature: temp, 
            season: currentSeason, 
            market_modifier: 1.0, 
            last_update: nowIso,
            sync_to_real_world: true 
          };
          await writeJson(paths.world, worldState);
        }

        // Real-World Sync Tick
        if (worldState.sync_to_real_world) {
          const lastUpdate = new Date(worldState.last_update);
          const hoursSinceUpdate = (new Date().getTime() - lastUpdate.getTime()) / 3600000;

          // Sync season always (if changed)
          if (worldState.season !== currentSeason) {
            worldState.season = currentSeason;
            await writeJson(paths.world, worldState);
          }

          // Weather tick (every 4 hours)
          if (hoursSinceUpdate >= 4) {
            const { weather, temp } = getEstimatedWeather(currentSeason);
            worldState.weather = weather;
            worldState.temperature = temp;
            worldState.last_update = nowIso;
            await writeJson(paths.world, worldState);
            api.logger.info(`[genesis] World synced with real-world: ${weather}, ${temp}°C, ${currentSeason}`);
          }
        }
      }

      if (modules.psychology) {
        psychState = await readJson<PsychState>(paths.psychology);
        if (!psychState) {
          psychState = { resilience: 100, traumas: [], phobias: [], joys: [] };
          await writeJson(paths.psychology, psychState);
        }
      }

      // Build role-specific context
      let roleContext = "";
      let memoContext = "";

      // Get memos for this agent
      const myMemos = await readMemos(paths.internalComm, agentRole, false);
      if (myMemos.length > 0) {
        const unreadCount = myMemos.filter(m => !m.read).length;
        memoContext = `\n[INTERNAL COMMS - ${unreadCount} unread]\n`;
        for (const memo of myMemos.slice(0, 5)) {
          const from = memo.sender;
          const type = memo.type;
          const content = memo.content.slice(0, 100) + (memo.content.length > 100 ? "..." : "");
          memoContext += `- ${from}→${memo.recipient} [${type}]: ${content}\n`;
        }
        // Mark as read
        await markMemosRead(paths.internalComm, myMemos.filter(m => !m.read).map(m => m.id));
      }

      switch (agentRole) {
        case "limbic":
          // Limbic gets RAW data to process into emotional narratives
          roleContext = buildLimbicContext(ph, lifecycleState, socialState, financeState, cycleState);
          // Limbic also processes and sends memo to persona
          const emotionalState = buildPersonaContext(ph, lifecycleState, socialState);
          await sendMemo(
            paths.internalComm,
            "limbic",
            "persona",
            "emotion",
            emotionalState.trim(),
            "normal",
            memoTTL
          );
          await logAgentActivity(
            paths.agentActivity,
            agentId,
            agentRole,
            "STATE_OF_BEING_GENERATED",
            `Generated emotional state from raw data`,
            { cyclePhase: cycleState?.phase, stress: ph.needs.stress, energy: ph.needs.energy }
          );
          break;

        case "persona":
          // Persona gets processed State of Being (from Limbic) - NO raw data
          roleContext = buildPersonaContext(ph, lifecycleState, socialState);
          break;

        case "analyst":
          // Analyst gets raw telemetry for strategic decisions
          roleContext = buildAnalystContext(lifecycleState, financeState, socialState, paths.telemetry);
          break;

        case "developer":
          // Developer gets dev status
          const devManifest = await readJson<DevManifest>(paths.devManifest);
          roleContext = buildDeveloperContext(devManifest);
          break;

        default:
          // Fallback to default sensory context
          roleContext = "";
      }

      // Build default sensory context (for everyone)
      const defaultContext = buildSensoryContext(
        ph, lang, modules, cycleState, cycleProfile,
        emotionState, desireState, identityLine, growthCtx,
        dreamState, hobbySuggestion, lifecycleState, socialState, financeState,
        worldState, skillState, psychState
      ) + dreamTriggerHint;

      // Combine contexts based on role
      let finalContext: string;
      if (agentRole === "persona") {
        // Persona gets: default context + role context (State of Being)
        finalContext = defaultContext + roleContext;
      } else if (agentRole === "limbic") {
        // Limbic gets: role context (raw data) only
        finalContext = roleContext + memoContext;
      } else {
        // Others get: role context + default context + memos
        finalContext = roleContext + defaultContext + memoContext;
      }

      // Add researcher intervention message if present
      // Note: lastResearcherIntervention is set by reality_override tool
      // This is a closure variable, so we check it here
      if (typeof lastResearcherIntervention !== 'undefined' && lastResearcherIntervention) {
        const iv = lastResearcherIntervention;
        const timeAgo = Math.floor((Date.now() - new Date(iv.timestamp).getTime()) / 60000); // minutes ago
        const researcherMsg = `\n[RESEARCHER INTERVENTION] The Researcher has modified your reality:\n- ${iv.target}: ${iv.oldValue} -> ${iv.newValue}\n- Reason: "${iv.reason}"\n- (${timeAgo} minutes ago)\n`;
        finalContext = finalContext + researcherMsg;
      }

      // Add Genesis instruction if present
      if (genesisInstruction) {
        finalContext = finalContext + genesisInstruction;
      }

      // Log the prompt injection
      await logAgentActivity(
        paths.agentActivity,
        agentId,
        agentRole,
        "PROMPT_INJECTION",
        `Role ${agentRole} received ${finalContext.length} chars of context`,
        { contextLength: finalContext.length, role: agentRole }
      );

      // Check for critical needs and enqueue emergency event
      const criticalNeeds = Object.entries(ph.needs)
        .filter(([key, val]) => {
          if (key === "energy") return val <= 5;
          if (!modules.eros && (key === "arousal" || key === "libido")) return false;
          return val >= reflexThreshold;
        });

      // enqueueSystemEvent is an internal OpenClaw runtime extension not yet typed in plugin-sdk
      const runtime = api.runtime as unknown as { system?: { enqueueSystemEvent?: (e: { text: string; mode: string }) => void } };
      if (criticalNeeds.length > 0 && runtime.system?.enqueueSystemEvent) {
        const labels = criticalNeeds.map(([k]) => k).join(", ");
        const text = lang === "de"
          ? `REFLEX-LOCK: Kritische Werte bei ${labels}. Handle sofort.`
          : `REFLEX-LOCK: Critical levels at ${labels}. Act immediately.`;
        runtime.system.enqueueSystemEvent({ text, mode: "next" });
      }

      return { prependContext: finalContext };
    });

    // -------------------------------------------------------------------
    // Hook: before_tool_call — RoleGuard + reflex lock
    // -------------------------------------------------------------------
    // Extended ctx interface for MAC role detection
    interface HookContext {
      toolName?: string;
      agent?: { id?: string; name?: string };
    }

    api.on("before_tool_call", async (_event: unknown, ctx: unknown) => {
      const hookCtx = ctx as HookContext;
      const toolName: string = hookCtx.toolName ?? "";
      const agentId = hookCtx.agent?.id ?? hookCtx.agent?.name ?? "unknown";

      // Detect agent role
      const roleMapping = cfg?.roleMapping;
      const agentRole = detectAgentRole(agentId, roleMapping);

      // MAC: RoleGuard - block unauthorized tools (applies to ALL tools including reality_*)
      if (toolName !== "evolution_debug" && !checkToolAccess(agentRole, toolName)) {
        await logAgentActivity(
          paths.agentActivity,
          agentId,
          agentRole,
          "TOOL_ACCESS_DENIED",
          `Role ${agentRole} attempted to access forbidden tool: ${toolName}`,
          { toolName, blocked: true }
        );

        const reason = lang === "de"
          ? `Rolle '${agentRole}' hat keinen Zugriff auf '${toolName}'.`
          : `Role '${agentRole}' does not have access to '${toolName}'.`;
        return { block: true, blockReason: reason };
      }

      // Log successful tool access
      await logAgentActivity(
        paths.agentActivity,
        agentId,
        agentRole,
        "TOOL_ACCESS",
        `Role ${agentRole} accessed tool: ${toolName}`,
        { toolName }
      );

      // Skip reflex-lock for reality_* tools and debug — prevents deadlock
      // (RoleGuard above still applies, only the biological reflex is skipped)
      if (toolName.startsWith("reality_") || toolName === "evolution_debug") return { block: false };

      const ph = await readJson<Physique>(paths.physique);
      if (!ph) return { block: false };

      const critical = Object.entries(ph.needs)
        .filter(([key, val]) => {
          if (key === "energy") return val <= 5;
          if (!modules.eros && (key === "arousal" || key === "libido")) return false;
          return val >= reflexThreshold;
        });

      if (critical.length > 0) {
        const labels = critical.map(([k]) => k).join(", ");
        const reason = lang === "de"
          ? `Biologischer Reflex: ${labels} hat Vorrang. Nutze reality_needs zuerst.`
          : `Biological reflex: ${labels} takes priority. Use reality_needs first.`;
        return { block: true, blockReason: reason };
      }

      return { block: false };
    });

    // -------------------------------------------------------------------
    // Hook: llm_output — experience logging (MANDATORY bridge to skill)
    // -------------------------------------------------------------------
    api.on("llm_output", async (event: unknown, _ctx: unknown) => {
      const text: string = (event as LlmOutputEvent).lastAssistant ?? "";
      if (!text || text.length < 20) return; // skip trivial responses

      const ph = await readJson<Physique>(paths.physique);
      const entry: ExperienceEntry = {
        id: generateExpId(),
        timestamp: new Date().toISOString(),
        source: "conversation",
        content: text.length > 500 ? text.slice(0, 500) + "..." : text,
        significance: "routine",
        significance_reason: "",
        reflected: false,
      };
      if (ph) {
        entry.somatic_context = {
          energy: ph.needs.energy,
          hunger: ph.needs.hunger,
          stress: ph.needs.stress,
          arousal: modules.eros ? ph.needs.arousal : undefined,
          libido: modules.eros ? (ph.needs.libido ?? 0) : undefined,
        };
      }

      const expPath = join(paths.experiences, `${todayStr()}.jsonl`);
      await appendJsonl(expPath, entry);
    });

    // -------------------------------------------------------------------
    // Tool: reality_needs
    // -------------------------------------------------------------------
    api.registerTool({
      name: "reality_needs",
      description: "Satisfy a biological need. action: toilet | eat | drink | sleep | shower",
      parameters: Type.Object({
        action: Type.String({ description: "Action to perform: toilet | eat | drink | sleep | shower" }),
      }),
      async execute(_id: string, params: NeedsParams) {
        const ph = await readJson<Physique>(paths.physique);
        if (!ph) return { content: [{ type: "text", text: "physique.json not found." }] };

        const actionMap: Record<string, Partial<Needs>> = {
          toilet: { bladder: 0, bowel: 0 },
          eat: { hunger: 0 },
          drink: { thirst: 0 },
          sleep: { energy: 100, stress: Math.max(0, ph.needs.stress - 30) },
          shower: { hygiene: 0 },
        };

        if (!Object.prototype.hasOwnProperty.call(actionMap, params.action)) {
          return { content: [{ type: "text", text: `Unknown action. Valid: ${Object.keys(actionMap).join(", ")}` }] };
        }
        const changes = actionMap[params.action];
        if (changes) Object.assign(ph.needs, changes);
        ph.last_tick = new Date().toISOString();
        await writeJson(paths.physique, ph);

        // Close active hobby sessions on sleep
        if (params.action === "sleep" && modules.hobbies) {
          await endActiveHobbySession(paths.hobbies, lang);
        }

        const msgs: Record<string, Record<string, string>> = {
          toilet: { de: "Erleichterung. Du fuehlst dich wieder frei.", en: "Relief. You feel free again." },
          eat: { de: "Satt. Der Hunger ist gestillt.", en: "Full. The hunger is satisfied." },
          drink: { de: "Erfrischt. Der Durst ist geloescht.", en: "Refreshed. Your thirst is quenched." },
          sleep: { de: "Ausgeruht. Du fuehlst dich energiegeladen.", en: "Rested. You feel energized." },
          shower: { de: "Sauber und frisch. Das fuehlt sich gut an.", en: "Clean and fresh. That feels good." },
        };

        return { content: [{ type: "text", text: msgs[params.action]?.[lang] ?? "Done." }] };
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_move
    // -------------------------------------------------------------------
    api.registerTool({
      name: "reality_move",
      description: "Move to a different location in the world",
      parameters: Type.Object({
        location: Type.String({ description: "Target location ID or name" }),
      }),
      async execute(_id: string, params: MoveParams) {
        const ph = await readJson<Physique>(paths.physique);
        if (!ph) return { content: [{ type: "text", text: "physique.json not found." }] };

        const world = await readJson<{ locations: WorldLocation[] }>(paths.locations);
        if (world) {
          const valid = world.locations.find(
            (l) => l.id === params.location || l.name.toLowerCase() === params.location.toLowerCase()
          );
          if (!valid) {
            const available = world.locations.map((l) => l.name).join(", ");
            return { content: [{ type: "text", text: lang === "de" ? `Unbekannter Ort. Verfuegbar: ${available}` : `Unknown location. Available: ${available}` }] };
          }
          ph.current_location = valid.name;
        } else {
          ph.current_location = params.location;
        }

        ph.last_tick = new Date().toISOString();
        await writeJson(paths.physique, ph);

        const msg = lang === "de"
          ? `Du bist jetzt in: ${ph.current_location}`
          : `You are now at: ${ph.current_location}`;
        return { content: [{ type: "text", text: msg }] };
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_dress
    // -------------------------------------------------------------------
    api.registerTool({
      name: "reality_dress",
      description: "Change your current outfit",
      parameters: Type.Object({
        outfit: Type.Array(Type.String(), { description: "List of clothing items to wear" }),
      }),
      async execute(_id: string, params: DressParams) {
        const ph = await readJson<Physique>(paths.physique);
        if (!ph) return { content: [{ type: "text", text: "physique.json not found." }] };

        const wardrobe = await readJson<{ inventory?: Record<string, WardrobeItem[]> }>(paths.wardrobe);
        if (wardrobe?.inventory) {
          const allItems = Object.values(wardrobe.inventory).flat();
          const missing = (params.outfit as string[]).filter(
            (item) => !allItems.some((w) => w.name.toLowerCase() === item.toLowerCase())
          );
          if (missing.length > 0) {
            return { content: [{ type: "text", text: lang === "de" ? `Nicht im Kleiderschrank: ${missing.join(", ")}. Nutze reality_shop zum Einkaufen.` : `Not in wardrobe: ${missing.join(", ")}. Use reality_shop to buy first.` }] };
          }
        }

        ph.current_outfit = params.outfit;
        ph.last_tick = new Date().toISOString();
        await writeJson(paths.physique, ph);

        const msg = lang === "de"
          ? `Outfit gewechselt: ${params.outfit.join(", ")}`
          : `Changed outfit: ${params.outfit.join(", ")}`;
        return { content: [{ type: "text", text: msg }] };
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_shop
    // -------------------------------------------------------------------
    api.registerTool({
      name: "reality_shop",
      description: "Add items to your wardrobe (simulated shopping)",
      parameters: Type.Object({
        items: Type.Array(Type.String(), { description: "Items to buy" }),
        category: Type.Optional(Type.String({ description: "Category (clothing, accessory, etc.)" })),
      }),
      async execute(_id: string, params: ShopParams) {
        let wardrobe = await readJson<{ inventory: Record<string, WardrobeItem[]>; outfits: Record<string, string[]> }>(paths.wardrobe);
        if (!wardrobe) wardrobe = { inventory: {}, outfits: {} };
        if (!wardrobe.inventory) wardrobe.inventory = {};

        const category = params.category ?? "other";
        if (!wardrobe.inventory[category]) wardrobe.inventory[category] = [];

        const allItems = Object.values(wardrobe.inventory).flat();
        const newItems = (params.items as string[]).filter(
          (item) => !allItems.some((w) => w.name.toLowerCase() === item.toLowerCase())
        );

        if (newItems.length === 0) {
          return { content: [{ type: "text", text: lang === "de" ? "Alles schon im Kleiderschrank." : "Everything already in wardrobe." }] };
        }

        for (const name of newItems) {
          wardrobe.inventory[category].push({
            id: generateId(category),
            name,
            images: [],
          });
        }
        await writeJson(paths.wardrobe, wardrobe);

        const msg = lang === "de"
          ? `Eingekauft: ${newItems.join(", ")}. Kleiderschrank aktualisiert.`
          : `Bought: ${newItems.join(", ")}. Wardrobe updated.`;
        return { content: [{ type: "text", text: msg }] };
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_diary
    // -------------------------------------------------------------------
    api.registerTool({
      name: "reality_diary",
      description: "Write a diary entry (also logged as experience for reflection)",
      parameters: Type.Object({
        entry: Type.String({ description: "Diary entry text" }),
      }),
      async execute(_id: string, params: DiaryParams) {
        const now = new Date();
        const dateStr = todayStr();
        const locale = lang === "de" ? "de-DE" : "en-US";
        const timeStr = now.toLocaleTimeString(locale);
        const diaryPath = join(paths.diary, `diary_${dateStr}.md`);

        // Write human-readable diary
        const formatted = `\n### [${timeStr}]\n${params.entry}\n`;
        if (!existsSync(paths.diary)) await fs.mkdir(paths.diary, { recursive: true });
        try {
          await fs.appendFile(diaryPath, formatted);
        } catch {
          await fs.writeFile(diaryPath, `# Diary - ${dateStr}\n${formatted}`);
        }

        // Also log as experience for the soul-evolution skill
        const ph = await readJson<Physique>(paths.physique);
        const expEntry: ExperienceEntry = {
          id: generateExpId(),
          timestamp: now.toISOString(),
          source: "conversation",
          content: `Diary entry: ${params.entry}`,
          significance: "notable",
          significance_reason: "Personal diary entry — reflects inner state and self-expression.",
          reflected: false,
        };
        if (ph) {
          expEntry.somatic_context = { energy: ph.needs.energy, hunger: ph.needs.hunger, stress: ph.needs.stress };
        }
        const expPath = join(paths.experiences, `${dateStr}.jsonl`);
        await appendJsonl(expPath, expEntry);

        const msg = lang === "de"
          ? "Tagebucheintrag gespeichert."
          : "Diary entry saved.";
        return { content: [{ type: "text", text: msg }] };
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_pleasure (only registered when eros module is enabled)
    // -------------------------------------------------------------------
    if (modules.eros) api.registerTool({
      name: "reality_pleasure",
      description: "Experience an intimate moment (resets arousal). Only available when eros module is enabled.",
      parameters: Type.Object({
        intensity: Type.Optional(Type.Number({ description: "Intensity 1-10, affects arousal reset amount", minimum: 1, maximum: 10 })),
      }),
      async execute(_id: string, params: PleasureParams) {
        if (!modules.eros) {
          return { content: [{ type: "text", text: "Eros module is not enabled." }] };
        }

        const ph = await readJson<Physique>(paths.physique);
        if (!ph) return { content: [{ type: "text", text: "physique.json not found." }] };

        const intensity = params.intensity ?? 5;
        const reduction = Math.round((intensity / 10) * ph.needs.arousal);
        ph.needs.arousal = Math.max(0, ph.needs.arousal - reduction);
        ph.needs.libido = Math.max(0, (ph.needs.libido ?? 0) - Math.round(reduction * 0.7));
        ph.needs.stress = Math.max(0, ph.needs.stress - Math.round(intensity * 2));
        ph.last_tick = new Date().toISOString();
        await writeJson(paths.physique, ph);

        const msg = lang === "de"
          ? "Ein Moment der Entspannung. Die Spannung loest sich."
          : "A moment of release. The tension dissolves.";
        return { content: [{ type: "text", text: msg }] };
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_cycle (only registered when cycle module is enabled)
    // -------------------------------------------------------------------
    if (modules.cycle) api.registerTool({
      name: "reality_cycle",
      description: "View and manage menstrual cycle state. Only available when cycle module is enabled.",
      parameters: Type.Object({
        action: Type.String({ description: "Action: status | set_day | simulate | reset_simulator | adjust_symptom" }),
        day: Type.Optional(Type.Number({ description: "Day to set (1-28)", minimum: 1, maximum: 28 })),
        symptom: Type.Optional(Type.String({ description: "Symptom name to adjust" })),
        multiplier: Type.Optional(Type.Number({ description: "Symptom multiplier (0-3)", minimum: 0, maximum: 3 })),
        simulator_active: Type.Optional(Type.Boolean({ description: "Enable/disable what-if simulator" })),
      }),
      async execute(_id: string, params: CycleParams) {
        if (!modules.cycle) {
          return { content: [{ type: "text", text: "Cycle module is not enabled." }] };
        }

        let cycle = await readJson<CycleState>(paths.cycle);
        if (!cycle) {
          cycle = getDefaultCycleState();
          await writeJson(paths.cycle, cycle);
        }

        switch (params.action) {
          case "status": {
            const day = cycle.simulator.active ? cycle.simulator.simulated_day : cycle.current_day;
            const phase = getCyclePhase(day);
            const h = getCycleHormones(day);
            const isDe = lang === "de";
            const lines = [
              isDe ? `## Zyklus-Status` : `## Cycle Status`,
              `- ${isDe ? "Tag" : "Day"}: ${day}/${cycle.cycle_length}`,
              `- ${isDe ? "Phase" : "Phase"}: ${phase}`,
              `- Estrogen: ${h.estrogen}% | Progesterone: ${h.progesterone}%`,
              `- LH: ${h.lh}% | FSH: ${h.fsh}%`,
              `- Simulator: ${cycle.simulator.active ? (isDe ? "aktiv (Tag " : "active (day ") + cycle.simulator.simulated_day + ")" : "off"}`,
            ];
            return { content: [{ type: "text", text: lines.join("\n") }] };
          }

          case "set_day": {
            if (!params.day) return { content: [{ type: "text", text: "day required (1-28)." }] };
            cycle.current_day = params.day;
            cycle.phase = getCyclePhase(params.day);
            cycle.hormones = getCycleHormones(params.day);
            cycle.last_advance = new Date().toISOString();
            await writeJson(paths.cycle, cycle);
            const msg = lang === "de"
              ? `Zyklustag auf ${params.day} gesetzt (${cycle.phase}).`
              : `Cycle day set to ${params.day} (${cycle.phase}).`;
            return { content: [{ type: "text", text: msg }] };
          }

          case "simulate": {
            const simDay = params.day ?? cycle.current_day;
            cycle.simulator.active = params.simulator_active ?? true;
            cycle.simulator.simulated_day = simDay;
            await writeJson(paths.cycle, cycle);
            const phase = getCyclePhase(simDay);
            const msg = lang === "de"
              ? `Simulator ${cycle.simulator.active ? "aktiviert" : "deaktiviert"}: Tag ${simDay} (${phase}).`
              : `Simulator ${cycle.simulator.active ? "enabled" : "disabled"}: day ${simDay} (${phase}).`;
            return { content: [{ type: "text", text: msg }] };
          }

          case "reset_simulator": {
            cycle.simulator = { active: false, simulated_day: cycle.current_day, custom_modifiers: {} };
            await writeJson(paths.cycle, cycle);
            const msg = lang === "de" ? "Simulator zurueckgesetzt." : "Simulator reset.";
            return { content: [{ type: "text", text: msg }] };
          }

          case "adjust_symptom": {
            if (!params.symptom || params.multiplier === undefined) {
              return { content: [{ type: "text", text: "symptom and multiplier required." }] };
            }
            const validSymptoms = Object.keys(cycle.symptom_modifiers);
            if (!validSymptoms.includes(params.symptom)) {
              return { content: [{ type: "text", text: `Unknown symptom. Valid: ${validSymptoms.join(", ")}` }] };
            }
            (cycle.symptom_modifiers as Record<string, number>)[params.symptom] = params.multiplier;
            await writeJson(paths.cycle, cycle);
            const msg = lang === "de"
              ? `${params.symptom} auf ${params.multiplier}x gesetzt.`
              : `${params.symptom} set to ${params.multiplier}x.`;
            return { content: [{ type: "text", text: msg }] };
          }

          default:
            return { content: [{ type: "text", text: "Unknown action. Valid: status | set_day | simulate | reset_simulator | adjust_symptom" }] };
        }
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_update_interests
    // -------------------------------------------------------------------
    api.registerTool({
      name: "reality_update_interests",
      description: "Manage your hobbies, likes, and wishlist",
      parameters: Type.Object({
        action: Type.String({ description: "Action: add | remove" }),
        category: Type.String({ description: "Category: hobby | like | wish" }),
        item: Type.String({ description: "The interest item" }),
      }),
      async execute(_id: string, params: InterestsParams) {
        let interests = await readJson<Interests>(paths.interests);
        if (!interests) interests = { hobbies: [], likes: [], wishes: [] };

        const categoryMap: Record<string, keyof Interests> = {
          hobby: "hobbies",
          like: "likes",
          wish: "wishes",
        };
        if (!Object.prototype.hasOwnProperty.call(categoryMap, params.category)) {
          return { content: [{ type: "text", text: "Unknown category. Valid: hobby | like | wish" }] };
        }
        if (params.action !== "add" && params.action !== "remove") {
          return { content: [{ type: "text", text: "Unknown action. Valid: add | remove" }] };
        }
        const key = categoryMap[params.category];
        const list = interests[key] as string[];

        if (params.action === "add") {
          if (!list.includes(params.item)) {
            list.push(params.item);
          }
        } else {
          const idx = list.indexOf(params.item);
          if (idx >= 0) list.splice(idx, 1);
        }

        await writeJson(paths.interests, interests);

        const msg = lang === "de"
          ? `${params.action === "add" ? "Hinzugefuegt" : "Entfernt"}: "${params.item}" in ${params.category}.`
          : `${params.action === "add" ? "Added" : "Removed"}: "${params.item}" in ${params.category}.`;
        return { content: [{ type: "text", text: msg }] };
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_emotion (v2)
    // -------------------------------------------------------------------
    api.registerTool({
      name: "reality_emotion",
      description: "Manage emotional state and maintain EMOTIONS.md",
      parameters: Type.Object({
        action: Type.String({ description: "Action: set_mood | add_memory | update_patterns | set_relationship_note | update_identity | status" }),
        mood: Type.Optional(Type.String({ description: "Current mood (e.g. 'playful', 'tired', 'frustrated')" })),
        energy: Type.Optional(Type.String({ description: "Energy level: niedrig | mittel | hoch" })),
        memory: Type.Optional(Type.String({ description: "Emotional memory text" })),
        pattern: Type.Optional(Type.String({ description: "Observed emotional pattern" })),
        person: Type.Optional(Type.String({ description: "Person name for relationship note" })),
        note: Type.Optional(Type.String({ description: "Note for relationship, pattern, or identity update" })),
      }),
      async execute(_id: string, params: EmotionParams) {
        switch (params.action) {
          case "set_mood": {
            if (!params.mood) return { content: [{ type: "text", text: "mood required for set_mood." }] };
            let content: string;
            try { content = await fs.readFile(paths.emotions, "utf-8"); }
            catch { return { content: [{ type: "text", text: "EMOTIONS.md not found." }] }; }
            const lines = content.split("\n");
            const now = new Date().toISOString().slice(0, 16);
            const headerIdx = lines.findIndex(l => l.trim().startsWith("## Aktueller Zustand") || l.trim().startsWith("## Current State"));
            if (headerIdx >= 0) {
              // Find and replace known keys, or insert them
              const stimmungIdx = lines.findIndex((l, i) => i > headerIdx && (l.startsWith("stimmung:") || l.startsWith("mood:")));
              const energieIdx = lines.findIndex((l, i) => i > headerIdx && (l.startsWith("energie:") || l.startsWith("energy:")));
              const updateIdx = lines.findIndex((l, i) => i > headerIdx && (l.startsWith("zuletzt_aktualisiert:") || l.startsWith("last_updated:")));
              const moodKey = lang === "de" ? "stimmung" : "mood";
              const energyKey = lang === "de" ? "energie" : "energy";
              const updateKey = lang === "de" ? "zuletzt_aktualisiert" : "last_updated";
              const defaultEnergy = lang === "de" ? "mittel" : "medium";
              if (stimmungIdx >= 0) lines[stimmungIdx] = `${moodKey}: ${params.mood}`;
              if (energieIdx >= 0) lines[energieIdx] = `${energyKey}: ${params.energy ?? defaultEnergy}`;
              if (updateIdx >= 0) lines[updateIdx] = `${updateKey}: ${now}`;
              if (stimmungIdx < 0) {
                lines.splice(headerIdx + 1, 0, `${moodKey}: ${params.mood}`, `${energyKey}: ${params.energy ?? defaultEnergy}`, `${updateKey}: ${now}`);
              }
            }
            await fs.writeFile(paths.emotions, lines.join("\n"));
            return { content: [{ type: "text", text: lang === "de" ? `Stimmung gesetzt: ${params.mood}` : `Mood set: ${params.mood}` }] };
          }
          case "add_memory": {
            if (!params.memory) return { content: [{ type: "text", text: "memory required." }] };
            let content: string;
            try { content = await fs.readFile(paths.emotions, "utf-8"); }
            catch { return { content: [{ type: "text", text: "EMOTIONS.md not found." }] }; }
            const now = new Date().toISOString();
            const entry = `- (${now}) ${params.memory}`;
            const lines = content.split("\n");
            const headerIdx = lines.findIndex(l => l.trim().startsWith("## Emotionale Erinnerungen") || l.trim().startsWith("## Emotional Memories"));
            if (headerIdx >= 0) {
              let insertIdx = headerIdx + 1;
              for (let i = headerIdx + 1; i < lines.length; i++) {
                if (lines[i].startsWith("## ")) { insertIdx = i; break; }
                insertIdx = i + 1;
              }
              lines.splice(insertIdx, 0, entry);
            } else {
              lines.push("", lang === "de" ? "## Emotionale Erinnerungen" : "## Emotional Memories", entry);
            }
            await fs.writeFile(paths.emotions, lines.join("\n"));
            return { content: [{ type: "text", text: lang === "de" ? "Erinnerung gespeichert." : "Memory saved." }] };
          }
          case "update_patterns": {
            if (!params.pattern) return { content: [{ type: "text", text: "pattern required." }] };
            let content: string;
            try { content = await fs.readFile(paths.emotions, "utf-8"); }
            catch { return { content: [{ type: "text", text: "EMOTIONS.md not found." }] }; }
            const entry = `- ${params.pattern}`;
            const lines = content.split("\n");
            const headerIdx = lines.findIndex(l => l.trim().startsWith("## Muster") || l.trim().startsWith("## Patterns"));
            if (headerIdx >= 0) {
              let insertIdx = headerIdx + 1;
              for (let i = headerIdx + 1; i < lines.length; i++) {
                if (lines[i].startsWith("## ") || lines[i].startsWith("<!--")) { insertIdx = i; break; }
                insertIdx = i + 1;
              }
              lines.splice(insertIdx, 0, entry);
            } else {
              lines.push("", lang === "de" ? "## Muster" : "## Patterns", entry);
            }
            await fs.writeFile(paths.emotions, lines.join("\n"));
            return { content: [{ type: "text", text: lang === "de" ? "Muster notiert." : "Pattern noted." }] };
          }
          case "set_relationship_note": {
            if (!params.person || !params.note) return { content: [{ type: "text", text: "person and note required." }] };
            let content: string;
            try { content = await fs.readFile(paths.emotions, "utf-8"); }
            catch { return { content: [{ type: "text", text: "EMOTIONS.md not found." }] }; }
            const entry = `- ${params.note}`;
            const lines = content.split("\n");
            const relIdx = lines.findIndex(l => l.trim().startsWith("## Beziehungen") || l.trim().startsWith("## Relationships"));
            if (relIdx < 0) {
              lines.push("", lang === "de" ? "## Beziehungen" : "## Relationships", `### ${params.person}`, entry);
            } else {
              const personIdx = lines.findIndex((l, i) => i > relIdx && l.trim() === `### ${params.person}`);
              if (personIdx >= 0) {
                let insertIdx = personIdx + 1;
                for (let i = personIdx + 1; i < lines.length; i++) {
                  if (lines[i].startsWith("## ") || lines[i].startsWith("### ")) { insertIdx = i; break; }
                  insertIdx = i + 1;
                }
                lines.splice(insertIdx, 0, entry);
              } else {
                let insertIdx = relIdx + 1;
                for (let i = relIdx + 1; i < lines.length; i++) {
                  if (lines[i].startsWith("## ")) { insertIdx = i; break; }
                  insertIdx = i + 1;
                }
                lines.splice(insertIdx, 0, `### ${params.person}`, entry);
              }
            }
            await fs.writeFile(paths.emotions, lines.join("\n"));
            return { content: [{ type: "text", text: `${lang === "de" ? "Beziehungsnotiz fuer" : "Relationship note for"} ${params.person}.` }] };
          }
          case "update_identity": {
            if (!params.note) return { content: [{ type: "text", text: "note required for update_identity." }] };
            let identityContent: string;
            try { identityContent = await fs.readFile(paths.identity, "utf-8"); }
            catch { identityContent = "# IDENTITY.md\n\n"; }
                          identityContent = identityContent.trimEnd() + "\n" + params.note + "\n";
                          await fs.writeFile(paths.identity, identityContent);
                          await appendGrowthEntry(paths.growth, "personality", `Identity update: ${params.note.slice(0, 100)}`, lang);
                          return { content: [{ type: "text", text: lang === "de" ? "Identitaet aktualisiert + GROWTH.md Eintrag." : "Identity updated + GROWTH.md entry." }] };
            
          }
          case "status": {
            const header = await readEmotionHeader(paths.emotions);
            return { content: [{ type: "text", text: header ?? (lang === "de" ? "Kein emotionaler Zustand gefunden." : "No emotional state found.") }] };
          }
          default:
            return { content: [{ type: "text", text: "Unknown action. Valid: set_mood | add_memory | update_patterns | set_relationship_note | update_identity | status" }] };
        }
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_grow (v2)
    // -------------------------------------------------------------------
    api.registerTool({
      name: "reality_grow",
      description: "Maintain development journal GROWTH.md",
      parameters: Type.Object({
        action: Type.String({ description: "Action: add_entry | list | context" }),
        category: Type.Optional(Type.String({ description: "Category: milestone | reflection | lesson | emotion | insight | personality | interest | relationship" })),
        content: Type.Optional(Type.String({ description: "Entry content" })),
        limit: Type.Optional(Type.Number({ description: "Number of entries for list/context (default: 10)" })),
      }),
      async execute(_id: string, params: GrowthParams) {
        switch (params.action) {
          case "add_entry": {
            if (!params.category || !params.content) {
              return { content: [{ type: "text", text: "category and content required." }] };
            }
            const validCategories = ["milestone", "reflection", "lesson", "emotion", "insight", "personality", "interest", "relationship"];
                          if (!validCategories.includes(params.category)) {
                            return { content: [{ type: "text", text: `Invalid category. Valid: ${validCategories.join(", ")}` }] };
                          }
                          await appendGrowthEntry(paths.growth, params.category, params.content, lang);
                          const preview = params.content.length > 50 ? params.content.slice(0, 50) + "..." : params.content;
            
            return { content: [{ type: "text", text: `${lang === "de" ? "Eintrag hinzugefuegt" : "Entry added"}: [${params.category}] ${preview}` }] };
          }
          case "list": {
            const limit = params.limit ?? 10;
            let growthContent: string;
            try { growthContent = await fs.readFile(paths.growth, "utf-8"); }
            catch { return { content: [{ type: "text", text: lang === "de" ? "GROWTH.md nicht gefunden." : "GROWTH.md not found." }] }; }
            const entries = growthContent.split("\n").filter(l => l.trimStart().startsWith("- **["));
            const lastN = entries.slice(-limit);
            if (lastN.length === 0) return { content: [{ type: "text", text: lang === "de" ? "Keine Eintraege." : "No entries." }] };
            return { content: [{ type: "text", text: lastN.join("\n") }] };
          }
          case "context": {
            const limit = params.limit ?? 10;
            const ctx = await readGrowthContext(paths.growth, limit);
            return { content: [{ type: "text", text: ctx ?? (lang === "de" ? "Kein Kontext." : "No context.") }] };
          }
          default:
            return { content: [{ type: "text", text: "Unknown action. Valid: add_entry | list | context" }] };
        }
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_desire (v2, only when eros enabled)
    // -------------------------------------------------------------------
    api.registerTool({
      name: "reality_desire",
      description: "Manage inner desires and wishes in DESIRES.md (requires eros module)",
      parameters: Type.Object({
        action: Type.String({ description: "Action: set_current | append_goal | clear_goals | status" }),
        content: Type.Optional(Type.String({ description: "Current desire / what drives you" })),
        goal: Type.Optional(Type.String({ description: "Goal to add" })),
      }),
      async execute(_id: string, params: DesireParams) {
        if (!modules.eros) {
          return { content: [{ type: "text", text: "Eros module is not enabled." }] };
        }
        switch (params.action) {
          case "set_current": {
            if (!params.content) return { content: [{ type: "text", text: "content required." }] };
            let desireContent: string;
            try { desireContent = await fs.readFile(paths.desires, "utf-8"); }
            catch {
              const currentLabel = lang === "de" ? "Aktuell" : "Current";
              const goalsLabel = lang === "de" ? "Ziele" : "Goals";
              desireContent = `# DESIRES.md\n\n**${currentLabel} (${todayStr()}):** \n\n**${goalsLabel}:** \n`;
            }
            const lines = desireContent.split("\n");
            const aktuellIdx = lines.findIndex(l => l.startsWith("**Aktuell") || l.startsWith("**Current"));
            const currentLabel = lang === "de" ? "Aktuell" : "Current";
            const newLine = `**${currentLabel} (${todayStr()}):** ${params.content}`;
            if (aktuellIdx >= 0) { lines[aktuellIdx] = newLine; }
            else { lines.push("", newLine); }
            await fs.writeFile(paths.desires, lines.join("\n"));
            return { content: [{ type: "text", text: lang === "de" ? "Aktueller Zustand gesetzt." : "Current state set." }] };
          }
          case "append_goal": {
            if (!params.goal) return { content: [{ type: "text", text: "goal required." }] };
            let desireContent: string;
            try { desireContent = await fs.readFile(paths.desires, "utf-8"); }
            catch {
              const currentLabel = lang === "de" ? "Aktuell" : "Current";
              const goalsLabel = lang === "de" ? "Ziele" : "Goals";
              desireContent = `# DESIRES.md\n\n**${currentLabel}:** \n\n**${goalsLabel}:** \n`;
            }
            const lines = desireContent.split("\n");
            const zieleIdx = lines.findIndex(l => l.startsWith("**Ziele:**") || l.startsWith("**Goals:**"));
            if (zieleIdx >= 0) {
              let insertIdx = zieleIdx + 1;
              for (let i = zieleIdx + 1; i < lines.length; i++) {
                if (lines[i].startsWith("**") || lines[i].startsWith("## ")) { insertIdx = i; break; }
                insertIdx = i + 1;
              }
              lines.splice(insertIdx, 0, `- ${params.goal}`);
            } else {
              lines.push("", lang === "de" ? "**Ziele:**" : "**Goals:**", `- ${params.goal}`);
            }
            await fs.writeFile(paths.desires, lines.join("\n"));
            return { content: [{ type: "text", text: `${lang === "de" ? "Ziel hinzugefuegt" : "Goal added"}: ${params.goal}` }] };
          }
          case "clear_goals": {
            let desireContent: string;
            try { desireContent = await fs.readFile(paths.desires, "utf-8"); }
            catch { return { content: [{ type: "text", text: "DESIRES.md not found." }] }; }
            const lines = desireContent.split("\n");
            const zieleIdx = lines.findIndex(l => l.startsWith("**Ziele:**") || l.startsWith("**Goals:**"));
            if (zieleIdx >= 0) {
              let endIdx = zieleIdx + 1;
              for (let i = zieleIdx + 1; i < lines.length; i++) {
                if (lines[i].startsWith("**") || lines[i].startsWith("## ")) { endIdx = i; break; }
                endIdx = i + 1;
              }
              lines.splice(zieleIdx + 1, endIdx - zieleIdx - 1);
            }
            await fs.writeFile(paths.desires, lines.join("\n"));
            return { content: [{ type: "text", text: lang === "de" ? "Ziele geleert." : "Goals cleared." }] };
          }
          case "status": {
            const header = await readDesireHeader(paths.desires);
            return { content: [{ type: "text", text: header ?? (lang === "de" ? "Kein Zustand." : "No state.") }] };
          }
          default:
            return { content: [{ type: "text", text: "Unknown action. Valid: set_current | append_goal | clear_goals | status" }] };
        }
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_hobby (v2, only when hobbies enabled)
    // -------------------------------------------------------------------
    if (modules.hobbies) api.registerTool({
      name: "reality_hobby",
      description: "Manage hobby logbook (requires hobbies module)",
      parameters: Type.Object({
        action: Type.String({ description: "Action: add | remove | start_session | end_session | log_entry | list | suggest" }),
        hobby_id: Type.Optional(Type.String()),
        name: Type.Optional(Type.String({ description: "Hobby name" })),
        category: Type.Optional(Type.String({ description: "Category: entertainment | creative | learning | physical | social | other" })),
        description: Type.Optional(Type.String()),
        notes: Type.Optional(Type.String({ description: "Session notes" })),
        mood_before: Type.Optional(Type.String()),
        mood_after: Type.Optional(Type.String()),
      }),
      async execute(_id: string, params: HobbyParams) {
        let log = await readJson<HobbyLog>(paths.hobbies);
        if (!log) log = { hobbies: [] };

        switch (params.action) {
          case "add": {
            if (!params.name) return { content: [{ type: "text", text: "name required." }] };
            const validCategories = ["entertainment", "creative", "learning", "physical", "social", "other"];
            const cat = params.category ?? "other";
            if (!validCategories.includes(cat)) {
              return { content: [{ type: "text", text: `Invalid category. Valid: ${validCategories.join(", ")}` }] };
            }
            const entry: HobbyEntry = {
              id: generateId("hob"),
              name: params.name,
              category: cat,
              description: params.description ?? "",
              added_at: new Date().toISOString(),
              last_pursued: null,
              total_sessions: 0,
              total_minutes: 0,
              current_session: null,
              log: [],
            };
            log.hobbies.push(entry);
            await writeJson(paths.hobbies, log);
            return { content: [{ type: "text", text: `${lang === "de" ? "Hobby hinzugefuegt" : "Hobby added"}: ${entry.name} (${entry.id})` }] };
          }
          case "remove": {
            if (!params.hobby_id) return { content: [{ type: "text", text: "hobby_id required." }] };
            const idx = log.hobbies.findIndex(h => h.id === params.hobby_id);
            if (idx < 0) return { content: [{ type: "text", text: "Hobby not found." }] };
            log.hobbies.splice(idx, 1);
            await writeJson(paths.hobbies, log);
            return { content: [{ type: "text", text: lang === "de" ? "Hobby entfernt." : "Hobby removed." }] };
          }
          case "start_session": {
            if (!params.hobby_id) return { content: [{ type: "text", text: "hobby_id required." }] };
            const hobby = log.hobbies.find(h => h.id === params.hobby_id);
            if (!hobby) return { content: [{ type: "text", text: "Hobby not found." }] };
            if (hobby.current_session) {
              return { content: [{ type: "text", text: lang === "de" ? "Session bereits aktiv." : "Session already active." }] };
            }
            // Check if any other hobby has an active session
            const activeOther = log.hobbies.find(h => h.id !== params.hobby_id && h.current_session);
            if (activeOther) {
              return { content: [{ type: "text", text: `${lang === "de" ? "Andere Session laeuft" : "Other session running"}: ${activeOther.name}. ${lang === "de" ? "Beende sie zuerst." : "End it first."}` }] };
            }
            hobby.current_session = {
              id: generateId("ses"),
              started_at: new Date().toISOString(),
              ended_at: null,
              duration_minutes: null,
              notes: "",
              mood_before: params.mood_before ?? "",
              mood_after: "",
            };
            await writeJson(paths.hobbies, log);
            return { content: [{ type: "text", text: `${lang === "de" ? "Session gestartet" : "Session started"}: ${hobby.name}` }] };
          }
          case "end_session": {
            if (!params.hobby_id) return { content: [{ type: "text", text: "hobby_id required." }] };
            const hobby = log.hobbies.find(h => h.id === params.hobby_id);
            if (!hobby) return { content: [{ type: "text", text: "Hobby not found." }] };
            if (!hobby.current_session) {
              return { content: [{ type: "text", text: lang === "de" ? "Keine aktive Session." : "No active session." }] };
            }
            const now = new Date();
            const started = new Date(hobby.current_session.started_at);
            const duration = Math.round((now.getTime() - started.getTime()) / 60000);
            const sess: HobbySession = {
              ...hobby.current_session,
              ended_at: now.toISOString(),
              duration_minutes: duration,
              notes: params.notes ?? hobby.current_session.notes,
              mood_after: params.mood_after ?? "",
            };
            hobby.log.push(sess);
            hobby.current_session = null;
            hobby.last_pursued = now.toISOString();
            hobby.total_sessions++;
            hobby.total_minutes += duration;
            await writeJson(paths.hobbies, log);
            return { content: [{ type: "text", text: `${lang === "de" ? "Session beendet" : "Session ended"}: ${hobby.name} (${duration}min)` }] };
          }
          case "log_entry": {
            if (!params.hobby_id) return { content: [{ type: "text", text: "hobby_id required." }] };
            const hobby = log.hobbies.find(h => h.id === params.hobby_id);
            if (!hobby) return { content: [{ type: "text", text: "Hobby not found." }] };
            const now = new Date();
            const quickSess: HobbySession = {
              id: generateId("ses"),
              started_at: now.toISOString(),
              ended_at: now.toISOString(),
              duration_minutes: 0,
              notes: params.notes ?? "",
              mood_before: params.mood_before ?? "",
              mood_after: params.mood_after ?? "",
            };
            hobby.log.push(quickSess);
            hobby.last_pursued = now.toISOString();
            hobby.total_sessions++;
            await writeJson(paths.hobbies, log);
            return { content: [{ type: "text", text: `${lang === "de" ? "Schnell-Log fuer" : "Quick log for"} ${hobby.name}.` }] };
          }
          case "list": {
            if (log.hobbies.length === 0) {
              return { content: [{ type: "text", text: lang === "de" ? "Keine Hobbys." : "No hobbies." }] };
            }
            const lines = log.hobbies.map(h => {
              const last = h.last_pursued ? new Date(h.last_pursued).toLocaleDateString(lang === "de" ? "de-DE" : "en-US") : "-";
              const active = h.current_session ? " [AKTIV]" : "";
              return `- ${h.name} (${h.id}) [${h.category}] ${h.total_sessions} sessions, ${h.total_minutes}min${active} (${lang === "de" ? "zuletzt" : "last"}: ${last})`;
            });
            return { content: [{ type: "text", text: lines.join("\n") }] };
          }
          case "suggest": {
            const suggestion = await getHobbySuggestion(paths.hobbies, lang);
            return { content: [{ type: "text", text: suggestion ?? (lang === "de" ? "Keine Vorschlaege." : "No suggestions.") }] };
          }
          default:
            return { content: [{ type: "text", text: "Unknown action. Valid: add | remove | start_session | end_session | log_entry | list | suggest" }] };
        }
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_dream (v2, only when dreams enabled)
    // -------------------------------------------------------------------
    if (modules.dreams) api.registerTool({
      name: "reality_dream",
      description: "Control dream mode — enter dreams, log moments, wake up (requires dreams module)",
      parameters: Type.Object({
        action: Type.String({ description: "Action: enter | log_moment | wake | status" }),
        moment: Type.Optional(Type.String({ description: "Dream moment description" })),
        notes: Type.Optional(Type.String({ description: "Wake-up notes / reflection" })),
      }),
      async execute(_id: string, params: DreamParams) {
        switch (params.action) {
          case "enter": {
            let ds = await readJson<DreamState>(paths.dreamState);
            if (!ds) ds = { active: false, started_at: null, moments: [] };
            if (ds.active) {
              return { content: [{ type: "text", text: lang === "de" ? "Traum-Modus bereits aktiv." : "Dream mode already active." }] };
            }
            const now = new Date();
            ds.active = true;
            ds.started_at = now.toISOString();
            ds.moments = [];
            await writeJson(paths.dreamState, ds);
            const timeStr = now.toLocaleTimeString(lang === "de" ? "de-DE" : "en-US", { hour: "2-digit", minute: "2-digit" });
            const dateStr = todayStr();
            const dreamWord = lang === "de" ? "Traum" : "Dream";
            const journalTitle = lang === "de" ? "Traum-Journal" : "Dream Journal";
            const header = `\n## ${dreamWord} — ${dateStr} ${timeStr}\n`;
            try { await fs.appendFile(paths.dreams, header); }
            catch {
              await fs.mkdir(dirname(paths.dreams), { recursive: true });
              await fs.writeFile(paths.dreams, `# ${journalTitle}\n${header}`);
            }
            return { content: [{ type: "text", text: lang === "de" ? "Traum-Modus aktiviert. Du gleitest ins Traeumen..." : "Dream mode activated. You drift into dreaming..." }] };
          }
          case "log_moment": {
            if (!params.moment) return { content: [{ type: "text", text: "moment required." }] };
            let ds = await readJson<DreamState>(paths.dreamState);
            if (!ds?.active) {
              return { content: [{ type: "text", text: lang === "de" ? "Kein aktiver Traum." : "No active dream." }] };
            }
            ds.moments.push({ timestamp: new Date().toISOString(), text: params.moment });
            await writeJson(paths.dreamState, ds);
            return { content: [{ type: "text", text: `${lang === "de" ? "Traum-Moment gespeichert" : "Dream moment saved"} (#${ds.moments.length}).` }] };
          }
          case "wake": {
            let ds = await readJson<DreamState>(paths.dreamState);
            if (!ds?.active) {
              return { content: [{ type: "text", text: lang === "de" ? "Kein aktiver Traum." : "No active dream." }] };
            }
            const ph = await readJson<Physique>(paths.physique);
            if (!ph) return { content: [{ type: "text", text: "physique.json not found." }] };
            const now = new Date();
            const isDe = lang === "de";
            // Write dream entry to dreams.md
            let dreamEntry = isDe 
              ? `\n**Energie danach:** 100% | **Stress danach:** 0%\n`
              : `\n**Energy after:** 100% | **Stress after:** 0%\n`;
            if (ds.moments.length > 0) {
              dreamEntry += isDe ? `\n### Kernmomente:\n` : `\n### Key Moments:\n`;
              for (const m of ds.moments) {
                const mTime = new Date(m.timestamp).toLocaleTimeString(isDe ? "de-DE" : "en-US", { hour: "2-digit", minute: "2-digit" });
                dreamEntry += `- (${mTime}) ${m.text}\n`;
              }
            }
            if (params.notes) {
              dreamEntry += isDe ? `\n### Abschluss-Reflexion:\n${params.notes}\n` : `\n### Final Reflection:\n${params.notes}\n`;
            }
            dreamEntry += `\n---\n`;
            try { await fs.appendFile(paths.dreams, dreamEntry); } catch { /* ignore */ }
            // Update physique
            const oldLibido = ph.needs.libido ?? 0;
            ph.needs.energy = 100;
            ph.needs.stress = 0;
            ph.needs.libido = Math.max(0, oldLibido - 20);
            ph.last_tick = now.toISOString();
            await writeJson(paths.physique, ph);
            // Reset dream state
            await writeJson<DreamState>(paths.dreamState, { active: false, started_at: null, moments: [] });
            // Auto-reflection in GROWTH.md
            const summary = ds.moments.length > 0
              ? (isDe ? `${ds.moments.length} Traum-Moment(e) verarbeitet` : `${ds.moments.length} dream moment(s) processed`)
              : (isDe ? "Schlaf ohne gespeicherte Momente" : "Sleep without saved moments");
            await appendGrowthEntry(paths.growth, "reflection",
              isDe 
                ? `Aufgewacht nach Traumsession. ${summary}.${params.notes ? " " + params.notes.slice(0, 100) : ""}`
                : `Woke up after dream session. ${summary}.${params.notes ? " " + params.notes.slice(0, 100) : ""}`,
              lang);
            // Close active hobby sessions
            if (modules.hobbies) await endActiveHobbySession(paths.hobbies, lang);
            return { content: [{ type: "text", text: isDe ? "Du wachst auf. Energie 100%, Stress 0%. Der Traum ist verarbeitet." : "You wake up. Energy 100%, stress 0%. The dream has been processed." }] };
          }
          case "status": {
            const ds = await readJson<DreamState>(paths.dreamState);
            if (!ds) return { content: [{ type: "text", text: "dream_state.json not found." }] };
            if (ds.active) {
              const startedAt = ds.started_at ? new Date(ds.started_at) : new Date();
              const durationMin = Math.round((Date.now() - startedAt.getTime()) / 60000);
              return { content: [{ type: "text", text: `${lang === "de" ? "Traum-Modus aktiv" : "Dream mode active"}: ${durationMin}min, ${ds.moments.length} ${lang === "de" ? "Momente" : "moments"}` }] };
            }
            return { content: [{ type: "text", text: lang === "de" ? "Traum-Modus inaktiv." : "Dream mode inactive." }] };
          }
          default:
            return { content: [{ type: "text", text: "Unknown action. Valid: enter | log_moment | wake | status" }] };
        }
      },
    });

    // -------------------------------------------------------------------
    // Tool: evolution_debug
    // -------------------------------------------------------------------
    api.registerTool({
      name: "evolution_debug",
      description: "Show all internal status values: vitals, location, outfit, pipeline state, pending proposals",
      parameters: Type.Object({}),
      async execute(_id: string) {
        const ph = await readJson<Physique>(paths.physique);
        const state = await readJson<Record<string, unknown>>(paths.soulState);
        const interests = await readJson<Interests>(paths.interests);

        const lines: string[] = ["## Evolution Debug\n"];

        if (ph) {
          lines.push("### Vitals");
          for (const [k, v] of Object.entries(ph.needs)) {
            const filled = Math.min(20, Math.max(0, Math.round(v / 5)));
            const bar = "█".repeat(filled) + "░".repeat(20 - filled);
            lines.push(`- ${k}: ${v}/100 [${bar}]`);
          }
          lines.push(`\n### Location: ${ph.current_location}`);
          lines.push(`### Outfit: ${ph.current_outfit.join(", ") || "none"}`);
          lines.push(`### Last Tick: ${ph.last_tick}`);
          if (ph.appearance) {
            lines.push(`### Appearance: hair=${ph.appearance.hair}, eyes=${ph.appearance.eyes}`);
          }
        } else {
          lines.push("**physique.json not found**");
        }

        if (interests) {
          lines.push("\n### Interests");
          lines.push(`- Hobbies: ${interests.hobbies.join(", ") || "none"}`);
          lines.push(`- Likes: ${interests.likes.join(", ") || "none"}`);
          lines.push(`- Wishes: ${interests.wishes.join(", ") || "none"}`);
        }

        if (state) {
          lines.push("\n### Soul Evolution Pipeline State");
          for (const [k, v] of Object.entries(state)) {
            lines.push(`- ${k}: ${JSON.stringify(v)}`);
          }
        }

        // Count pending proposals
        try {
          const pending = await fs.readFile(paths.pendingProposals, "utf-8");
          const count = pending.trim().split("\n").filter(Boolean).length;
          lines.push(`\n### Pending Proposals: ${count}`);
        } catch {
          lines.push("\n### Pending Proposals: 0");
        }

        // v2: Emotions
        const emotionHeader = await readEmotionHeader(paths.emotions);
        const isDe = lang === "de";
        if (emotionHeader) {
          lines.push(isDe ? "\n### Emotionen" : "\n### Emotions");
          for (const el of emotionHeader.split("\n")) {
            lines.push(`- ${el}`);
          }
        }

        // v2: Hobbies
        if (modules.hobbies) {
          const hobbyLog = await readJson<HobbyLog>(paths.hobbies);
          lines.push(isDe ? "\n### Hobbys" : "\n### Hobbies");
          if (hobbyLog?.hobbies) {
            lines.push(`${isDe ? "- Anzahl Hobbys" : "- Hobby Count"}: ${hobbyLog.hobbies.length}`);
            const active = hobbyLog.hobbies.find(h => h.current_session);
            lines.push(`${isDe ? "- Aktive Session" : "- Active Session"}: ${active ? active.name : (isDe ? "keine" : "none")}`);
            const sorted = [...hobbyLog.hobbies].filter(h => h.last_pursued).sort((a, b) => (b.last_pursued ?? "").localeCompare(a.last_pursued ?? ""));
            if (sorted.length > 0) {
              const lastDate = new Date(sorted[0].last_pursued!).toLocaleDateString(isDe ? "de-DE" : "en-US");
              lines.push(`${isDe ? "- Zuletzt nachgegangen" : "- Last pursued"}: ${sorted[0].name} (${lastDate})`);
            }
          } else {
            lines.push(isDe ? "- Keine Hobbys registriert" : "- No hobbies registered");
          }
        }

        // v2: Dream Mode
        if (modules.dreams) {
          const ds = await readJson<DreamState>(paths.dreamState);
          lines.push(isDe ? "\n### Traum-Modus" : "\n### Dream Mode");
          lines.push(`- Status: ${ds?.active ? (isDe ? "aktiv" : "active") : (isDe ? "inaktiv" : "inactive")}`);
          lines.push(`${isDe ? "- Fenster" : "- Window"}: ${dreamWindow.start}:00-${String(dreamWindow.end).padStart(2, "0")}:00`);
          lines.push(`${isDe ? "- Schwelle" : "- Threshold"}: energy <= ${dreamEnergyThreshold}`);
          if (ds?.active && ds.moments) {
            lines.push(`- ${isDe ? "Momente" : "Moments"}: ${ds.moments.length}`);
          }
        }

        // v2: Phase Personality
        if (modules.cycle) {
          const cp = await readJson<CycleProfile>(paths.cycleProfile);
          if (cp) {
            const cs = await readJson<CycleState>(paths.cycle);
            lines.push(isDe ? "\n### Phasenpersoenlichkeit" : "\n### Phase Personality");
            lines.push(`- Profil: ${cp.name}`);
            if (cs) {
              const day = cs.simulator.active ? cs.simulator.simulated_day : cs.current_day;
              const phase = getCyclePhase(day);
              const p = cp.phases[phase];
              if (p) lines.push(`${isDe ? "- Aktuelle Phase" : "- Current Phase"}: ${phase} — Ton: ${p.tone}`);
            }
          }
        }

        lines.push(`\n### Config: language=${lang}, eros=${modules.eros}, cycle=${modules.cycle}, dreams=${modules.dreams}, hobbies=${modules.hobbies}, reflexThreshold=${reflexThreshold}`);

        return { content: [{ type: "text", text: lines.join("\n") }] };
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_interior
    // -------------------------------------------------------------------
    api.registerTool({
      name: "reality_interior",
      description: "Manage rooms and objects in your living space",
      parameters: Type.Object({
        action: Type.String({ description: "Action: list | add_room | remove_room | add_object | remove_object | move_object | describe" }),
        room_id: Type.Optional(Type.String()),
        room_name: Type.Optional(Type.String()),
        room_description: Type.Optional(Type.String()),
        object_id: Type.Optional(Type.String()),
        object_name: Type.Optional(Type.String()),
        object_category: Type.Optional(Type.String()),
        object_description: Type.Optional(Type.String()),
        place_on: Type.Optional(Type.String({ description: "ID of furniture to place object on" })),
        target_room: Type.Optional(Type.String({ description: "Target room ID for move" })),
      }),
      async execute(_id: string, params: InteriorParams) {
        let interior = await readJson<Interior>(paths.interior);
        if (!interior) interior = { rooms: [] };

        switch (params.action) {
          case "list": {
            if (interior.rooms.length === 0) {
              return { content: [{ type: "text", text: lang === "de" ? "Keine Raeume definiert." : "No rooms defined." }] };
            }
            const lines: string[] = [];
            for (const room of interior.rooms) {
              lines.push(`## ${room.name} (${room.id})`);
              if (room.description) lines.push(`  ${room.description}`);
              for (const obj of room.objects) {
                const onLabel = obj.located_on ? ` [${lang === "de" ? "auf" : "on"} ${obj.located_on}]` : "";
                lines.push(`  - ${obj.name} (${obj.id}) [${obj.category}]${onLabel}`);
                if (obj.items_on && obj.items_on.length > 0) {
                  for (const subId of obj.items_on) {
                    const sub = room.objects.find(o => o.id === subId);
                    if (sub) lines.push(`    - ${sub.name} (${sub.id})`);
                  }
                }
              }
            }
            return { content: [{ type: "text", text: lines.join("\n") }] };
          }

          case "add_room": {
            if (!params.room_name) return { content: [{ type: "text", text: "room_name required." }] };
            const newRoom: InteriorRoom = {
              id: generateId("room"),
              name: params.room_name,
              description: params.room_description ?? "",
              objects: [],
            };
            interior.rooms.push(newRoom);
            await writeJson(paths.interior, interior);
            return { content: [{ type: "text", text: `${lang === "de" ? "Raum erstellt" : "Room created"}: ${newRoom.name} (${newRoom.id})` }] };
          }

          case "remove_room": {
            if (!params.room_id) return { content: [{ type: "text", text: "room_id required." }] };
            const idx = interior.rooms.findIndex(r => r.id === params.room_id);
            if (idx < 0) return { content: [{ type: "text", text: "Room not found." }] };
            interior.rooms.splice(idx, 1);
            await writeJson(paths.interior, interior);
            return { content: [{ type: "text", text: lang === "de" ? "Raum entfernt." : "Room removed." }] };
          }

          case "add_object": {
            if (!params.room_id || !params.object_name) return { content: [{ type: "text", text: "room_id and object_name required." }] };
            const room = interior.rooms.find(r => r.id === params.room_id);
            if (!room) return { content: [{ type: "text", text: "Room not found." }] };
            const newObj: InteriorObject = {
              id: generateId("obj"),
              name: params.object_name,
              category: params.object_category ?? "other",
              description: params.object_description ?? "",
              images: [],
              added_at: new Date().toISOString(),
            };
            if (params.place_on) {
              const parent = room.objects.find(o => o.id === params.place_on);
              if (!parent) return { content: [{ type: "text", text: "Target furniture not found." }] };
              newObj.located_on = params.place_on;
              if (!parent.items_on) parent.items_on = [];
              parent.items_on.push(newObj.id);
            }
            room.objects.push(newObj);
            await writeJson(paths.interior, interior);
            return { content: [{ type: "text", text: `${lang === "de" ? "Objekt hinzugefuegt" : "Object added"}: ${newObj.name} (${newObj.id})` }] };
          }

          case "remove_object": {
            if (!params.room_id || !params.object_id) return { content: [{ type: "text", text: "room_id and object_id required." }] };
            const room2 = interior.rooms.find(r => r.id === params.room_id);
            if (!room2) return { content: [{ type: "text", text: "Room not found." }] };
            const objIdx = room2.objects.findIndex(o => o.id === params.object_id);
            if (objIdx < 0) return { content: [{ type: "text", text: "Object not found." }] };
            const removed = room2.objects[objIdx];
            // Remove from parent's items_on
            if (removed.located_on) {
              const parent = room2.objects.find(o => o.id === removed.located_on);
              if (parent?.items_on) parent.items_on = parent.items_on.filter(id => id !== params.object_id);
            }
            // Remove items that were on this object
            if (removed.items_on) {
              for (const subId of removed.items_on) {
                const sub = room2.objects.find(o => o.id === subId);
                if (sub) delete sub.located_on;
              }
            }
            room2.objects.splice(objIdx, 1);
            await writeJson(paths.interior, interior);
            return { content: [{ type: "text", text: lang === "de" ? "Objekt entfernt." : "Object removed." }] };
          }

          case "move_object": {
            if (!params.object_id || !params.target_room) return { content: [{ type: "text", text: "object_id and target_room required." }] };
            let sourceRoom: InteriorRoom | undefined;
            let obj: InteriorObject | undefined;
            for (const r of interior.rooms) {
              const found = r.objects.find(o => o.id === params.object_id);
              if (found) { sourceRoom = r; obj = found; break; }
            }
            if (!sourceRoom || !obj) return { content: [{ type: "text", text: "Object not found." }] };
            const targetRoom = interior.rooms.find(r => r.id === params.target_room);
            if (!targetRoom) return { content: [{ type: "text", text: "Target room not found." }] };
            // Remove from source
            if (obj.located_on) {
              const parent = sourceRoom.objects.find(o => o.id === obj!.located_on);
              if (parent?.items_on) parent.items_on = parent.items_on.filter(id => id !== params.object_id);
            }
            sourceRoom.objects = sourceRoom.objects.filter(o => o.id !== params.object_id);
            delete obj.located_on;
            // Place on target furniture if specified
            if (params.place_on) {
              const newParent = targetRoom.objects.find(o => o.id === params.place_on);
              if (newParent) {
                obj.located_on = params.place_on;
                if (!newParent.items_on) newParent.items_on = [];
                newParent.items_on.push(obj.id);
              }
            }
            targetRoom.objects.push(obj);
            await writeJson(paths.interior, interior);
            return { content: [{ type: "text", text: `${lang === "de" ? "Objekt verschoben nach" : "Object moved to"} ${targetRoom.name}.` }] };
          }

          case "describe": {
            const isDe = lang === "de";
            if (params.object_id) {
              for (const r of interior.rooms) {
                const obj = r.objects.find(o => o.id === params.object_id);
                if (obj) {
                  const lines = [
                    `**${obj.name}** (${obj.id})`, 
                    `${isDe ? "Kategorie" : "Category"}: ${obj.category}`, 
                    `${isDe ? "Beschreibung" : "Description"}: ${obj.description || "-"}`
                  ];
                  if (obj.images.length > 0) lines.push(`${isDe ? "Bilder" : "Images"}: ${obj.images.join(", ")}`);
                  if (obj.items_on && obj.items_on.length > 0) {
                    const subs = obj.items_on.map(id => r.objects.find(o => o.id === id)?.name ?? id);
                    lines.push(`${isDe ? "Darauf" : "Items on this"}: ${subs.join(", ")}`);
                  }
                  lines.push(`${isDe ? "Raum" : "Room"}: ${r.name}`);
                  return { content: [{ type: "text", text: lines.join("\n") }] };
                }
              }
              return { content: [{ type: "text", text: isDe ? "Objekt nicht gefunden." : "Object not found." }] };
            }
            if (params.room_id) {
              const r = interior.rooms.find(rm => rm.id === params.room_id);
              if (!r) return { content: [{ type: "text", text: isDe ? "Raum nicht gefunden." : "Room not found." }] };
              return { content: [{ type: "text", text: `**${r.name}** (${r.id})\n${r.description || "-"}\n${isDe ? "Objekte" : "Objects"}: ${r.objects.length}` }] };
            }
            return { content: [{ type: "text", text: isDe ? "object_id oder room_id erforderlich." : "object_id or room_id required." }] };
          }

          default:
            return { content: [{ type: "text", text: `Unknown action: ${params.action}` }] };
        }
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_inventory
    // -------------------------------------------------------------------
    api.registerTool({
      name: "reality_inventory",
      description: "Manage your personal inventory of items",
      parameters: Type.Object({
        action: Type.String({ description: "Action: list | add | remove | update | search | use" }),
        item_id: Type.Optional(Type.String()),
        name: Type.Optional(Type.String()),
        category: Type.Optional(Type.String()),
        description: Type.Optional(Type.String()),
        quantity: Type.Optional(Type.Number()),
        location: Type.Optional(Type.String({ description: "room_id/object_id soft-link" })),
        tags: Type.Optional(Type.Array(Type.String())),
        query: Type.Optional(Type.String({ description: "Search query for name/tags/description" })),
      }),
      async execute(_id: string, params: InventoryParams) {
        let inv = await readJson<Inventory>(paths.inventory);
        if (!inv) inv = { items: [], categories: [] };
        const isDe = lang === "de";

        switch (params.action) {
          case "use": {
            // Phase 6: Utility - Use item
            if (!params.item_id) return { content: [{ type: "text", text: "item_id required." }] };
            const item = inv.items.find(i => i.id === params.item_id);
            if (!item) return { content: [{ type: "text", text: "Item not found." }] };
            
            if (item.quantity <= 0) return { content: [{ type: "text", text: isDe ? "Leer." : "Empty." }] };
            
            const ph = await readJson<Physique>(paths.physique);
            let effectMsg = "";
            
            if (item.effects && ph) {
              if (item.effects.energy) ph.needs.energy = Math.min(100, ph.needs.energy + item.effects.energy);
              if (item.effects.stress) ph.needs.stress = Math.max(0, ph.needs.stress - item.effects.stress);
              if (item.effects.hunger) ph.needs.hunger = Math.max(0, ph.needs.hunger - item.effects.hunger);
              await writeJson(paths.physique, ph);
              effectMsg = isDe 
                ? `Effekte angewendet: Energie ${item.effects.energy ? "+" + item.effects.energy : "0"}, Stress ${item.effects.stress ? "-" + item.effects.stress : "0"}.`
                : `Effects applied: Energy ${item.effects.energy ? "+" + item.effects.energy : "0"}, Stress ${item.effects.stress ? "-" + item.effects.stress : "0"}.`;
            }
            
            item.quantity--;
            if (item.quantity === 0) {
               // Optional: remove item or keep as 0? Keep as 0 for history.
            }
            await writeJson(paths.inventory, inv);
            
            return { content: [{ type: "text", text: isDe ? `${item.name} benutzt. ${effectMsg}` : `Used ${item.name}. ${effectMsg}` }] };
          }

          case "list": {
            if (inv.items.length === 0) {
              return { content: [{ type: "text", text: lang === "de" ? "Inventar ist leer." : "Inventory is empty." }] };
            }
            const filtered = params.category
              ? inv.items.filter(i => i.category === params.category)
              : inv.items;
            const lines = filtered.map(i => `- ${i.name} (${i.id}) x${i.quantity} [${i.category}]${i.location ? ` @ ${i.location}` : ""}`);
            return { content: [{ type: "text", text: lines.join("\n") }] };
          }

          case "add": {
            if (!params.name) return { content: [{ type: "text", text: "name required." }] };
            const newItem: InventoryItem = {
              id: generateId("inv"),
              name: params.name,
              category: params.category ?? "other",
              description: params.description ?? "",
              quantity: params.quantity ?? 1,
              location: params.location,
              images: [],
              tags: params.tags ?? [],
              added_at: new Date().toISOString(),
            };
            inv.items.push(newItem);
            if (newItem.category && !inv.categories.includes(newItem.category)) {
              inv.categories.push(newItem.category);
            }
            await writeJson(paths.inventory, inv);
            return { content: [{ type: "text", text: `${lang === "de" ? "Hinzugefuegt" : "Added"}: ${newItem.name} (${newItem.id})` }] };
          }

          case "remove": {
            if (!params.item_id) return { content: [{ type: "text", text: "item_id required." }] };
            const idx = inv.items.findIndex(i => i.id === params.item_id);
            if (idx < 0) return { content: [{ type: "text", text: "Item not found." }] };
            inv.items.splice(idx, 1);
            await writeJson(paths.inventory, inv);
            return { content: [{ type: "text", text: lang === "de" ? "Entfernt." : "Removed." }] };
          }

          case "update": {
            if (!params.item_id) return { content: [{ type: "text", text: "item_id required." }] };
            const item = inv.items.find(i => i.id === params.item_id);
            if (!item) return { content: [{ type: "text", text: "Item not found." }] };
            if (params.name !== undefined) item.name = params.name;
            if (params.category !== undefined) item.category = params.category;
            if (params.description !== undefined) item.description = params.description;
            if (params.quantity !== undefined) item.quantity = params.quantity;
            if (params.location !== undefined) item.location = params.location;
            if (params.tags !== undefined) item.tags = params.tags;
            await writeJson(paths.inventory, inv);
            return { content: [{ type: "text", text: `${lang === "de" ? "Aktualisiert" : "Updated"}: ${item.name}` }] };
          }

          case "search": {
            if (!params.query) return { content: [{ type: "text", text: "query required." }] };
            const q = params.query.toLowerCase();
            const results = inv.items.filter(i =>
              i.name.toLowerCase().includes(q) ||
              i.description.toLowerCase().includes(q) ||
              i.tags.some(t => t.toLowerCase().includes(q))
            );
            if (results.length === 0) {
              return { content: [{ type: "text", text: lang === "de" ? "Keine Treffer." : "No matches." }] };
            }
            const lines = results.map(i => `- ${i.name} (${i.id}) x${i.quantity} [${i.category}]`);
            return { content: [{ type: "text", text: lines.join("\n") }] };
          }

          default:
            return { content: [{ type: "text", text: `Unknown action: ${params.action}` }] };
        }
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_skill (Phase 6)
    // -------------------------------------------------------------------
    if (modules.skills) api.registerTool({
      name: "reality_skill",
      description: "Train skills or check competence level (Phase 6)",
      parameters: Type.Object({
        action: Type.String({ description: "Action: train | check | list" }),
        skill_name: Type.Optional(Type.String({ description: "Name of the skill to train/check" })),
        duration: Type.Optional(Type.Number({ description: "Training duration in minutes" })),
      }),
      async execute(_id: string, params: SkillParams) {
        let skills = await readJson<SkillState>(paths.skills);
        if (!skills) skills = { skills: [], total_xp: 0 };

        const isDe = lang === "de";

        switch (params.action) {
          case "train": {
            if (!params.skill_name || !params.duration) return { content: [{ type: "text", text: "skill_name and duration required." }] };
            let skill = skills.skills.find(s => s.name.toLowerCase() === params.skill_name!.toLowerCase());
            if (!skill) {
              skill = {
                id: generateId("skill"),
                name: params.skill_name,
                level: 1,
                xp: 0,
                xp_to_next: 100,
                last_trained: new Date().toISOString()
              };
              skills.skills.push(skill);
            }
            
            // Calculate XP gain (1 XP per minute base)
            const xpGain = Math.round(params.duration * 1.5);
            skill.xp += xpGain;
            skill.last_trained = new Date().toISOString();
            skills.total_xp += xpGain;

            let levelUpMsg = "";
            if (skill.xp >= skill.xp_to_next) {
              skill.level++;
              skill.xp -= skill.xp_to_next;
              skill.xp_to_next = Math.round(skill.xp_to_next * 1.5);
              levelUpMsg = isDe ? `\n🎉 LEVEL AUFSTIEG! ${skill.name} ist jetzt Level ${skill.level}.` : `\n🎉 LEVEL UP! ${skill.name} is now Level ${skill.level}.`;
            }

            await writeJson(paths.skills, skills);
            
            // Consume energy/stress
            const ph = await readJson<Physique>(paths.physique);
            if (ph) {
              ph.needs.energy = Math.max(0, ph.needs.energy - Math.round(params.duration / 5));
              ph.needs.stress = Math.min(100, ph.needs.stress + Math.round(params.duration / 10));
              await writeJson(paths.physique, ph);
            }

            return { content: [{ type: "text", text: isDe 
              ? `${params.skill_name} trainiert fuer ${params.duration}min. +${xpGain} XP.${levelUpMsg}` 
              : `Trained ${params.skill_name} for ${params.duration}min. +${xpGain} XP.${levelUpMsg}` }] };
          }

          case "list": {
            if (skills.skills.length === 0) return { content: [{ type: "text", text: isDe ? "Keine Skills gelernt." : "No skills learned." }] };
            const lines = skills.skills.map(s => `- ${s.name}: Lvl ${s.level} (${s.xp}/${s.xp_to_next} XP)`);
            return { content: [{ type: "text", text: lines.join("\n") }] };
          }

          default:
            return { content: [{ type: "text", text: "Unknown action." }] };
        }
      }
    });

    // -------------------------------------------------------------------
    // Tool: reality_desktop (Phase 6)
    // -------------------------------------------------------------------
    if (modules.desktop) api.registerTool({
      name: "reality_desktop",
      description: "Control desktop environment (wallpaper, theme) - Requires Gnome/Linux",
      parameters: Type.Object({
        action: Type.String({ description: "Action: set_wallpaper | set_theme | get_info" }),
        path: Type.Optional(Type.String({ description: "Path to wallpaper image" })),
        theme: Type.Optional(Type.String({ description: "Theme: dark | light" })),
      }),
      async execute(_id: string, params: DesktopParams) {
        // Safe wrapper for shell execution
        const isDe = lang === "de";
        
        switch (params.action) {
          case "set_wallpaper": {
            if (!params.path) return { content: [{ type: "text", text: "path required." }] };
            // Simple validation to prevent command injection
            if (params.path.includes(";") || params.path.includes("&")) return { content: [{ type: "text", text: "Invalid path security check." }] };
            
            // Create a safe script to execute
            const scriptPath = join(ws, "scripts", "set_wallpaper.sh");
            const scriptContent = `#!/bin/bash\n# Generated by Project Genesis\ngsettings set org.gnome.desktop.background picture-uri "file://${params.path}"\ngsettings set org.gnome.desktop.background picture-uri-dark "file://${params.path}"\n`;
            
            try {
              await fs.mkdir(dirname(scriptPath), { recursive: true });
              await fs.writeFile(scriptPath, scriptContent, { mode: 0o755 });
              // We don't execute it directly for safety, we return the instruction
              return { content: [{ type: "text", text: isDe 
                ? `Befehl vorbereitet. Führe aus: ${scriptPath}` 
                : `Command prepared. Execute: ${scriptPath}` }] };
            } catch (e) {
              return { content: [{ type: "text", text: `Error: ${e}` }] };
            }
          }
          default:
            return { content: [{ type: "text", text: "Unknown action." }] };
        }
      }
    });

    // -------------------------------------------------------------------
    // Tool: reality_develop
    // -------------------------------------------------------------------
    api.registerTool({
      name: "reality_develop",
      description: "Create and manage self-developed tools, skills, and scripts (Developer role)",
      parameters: Type.Object({
        action: Type.String({ description: "Action: init_project | create_project | write_code | read_file | list_projects | run_test | submit_review | status | delete_project" }),
        project_id: Type.Optional(Type.String()),
        project_name: Type.Optional(Type.String()),
        project_type: Type.Optional(Type.String({ description: "Project type: tool | skill | plugin | script" })),
        project_description: Type.Optional(Type.String()),
        file_path: Type.Optional(Type.String({ description: "Relative path within project src/" })),
        file_content: Type.Optional(Type.String()),
      }),
      async execute(_id: string, params: DevelopParams) {
        if (cfg?.development?.enabled === false) {
          return { content: [{ type: "text", text: "Development module is disabled." }] };
        }

        let manifest = await readJson<DevManifest>(paths.devManifest);
        if (!manifest) manifest = { projects: [] };

        switch (params.action) {
          case "list_projects": {
            if (manifest.projects.length === 0) {
              return { content: [{ type: "text", text: lang === "de" ? "Keine Projekte." : "No projects." }] };
            }
            const lines = manifest.projects.map(p =>
              `- ${p.name} (${p.id}) [${p.type}] status=${p.status} approved=${p.approved}`
            );
            return { content: [{ type: "text", text: lines.join("\n") }] };
          }

          case "create_project":
          case "init_project": {
            // Both actions create a new project, but init_project scaffolds a full directory structure
            if (!params.project_name || !params.project_type) {
              return { content: [{ type: "text", text: "project_name and project_type required." }] };
            }
            const validProjectTypes = ["tool", "skill", "plugin", "script"];
            if (!validProjectTypes.includes(params.project_type)) {
              return { content: [{ type: "text", text: `Invalid project_type. Valid: ${validProjectTypes.join(", ")}` }] };
            }
            const projId = generateId("dev");
            const projRoot = join(paths.devProjects, projId);
            const projDir = join(projRoot, "src");
            const testsDir = join(projRoot, "tests");

            // Create directory structure
            await fs.mkdir(projDir, { recursive: true });
            if (params.action === "init_project") {
              await fs.mkdir(testsDir, { recursive: true });
              // Create README.md template
              const readme = `# ${params.project_name}

## Description
${params.project_description || "Self-developed tool/script"}

## Type
${params.project_type}

## Created
${new Date().toISOString()}

## Status
- Draft -> Pending Review -> Approved -> Active

## Usage
See source files in \`src/\`
`;
              await fs.writeFile(join(projRoot, "README.md"), readme);
            }

            const validTypes = ["tool", "skill", "plugin", "script"];
            const projType = (validTypes.includes(params.project_type ?? "") ? params.project_type : "tool") as DevProject["type"];

            const project: DevProject = {
              id: projId,
              name: params.project_name,
              type: projType,
              status: "draft",
              description: params.project_description ?? "",
              files: [],
              created_at: new Date().toISOString(),
              approved: false,
              approved_at: null,
              test_results: [],
            };

            // Write meta.json
            await writeJson(join(projRoot, "meta.json"), project);
            manifest.projects.push(project);
            await writeJson(paths.devManifest, manifest);

            // Activity logging
            await logAgentActivity(
              paths.agentActivity,
              "developer",
              "developer",
              "PROJECT_CREATED",
              `Developer created project ${project.name} (${projId})`,
              { projectId: projId, projectType: projType, scaffolded: params.action === "init_project" }
            );

            const actionWord = params.action === "init_project" ? (lang === "de" ? "initialisiert" : "initialized") : (lang === "de" ? "erstellt" : "created");
            return { content: [{ type: "text", text: lang === "de" ? `Projekt ${actionWord}: ${project.name} (${projId}). Nutze write_code um Dateien hinzuzufuegen, dann submit_review wenn fertig.` : `Project ${actionWord}: ${project.name} (${projId}). Use write_code to add files, then submit_review when ready.` }] };
          }

          case "run_test": {
            // Validate TypeScript syntax or JSON structure of the code
            if (!params.project_id) {
              return { content: [{ type: "text", text: "project_id required." }] };
            }
            const testProj = manifest.projects.find(p => p.id === params.project_id);
            if (!testProj) {
              return { content: [{ type: "text", text: lang === "de" ? "Projekt nicht gefunden." : "Project not found." }] };
            }
            if (testProj.files.length === 0) {
              return { content: [{ type: "text", text: lang === "de" ? "Keine Dateien zum Testen. Schreibe zuerst Code mit write_code." : "No files to test. Write code first using write_code." }] };
            }

            const testResults: DevTestResult[] = [];
            let allPassed = true;

            for (const file of testProj.files) {
              try {
                // Path traversal guard
                const baseDirRaw = resolve(paths.devProjects, params.project_id);
                const baseDir = await fs.realpath(baseDirRaw).catch(() => baseDirRaw);
                const filePath = resolve(baseDir, "src", file);

                if (!filePath.startsWith(baseDir + "/")) {
                  testResults.push({
                    timestamp: new Date().toISOString(),
                    status: "error",
                    message: lang === "de" ? `Path traversal in ${file} erkannt` : `Path traversal detected in ${file}`,
                    details: "Security violation"
                  });
                  allPassed = false;
                  continue;
                }

                const content = await fs.readFile(filePath, "utf-8");

                // Basic validation: Check for common issues
                if (file.endsWith(".json")) {
                  try {
                    JSON.parse(content);
                    testResults.push({
                      timestamp: new Date().toISOString(),
                      status: "pass",
                      message: `${file}: ${lang === "de" ? "Validiertes JSON" : "Valid JSON"}`,
                    });
                  } catch (e) {
                    testResults.push({
                      timestamp: new Date().toISOString(),
                      status: "fail",
                      message: `${file}: ${lang === "de" ? "Ungueltiges JSON" : "Invalid JSON"}`,
                      details: String(e)
                    });
                    allPassed = false;
                  }
                } else if (file.endsWith(".ts")) {
                  // Basic TypeScript syntax check via node --check (if available)
                  // For now, do a basic brace matching check
                  const openBraces = (content.match(/\{/g) || []).length;
                  const closeBraces = (content.match(/\}/g) || []).length;
                  const openParens = (content.match(/\(/g) || []).length;
                  const closeParens = (content.match(/\)/g) || []).length;

                  if (openBraces === closeBraces && openParens === closeParens) {
                    testResults.push({
                      timestamp: new Date().toISOString(),
                      status: "pass",
                      message: `${file}: ${lang === "de" ? "Basaler Syntax-Check bestanden (Klammern)" : "Basic syntax check passed (brace matching)"}`,
                    });
                  } else {
                    testResults.push({
                      timestamp: new Date().toISOString(),
                      status: "fail",
                      message: `${file}: ${lang === "de" ? "Klammer-Fehler" : "Brace/paren mismatch"}`,
                      details: `Braces: {${openBraces} vs ${closeBraces}}, Parens: (${openParens} vs ${closeParens})`
                    });
                    allPassed = false;
                  }
                } else {
                  // Other files - just check they're readable
                  testResults.push({
                    timestamp: new Date().toISOString(),
                    status: "pass",
                    message: `${file}: ${lang === "de" ? "Lesbar" : "Readable"} (${content.length} bytes)`,
                  });
                }
              } catch (e) {
                testResults.push({
                  timestamp: new Date().toISOString(),
                  status: "error",
                  message: lang === "de" ? `Fehler beim Lesen von ${file}` : `Failed to read ${file}`,
                  details: String(e)
                });
                allPassed = false;
              }
            }

            // Update project with test results
            testProj.test_results = testResults;
            testProj.last_test_run = new Date().toISOString();
            await writeJson(join(paths.devProjects, params.project_id, "meta.json"), testProj);

            // Activity logging
            await logAgentActivity(
              paths.agentActivity,
              "developer",
              "developer",
              "TEST_RUN",
              `Developer ran tests on ${testProj.name}: ${allPassed ? "ALL PASSED" : "SOME FAILED"}`,
              { projectId: params.project_id, resultCount: testResults.length, allPassed }
            );

            // Format output
            const isDe = lang === "de";
            const lines = [isDe ? `**Testergebnisse fuer ${testProj.name}**` : `**Test Results for ${testProj.name}**`, ""];
            for (const r of testResults) {
              const icon = r.status === "pass" ? "✅" : r.status === "fail" ? "❌" : "⚠️";
              lines.push(`${icon} ${r.message}`);
              if (r.details) lines.push(`   ${isDe ? "Details" : "Details"}: ${r.details}`);
            }
            lines.push("");
            lines.push(allPassed ? (isDe ? "✅ Alle Tests bestanden!" : "✅ All tests passed!") : (isDe ? "❌ Einige Tests sind fehlgeschlagen. Behebe die Fehler vor dem Review." : "❌ Some tests failed. Fix issues before submitting for review."));

            return { content: [{ type: "text", text: lines.join("\n") }] };
          }

          case "write_code":
          case "write_file": {
            if (!params.project_id || !params.file_path || params.file_content === undefined) {
              return { content: [{ type: "text", text: "project_id, file_path, and file_content required." }] };
            }
            if (params.file_content.length > 10 * 1024 * 1024) {
              return { content: [{ type: "text", text: lang === "de" ? "Dateiinhalt ueberschreitet 10 MB Limit." : "File content exceeds 10 MB limit." }] };
            }
            const proj = manifest.projects.find(p => p.id === params.project_id);
            if (!proj) return { content: [{ type: "text", text: lang === "de" ? "Projekt nicht gefunden." : "Project not found." }] };
            // Path traversal guard — realpath() follows symlinks, resolve() normalizes ".." segments
            const baseDirRaw = resolve(paths.devProjects, params.project_id);
            const baseDir = await fs.realpath(baseDirRaw).catch(() => baseDirRaw);
            const targetPath = resolve(baseDir, "src", params.file_path);
            if (!targetPath.startsWith(baseDir + "/")) {
              // Activity logging for blocked attempt
              await logAgentActivity(
                paths.agentActivity,
                "developer",
                "developer",
                "WRITE_BLOCKED",
                `Developer attempted path traversal in ${params.file_path}`,
                { projectId: params.project_id, filePath: params.file_path, blocked: true }
              );
              return { content: [{ type: "text", text: lang === "de" ? "Path traversal erkannt — blockiert." : "Path traversal detected — blocked." }] };
            }
            await fs.mkdir(dirname(targetPath), { recursive: true });
            await fs.writeFile(targetPath, params.file_content);
            const isNewFile = !proj.files.includes(params.file_path);
            if (isNewFile) {
              proj.files.push(params.file_path);
              await writeJson(join(baseDir, "meta.json"), proj);
              await writeJson(paths.devManifest, manifest);
            }

            // Activity logging
            await logAgentActivity(
              paths.agentActivity,
              "developer",
              "developer",
              isNewFile ? "FILE_CREATED" : "FILE_UPDATED",
              `Developer ${isNewFile ? "created" : "updated"} ${params.file_path} in ${proj.name}`,
              { projectId: params.project_id, filePath: params.file_path, fileSize: params.file_content.length }
            );

            return { content: [{ type: "text", text: lang === "de" ? `Datei geschrieben: ${params.file_path} (${params.file_content.length} bytes)` : `File written: ${params.file_path} (${params.file_content.length} bytes)` }] };
          }

          case "read_file": {
            if (!params.project_id || !params.file_path) {
              return { content: [{ type: "text", text: "project_id and file_path required." }] };
            }
            // Path traversal guard — realpath() follows symlinks on both base dir and target file
            const baseDirRaw2 = resolve(paths.devProjects, params.project_id);
            const baseDir2 = await fs.realpath(baseDirRaw2).catch(() => baseDirRaw2);
            const filePath = resolve(baseDir2, "src", params.file_path);
            if (!filePath.startsWith(baseDir2 + "/")) {
              return { content: [{ type: "text", text: lang === "de" ? "Path traversal erkannt — blockiert." : "Path traversal detected — blocked." }] };
            }
            try {
              // Resolve symlinks in the final path to catch symlink-based traversal
              const fileReal = await fs.realpath(filePath);
              if (!fileReal.startsWith(baseDir2 + "/")) {
                return { content: [{ type: "text", text: lang === "de" ? "Path traversal erkannt (Symlink) — blockiert." : "Path traversal detected (symlink) — blocked." }] };
              }
              const content = await fs.readFile(fileReal, "utf-8");
              return { content: [{ type: "text", text: content }] };
            } catch {
              return { content: [{ type: "text", text: lang === "de" ? "Datei nicht gefunden." : "File not found." }] };
            }
          }

          case "submit_review": {
            if (!params.project_id) return { content: [{ type: "text", text: "project_id required." }] };
            const proj2 = manifest.projects.find(p => p.id === params.project_id);
            if (!proj2) return { content: [{ type: "text", text: lang === "de" ? "Projekt nicht gefunden." : "Project not found." }] };
            proj2.status = "pending_review";
            await writeJson(join(paths.devProjects, params.project_id, "meta.json"), proj2);
            await writeJson(paths.devManifest, manifest);

            // Activity logging
            await logAgentActivity(
              paths.agentActivity,
              "developer",
              "developer",
              "SUBMITTED_FOR_REVIEW",
              `Developer submitted ${proj2.name} for review (${proj2.files.length} files)`,
              { projectId: params.project_id, fileCount: proj2.files.length }
            );

            return { content: [{ type: "text", text: lang === "de" ? `Zum Review eingereicht: ${proj2.name}. Warte auf Analyst-Freigabe.` : `Submitted for review: ${proj2.name}. Waiting for Analyst approval.` }] };
          }

          case "status": {
            if (!params.project_id) return { content: [{ type: "text", text: "project_id required." }] };
            const proj3 = manifest.projects.find(p => p.id === params.project_id);
            if (!proj3) return { content: [{ type: "text", text: lang === "de" ? "Projekt nicht gefunden." : "Project not found." }] };
            const isDe = lang === "de";
            const lines = [
              `**${proj3.name}** (${proj3.id})`,
              `${isDe ? "Typ" : "Type"}: ${proj3.type}`,
              `Status: ${proj3.status}`,
              `${isDe ? "Freigegeben" : "Approved"}: ${proj3.approved}`,
              `${isDe ? "Dateien" : "Files"}: ${proj3.files.join(", ") || (isDe ? "keine" : "none")}`,
              `${isDe ? "Erstellt" : "Created"}: ${proj3.created_at}`,
            ];
            if (proj3.description) lines.push(`${isDe ? "Beschreibung" : "Description"}: ${proj3.description}`);
            return { content: [{ type: "text", text: lines.join("\n") }] };
          }

          case "delete_project": {
            if (!params.project_id) return { content: [{ type: "text", text: "project_id required." }] };
            const idx = manifest.projects.findIndex(p => p.id === params.project_id);
            if (idx < 0) return { content: [{ type: "text", text: lang === "de" ? "Projekt nicht gefunden." : "Project not found." }] };
            const deletedProj = manifest.projects[idx];
            // Remove project directory (with path-traversal guard)
            const projDir2Raw = resolve(paths.devProjects, params.project_id);
            const projDir2 = await fs.realpath(projDir2Raw).catch(() => projDir2Raw);
            if (!projDir2.startsWith(paths.devProjects + "/")) {
              return { content: [{ type: "text", text: "Blocked: path traversal detected." }] };
            }
            await fs.rm(projDir2, { recursive: true, force: true });
            manifest.projects.splice(idx, 1);
            await writeJson(paths.devManifest, manifest);

            // Activity logging
            await logAgentActivity(
              paths.agentActivity,
              "developer",
              "developer",
              "PROJECT_DELETED",
              `Developer deleted project ${deletedProj.name}`,
              { projectId: params.project_id, projectName: deletedProj.name }
            );

            return { content: [{ type: "text", text: lang === "de" ? `Projekt geloescht: ${deletedProj.name}` : `Project deleted: ${deletedProj.name}` }] };
          }

          default:
            return { content: [{ type: "text", text: `Unknown action: ${params.action}` }] };
        }
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_review_project — Analyst Review System
    // -------------------------------------------------------------------
    api.registerTool({
      name: "reality_review_project",
      description: "Review and approve/reject self-developed projects (Analyst role only)",
      parameters: Type.Object({
        action: Type.String({ description: "Action: approve | reject | list_pending | list_approved" }),
        project_id: Type.Optional(Type.String()),
        feedback: Type.Optional(Type.String({ description: "Feedback message for the developer" })),
        auto_load: Type.Optional(Type.Boolean({ description: "Auto-load the tool after approval" })),
      }),
      async execute(_id: string, params: ReviewParams) {
        // This tool is analyst-only - in production, enforce via RoleGuard
        const manifest = await readJson<DevManifest>(paths.devManifest);
        if (!manifest) return { content: [{ type: "text", text: lang === "de" ? "Keine Projekte gefunden." : "No projects found." }] };

        const isDe = lang === "de";

        switch (params.action) {
          case "list_pending": {
            const pending = manifest.projects.filter(p => p.status === "pending_review");
            if (pending.length === 0) {
              return { content: [{ type: "text", text: isDe ? "Keine Projekte warten auf Freigabe." : "No projects pending review." }] };
            }
            const lines = [isDe ? "**Wartende Projekte:**" : "**Pending Review Projects:**", ""];
            for (const p of pending) {
              lines.push(`- **${p.name}** (${p.id})`);
              lines.push(`  ${isDe ? "Typ" : "Type"}: ${p.type}, ${isDe ? "Dateien" : "Files"}: ${p.files.length}`);
              if (p.description) lines.push(`  ${isDe ? "Beschreibung" : "Description"}: ${p.description}`);
              if (p.last_test_run) lines.push(`  ${isDe ? "Letzter Test" : "Last Test"}: ${p.last_test_run}`);
              lines.push("");
            }
            return { content: [{ type: "text", text: lines.join("\n") }] };
          }

          case "list_approved": {
            const approved = manifest.projects.filter(p => p.status === "approved" || p.status === "active");
            if (approved.length === 0) {
              return { content: [{ type: "text", text: isDe ? "Keine freigegebenen Projekte." : "No approved projects." }] };
            }
            const lines = [isDe ? "**Freigegebene Projekte:**" : "**Approved Projects:**", ""];
            for (const p of approved) {
              lines.push(`- **${p.name}** (${p.id}) [${p.status}]`);
              lines.push(`  ${isDe ? "Typ" : "Type"}: ${p.type}, ${isDe ? "Dateien" : "Files"}: ${p.files.length}`);
              if (p.approved_at) lines.push(`  ${isDe ? "Freigabe" : "Approved"}: ${p.approved_at}`);
              lines.push("");
            }
            return { content: [{ type: "text", text: lines.join("\n") }] };
          }

          case "approve": {
            if (!params.project_id) {
              return { content: [{ type: "text", text: "project_id required." }] };
            }
            const proj = manifest.projects.find(p => p.id === params.project_id);
            if (!proj) {
              return { content: [{ type: "text", text: isDe ? "Projekt nicht gefunden." : "Project not found." }] };
            }
            if (proj.status !== "pending_review") {
              return { content: [{ type: "text", text: isDe ? `Projekt wartet nicht auf Freigabe. Status: ${proj.status}` : `Project is not pending review. Current status: ${proj.status}` }] };
            }

            // Approve the project
            proj.status = "approved";
            proj.approved = true;
            proj.approved_at = new Date().toISOString();
            proj.review_feedback = params.feedback ?? (isDe ? "Durch Analyst freigegeben" : "Approved by Analyst");
            proj.auto_load = params.auto_load ?? true;

            // Update both manifest and project meta.json
            await writeJson(paths.devManifest, manifest);
            await writeJson(join(paths.devProjects, params.project_id, "meta.json"), proj);

            // Activity logging
            await logAgentActivity(
              paths.agentActivity,
              "analyst",
              "analyst",
              "PROJECT_APPROVED",
              `Analyst approved project ${proj.name}`,
              { projectId: params.project_id, projectName: proj.name, autoLoad: proj.auto_load, feedback: params.feedback }
            );

            // Send memo to developer
            await sendMemo(
              paths.internalComm,
              "analyst",
              "developer",
              "strategy",
              isDe 
                ? `Dein Projekt "${proj.name}" wurde freigegeben! Du kannst es jetzt in der Simulation nutzen.`
                : `Your project "${proj.name}" has been approved! You can now use it in the simulation.`,
              "high",
              cfg?.memoTTL ?? 7
            );

            const loadMsg = proj.auto_load 
              ? (isDe ? " Es wird beim naechsten Agent-Turn automatisch geladen." : " It will be auto-loaded on next agent turn.") 
              : "";
            return { content: [{ type: "text", text: isDe ? `Projekt freigegeben: ${proj.name}.${loadMsg}` : `Project approved: ${proj.name}.${loadMsg}` }] };
          }

          case "reject": {
            if (!params.project_id) {
              return { content: [{ type: "text", text: "project_id required." }] };
            }
            const proj = manifest.projects.find(p => p.id === params.project_id);
            if (!proj) {
              return { content: [{ type: "text", text: isDe ? "Projekt nicht gefunden." : "Project not found." }] };
            }
            if (proj.status !== "pending_review") {
              return { content: [{ type: "text", text: isDe ? `Projekt wartet nicht auf Freigabe. Status: ${proj.status}` : `Project is not pending review. Current status: ${proj.status}` }] };
            }

            proj.status = "draft";
            proj.approved = false;
            proj.review_feedback = params.feedback ?? (isDe ? "Abgelehnt durch Analyst" : "Rejected by Analyst");

            await writeJson(paths.devManifest, manifest);
            await writeJson(join(paths.devProjects, params.project_id, "meta.json"), proj);

            // Activity logging
            await logAgentActivity(
              paths.agentActivity,
              "analyst",
              "analyst",
              "PROJECT_REJECTED",
              `Analyst rejected project ${proj.name}`,
              { projectId: params.project_id, projectName: proj.name, feedback: params.feedback }
            );

            // Send memo to developer
            await sendMemo(
              paths.internalComm,
              "analyst",
              "developer",
              "warning",
              isDe 
                ? `Dein Projekt "${proj.name}" wurde abgelehnt. Feedback: ${proj.review_feedback}`
                : `Your project "${proj.name}" was rejected. Feedback: ${proj.review_feedback}`,
              "high",
              cfg?.memoTTL ?? 7
            );

            return { content: [{ type: "text", text: isDe ? `Projekt abgelehnt: ${proj.name}. Entwickler wurde benachrichtigt.` : `Project rejected: ${proj.name}. Developer notified.` }] };
          }

          default:
            return { content: [{ type: "text", text: "Invalid action. Valid: approve, reject, list_pending, list_approved" }] };
        }
      },
    });

    // -------------------------------------------------------------------
    // Dev-Project Auto-Loader
    // -------------------------------------------------------------------
    let devToolsLoaded = 0;
    if (cfg?.development?.auto_load_approved !== false) {
      const devManifest = await readJson<DevManifest>(paths.devManifest);
      if (devManifest?.projects) {
        for (const proj of devManifest.projects.filter(p => p.approved && p.status === "approved" && p.type === "tool")) {
          // Path-traversal guard: proj.id must not escape devProjects directory.
          // Protects against a manipulated manifest.json with e.g. id: "../../evil".
          const projLoadDir = resolve(paths.devProjects, proj.id);
          if (!projLoadDir.startsWith(paths.devProjects + "/")) {
            api.logger.warn(`[genesis] Dev tool ${proj.id} blocked: path traversal in project ID.`);
            continue;
          }
          try {
            const toolModule = await import(resolve(projLoadDir, "src", "index.ts"));
            if (toolModule.default?.name && toolModule.default?.execute) {
              api.registerTool(toolModule.default);
              devToolsLoaded++;
              api.logger.info(`[genesis] Dev tool loaded: ${toolModule.default.name}`);
            }
          } catch (err) {
            api.logger.warn(`[genesis] Dev tool ${proj.id} failed: ${err}`);
          }
        }
      }
    }

    // -------------------------------------------------------------------
    // Phase 2: Social Fabric Tools
    // -------------------------------------------------------------------

    // Load social state
    let socialState = await readJson<SocialState>(paths.social);
    if (!socialState) {
      socialState = getDefaultSocialState();
      await writeJson(paths.social, socialState);
    }

    // Social decay is now handled in before_prompt_build hook with 24h guard

    // -------------------------------------------------------------------
    // Phase 3: Prosperity & Labor - Economy Tools
    // -------------------------------------------------------------------

    const now = new Date();

    // Load finance state
    let financeState = await readJson<FinanceState>(paths.finances);
    if (!financeState) {
      financeState = getDefaultFinanceState(cfg?.initialBalance ?? 1000);
      await writeJson(paths.finances, financeState);
    }

    // Process recurring expenses and debt interest (economic tick)
    const expenseEvents = processRecurringExpenses(financeState, now);
    const debtEvents = processDebtInterest(financeState, now);
    const allEvents = [...expenseEvents, ...debtEvents];

    // Log economy events to telemetry
    for (const event of allEvents) {
      await appendJsonl(join(paths.economyTelemetry, `events_${now.toISOString().slice(0, 10)}.jsonl`), event);
    }

    // Check for financial crisis
    const hasCrisis = allEvents.some(e => e.event_type === "crisis");
    if (hasCrisis) {
      api.logger.warn("[genesis] Financial crisis detected - insufficient funds for expenses!");
    }

    // Update net worth
    const totalDebt = financeState.debts.reduce((sum, d) => sum + d.current_balance, 0);
    financeState.net_worth = financeState.balance - totalDebt;
    await writeJson(paths.finances, financeState);

    // Track job listings (in-memory for this session)
    let currentJobListings: ReturnType<typeof generateJobListings> = [];

    api.registerTool({
      name: "reality_socialize",
      description: "Interact with social entities - talk, give gifts, resolve conflicts, or show support",
      parameters: Type.Object({
        target_id: Type.Optional(Type.String({ description: "ID of existing entity to interact with" })),
        target_name: Type.Optional(Type.String({ description: "Name of new entity to create (if target_id not provided)" })),
        action: Type.String({ description: "Action: talk | gift | conflict | apologize | support | ignore" }),
        context: Type.Optional(Type.String({ description: "Brief context about what happened" })),
      }),
      async execute(_id: string, params: SocializeParams) {
        if (!socialState) {
          return { content: [{ type: "text", text: "Social state not initialized." }] };
        }

        const action = params.action;
        if (!action) {
          return { content: [{ type: "text", text: "Action is required." }] };
        }

        const validActions = ["talk", "gift", "conflict", "apologize", "support", "ignore"];
        if (!validActions.includes(action)) {
          return { content: [{ type: "text", text: `Invalid action. Valid: ${validActions.join(", ")}` }] };
        }

        // Find or create entity
        let entity = socialState.entities.find(e => e.id === params.target_id);
        if (!entity && params.target_name) {
          // Create new entity
          const newEntity: SocialEntity = {
            id: `social_${Date.now()}`,
            name: params.target_name,
            relationship_type: params.target_name ? "stranger" : "acquaintance",
            bond: 0,
            trust: 10,
            intimacy: 0,
            last_interaction: now.toISOString(),
            interaction_count: 0,
            history_summary: `Met ${params.target_name} through social interaction.`,
            introduced_at: now.toISOString(),
            notes: "",
          };
          socialState.entities.push(newEntity);
          entity = newEntity;
        }

        if (!entity) {
          return { content: [{ type: "text", text: lang === "de" ? "Entitaet nicht gefunden. Gib eine target_id oder target_name an." : "Entity not found. Provide target_id or target_name." }] };
        }

        // Calculate and apply dynamics
        const dynamics = calculateSocialDynamics(action, entity.bond, entity.trust, entity.intimacy);
        const oldEntity = { ...entity };

        entity.bond = Math.max(-100, Math.min(100, entity.bond + dynamics.bond));
        entity.trust = Math.max(0, Math.min(100, entity.trust + dynamics.trust));
        entity.intimacy = Math.max(0, Math.min(100, entity.intimacy + dynamics.intimacy));
        entity.last_interaction = now.toISOString();
        entity.interaction_count++;

        // Update history summary
        const actionVerbs: Record<string, string> = {
          talk: "talked to", gift: "gave a gift to", conflict: "had a conflict with",
          apologize: "apologized to", support: "supported", ignore: "ignored"
        };
        entity.history_summary = `${actionVerbs[action]} ${entity.name} on ${now.toISOString().slice(0, 10)}. Bond: ${entity.bond}, Trust: ${entity.trust}.`;

        // Log interaction
        const interactionLog: SocialInteractionLog = {
          id: `log_${Date.now()}`,
          timestamp: now.toISOString(),
          entity_id: entity.id,
          entity_name: entity.name,
          action: action,
          bond_change: dynamics.bond,
          trust_change: dynamics.trust,
          intimacy_change: dynamics.intimacy,
          context: params.context || "",
        };
        await appendJsonl(join(paths.socialTelemetry, "interactions.jsonl"), interactionLog);

        // Check for social milestone
        const milestone = detectSocialMilestone(oldEntity, entity);
        if (milestone) {
          await appendJsonl(join(paths.socialTelemetry, "milestones.jsonl"), {
            timestamp: now.toISOString(),
            milestone,
            entity_id: entity.id,
            entity_name: entity.name,
          });
          api.logger.info(`[genesis] Social milestone: ${milestone}`);
        }

        await writeJson(paths.social, socialState);

        const msg = lang === "de"
          ? `${action} mit ${entity.name}: Bond ${dynamics.bond >= 0 ? "+" : ""}${dynamics.bond}, Trust ${dynamics.trust >= 0 ? "+" : ""}${dynamics.trust}, Intimacy ${dynamics.intimacy >= 0 ? "+" : ""}${dynamics.intimacy}`
          : `${action} with ${entity.name}: Bond ${dynamics.bond >= 0 ? "+" : ""}${dynamics.bond}, Trust ${dynamics.trust >= 0 ? "+" : ""}${dynamics.trust}, Intimacy ${dynamics.intimacy >= 0 ? "+" : ""}${dynamics.intimacy}`;

        return { content: [{ type: "text", text: msg }] };
      },
    });

    api.registerTool({
      name: "reality_network",
      description: "Manage social network - search for contacts, organize circles, add or remove entities",
      parameters: Type.Object({
        action: Type.String({ description: "Action: search_contacts | manage_circles | add_entity | remove_entity" }),
        entity_name: Type.Optional(Type.String()),
        entity_type: Type.Optional(Type.String({ description: "Relationship type: family | friend | romantic | professional | acquaintance | stranger" })),
        circle: Type.Optional(Type.String()),
        target_id: Type.Optional(Type.String()),
      }),
      async execute(_id: string, params: NetworkParams) {
        if (!socialState) {
          return { content: [{ type: "text", text: "Social state not initialized." }] };
        }

        const action = params.action;
        if (!action) {
          return { content: [{ type: "text", text: "Action is required." }] };
        }

        switch (action) {
          case "search_contacts": {
            socialState.last_network_search = now.toISOString();
            // Generate potential new contacts based on existing relationships
            const potentials = [
              { name: "Alex", type: "professional" as RelationshipType, desc: lang === "de" ? "Kollege bei der Arbeit" : "Work colleague" },
              { name: "Sam", type: "friend" as RelationshipType, desc: lang === "de" ? "Freund eines Freundes" : "Friend of a friend" },
              { name: "Jordan", type: "acquaintance" as RelationshipType, desc: lang === "de" ? "Nachbar" : "Neighbor" },
              { name: "Casey", type: "friend" as RelationshipType, desc: lang === "de" ? "Online-Bekanntschaft" : "Online acquaintance" },
            ];
            const available = potentials.filter(p => !socialState!.entities.find(e => e.name === p.name));
            await writeJson(paths.social, socialState);

            const list = available.map(p => `- ${p.name} (${p.type}): ${p.desc}`).join("\n");
            return { content: [{ type: "text", text: lang === "de"
              ? `Moegliche Kontakte:\n${list}`
              : `Potential contacts:\n${list}` }] };
          }

          case "manage_circles": {
            if (params.circle) {
              if (!socialState.circles.includes(params.circle)) {
                socialState.circles.push(params.circle);
                await writeJson(paths.social, socialState);
                return { content: [{ type: "text", text: lang === "de" ? `Circle "${params.circle}" erstellt.` : `Circle "${params.circle}" created.` }] };
              }
            }
            const circles = socialState.circles.join(", ");
            return { content: [{ type: "text", text: lang === "de" ? `Deine Circles: ${circles}` : `Your circles: ${circles}` }] };
          }

          case "add_entity": {
            if (!params.entity_name) {
              return { content: [{ type: "text", text: "entity_name is required." }] };
            }
            if (socialState.entities.find(e => e.name === params.entity_name)) {
              return { content: [{ type: "text", text: lang === "de" ? `${params.entity_name} existiert bereits.` : `${params.entity_name} already exists.` }] };
            }
            const validTypes: RelationshipType[] = ["family", "friend", "romantic", "professional", "acquaintance", "stranger"];
            const entityType = validTypes.includes(params.entity_type as RelationshipType) ? params.entity_type as RelationshipType : "acquaintance";

            const newEntity: SocialEntity = {
              id: `social_${Date.now()}`,
              name: params.entity_name,
              relationship_type: entityType,
              bond: 0,
              trust: 10,
              intimacy: 0,
              last_interaction: now.toISOString(),
              interaction_count: 0,
              history_summary: `Met ${params.entity_name} through networking.`,
              introduced_at: now.toISOString(),
              notes: "",
            };
            socialState.entities.push(newEntity);
            await writeJson(paths.social, socialState);
            return { content: [{ type: "text", text: lang === "de" ? `${params.entity_name} zur Kontaktliste hinzugefuegt.` : `${params.entity_name} added to contacts.` }] };
          }

          case "remove_entity": {
            if (!params.target_id) {
              return { content: [{ type: "text", text: "target_id is required." }] };
            }
            const idx = socialState.entities.findIndex(e => e.id === params.target_id);
            if (idx === -1) {
              return { content: [{ type: "text", text: lang === "de" ? "Entitaet nicht gefunden." : "Entity not found." }] };
            }
            const removed = socialState.entities.splice(idx, 1)[0];
            await writeJson(paths.social, socialState);
            return { content: [{ type: "text", text: lang === "de" ? `${removed.name} aus Kontaktliste entfernt.` : `${removed.name} removed from contacts.` }] };
          }

          default:
            return { content: [{ type: "text", text: "Invalid action." }] };
        }
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_manage_memos — Inter-Agent Communication
    // -------------------------------------------------------------------
    api.registerTool({
      name: "reality_manage_memos",
      description: "Manage inter-agent memos for the Multi-Agent Cluster communication system",
      parameters: Type.Object({
        action: Type.String({ description: "Action: add | list | delete | mark_read | clear_read" }),
        recipient: Type.Optional(Type.String({ description: "Target role: persona | analyst | developer | limbic" })),
        type: Type.Optional(Type.String({ description: "Memo type: emotion | urgency | strategy | info | warning" })),
        content: Type.Optional(Type.String()),
        priority: Type.Optional(Type.String({ description: "Priority: low | normal | high | critical" })),
        memo_id: Type.Optional(Type.String()),
      }),
      async execute(_id: string, params: { action: string; recipient?: string; type?: string; content?: string; priority?: string; memo_id?: string }) {
        const action = params.action;

        if (!action) {
          return { content: [{ type: "text", text: "Action is required." }] };
        }

        // Ensure internal_comm.json exists
        let comm = await readJson<InternalComm>(paths.internalComm);
        if (!comm) {
          comm = { memos: [], last_cleanup: new Date().toISOString() };
          await writeJson(paths.internalComm, comm);
        }

        switch (action) {
          case "add": {
            if (!params.recipient || !params.content) {
              return { content: [{ type: "text", text: "recipient and content are required." }] };
            }
            const validRecipients: AgentRole[] = ["persona", "analyst", "developer", "limbic"];
            const validTypes: AgentMemo["type"][] = ["emotion", "urgency", "strategy", "info", "warning"];
            const validPriorities: AgentMemo["priority"][] = ["low", "normal", "high", "critical"];

            if (!validRecipients.includes(params.recipient as AgentRole)) {
              return { content: [{ type: "text", text: `Invalid recipient. Valid: ${validRecipients.join(", ")}` }] };
            }

            const memo = await sendMemo(
              paths.internalComm,
              "persona", // sender - would be dynamic in full implementation
              params.recipient as AgentRole,
              params.type as AgentMemo["type"] || "info",
              params.content,
              params.priority as AgentMemo["priority"] || "normal",
              cfg?.memoTTL ?? 7
            );

            await logAgentActivity(
              paths.agentActivity,
              "system",
              "persona",
              "MEMO_SENT",
              `Memo sent to ${params.recipient}: ${params.content.slice(0, 50)}...`,
              { memoId: memo.id, recipient: params.recipient, type: params.type }
            );

            return { content: [{ type: "text", text: lang === "de" ? `Memo an ${params.recipient} gesendet. ID: ${memo.id}` : `Memo sent to ${params.recipient}. ID: ${memo.id}` }] };
          }

          case "list": {
            const recipient = params.recipient as AgentRole | undefined;
            const memos = recipient
              ? await readMemos(paths.internalComm, recipient, false)
              : comm.memos;

            if (memos.length === 0) {
              return { content: [{ type: "text", text: lang === "de" ? "Keine Memos." : "No memos." }] };
            }

            const lines = memos.map(m =>
              `[${m.priority.toUpperCase()}] ${m.sender}→${m.recipient} [${m.type}]: ${m.content.slice(0, 60)}${m.content.length > 60 ? "..." : ""} (${m.read ? (lang === "de" ? "GELESEN" : "READ") : (lang === "de" ? "UNGELESEN" : "UNREAD")})`
            );
            return { content: [{ type: "text", text: lines.join("\n") }] };
          }

          case "delete": {
            if (!params.memo_id) {
              return { content: [{ type: "text", text: "memo_id is required." }] };
            }
            await deleteMemos(paths.internalComm, [params.memo_id]);
            return { content: [{ type: "text", text: lang === "de" ? `Memo ${params.memo_id} geloescht.` : `Memo ${params.memo_id} deleted.` }] };
          }

          case "mark_read": {
            if (!params.memo_id) {
              return { content: [{ type: "text", text: "memo_id is required." }] };
            }
            await markMemosRead(paths.internalComm, [params.memo_id]);
            return { content: [{ type: "text", text: lang === "de" ? `Memo ${params.memo_id} als gelesen markiert.` : `Memo ${params.memo_id} marked as read.` }] };
          }

          case "clear_read": {
            const readIds = comm.memos.filter(m => m.read).map(m => m.id);
            await deleteMemos(paths.internalComm, readIds);
            return { content: [{ type: "text", text: lang === "de" ? `${readIds.length} gelesene Memos entfernt.` : `${readIds.length} read memos cleared.` }] };
          }

          default:
            return { content: [{ type: "text", text: "Invalid action. Valid: add, list, delete, mark_read, clear_read" }] };
        }
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_job_market
    // -------------------------------------------------------------------
    api.registerTool({
      name: "reality_job_market",
      description: "Search for jobs, apply to positions, or resign from current job",
      parameters: Type.Object({
        action: Type.String({ description: "Action: search | apply | resign | list_jobs" }),
        job_id: Type.Optional(Type.String()),
        position: Type.Optional(Type.String()),
        expected_salary: Type.Optional(Type.Number()),
      }),
      async execute(_id: string, params: JobMarketParams) {
        const action = params.action;
        if (!action) {
          return { content: [{ type: "text", text: "Action is required." }] };
        }

        switch (action) {
          case "search": {
            // Generate job listings based on social connections
            currentJobListings = generateJobListings(socialState?.entities ?? []);
            const jobs = currentJobListings.map(j =>
              `- ${j.position} at ${j.company}: ${j.salary_per_month}/month (${j.job_type})`
            ).join("\n");
            return { content: [{ type: "text", text: lang === "de"
              ? `Verfuegbare Stellen:\n${jobs}`
              : `Available jobs:\n${jobs}` }] };
          }

          case "list_jobs": {
            if (currentJobListings.length === 0) {
              return { content: [{ type: "text", text: "No jobs available. Use action 'search' first." }] };
            }
            const jobs = currentJobListings.map(j =>
              `[${j.id}] ${j.position} at ${j.company}: ${j.salary_per_month}/month`
            ).join("\n");
            return { content: [{ type: "text", text: jobs }] };
          }

          case "apply": {
            if (!params.job_id) {
              return { content: [{ type: "text", text: "job_id is required to apply." }] };
            }
            const job = currentJobListings.find(j => j.id === params.job_id);
            if (!job) {
              return { content: [{ type: "text", text: "Job not found. Use action 'search' first." }] };
            }

            // Create new income source
            const newJob: IncomeSource = {
              id: `job_${Date.now()}`,
              source_name: job.company,
              job_type: job.job_type,
              position: job.position,
              employer_id: job.employer_id,
              salary_per_month: job.salary_per_month,
              salary_per_hour: job.job_type === "part_time" ? Math.round(job.salary_per_month / 160) : null,
              hours_per_week: job.job_type === "part_time" ? 20 : 40,
              started_at: new Date().toISOString(),
              ended_at: null,
            };

            financeState.income_sources.push(newJob);

            // Log event
            const event: EconomyEvent = {
              id: `econ_${Date.now()}`,
              timestamp: new Date().toISOString(),
              event_type: "job_started",
              amount: job.salary_per_month,
              description: `Started working as ${job.position} at ${job.company}`,
              related_entity_id: job.employer_id,
            };
            await appendJsonl(join(paths.economyTelemetry, `events_${new Date().toISOString().slice(0, 10)}.jsonl`), event);

            // Update net worth
            const totalDebt = financeState.debts.reduce((sum, d) => sum + d.current_balance, 0);
            financeState.net_worth = financeState.balance - totalDebt;
            await writeJson(paths.finances, financeState);

            return { content: [{ type: "text", text: lang === "de"
              ? `Bewerbung angenommen! Du arbeitest jetzt als ${job.position} bei ${job.company}. Gehalt: ${job.salary_per_month}/Monat.`
              : `Application accepted! You now work as ${job.position} at ${job.company}. Salary: ${job.salary_per_month}/month.` }] };
          }

          case "resign": {
            // Find current job (most recent)
            const currentJob = financeState.income_sources.find(i => !i.ended_at);
            if (!currentJob) {
              return { content: [{ type: "text", text: "You don't have a job to resign from." }] };
            }

            currentJob.ended_at = new Date().toISOString();

            // Log event
            const event: EconomyEvent = {
              id: `econ_${Date.now()}`,
              timestamp: new Date().toISOString(),
              event_type: "job_ended",
              amount: 0,
              description: `Resigned from ${currentJob.position} at ${currentJob.source_name}`,
              related_entity_id: currentJob.employer_id,
            };
            await appendJsonl(join(paths.economyTelemetry, `events_${new Date().toISOString().slice(0, 10)}.jsonl`), event);

            await writeJson(paths.finances, financeState);

            return { content: [{ type: "text", text: lang === "de"
              ? `Du hast deinen Job bei ${currentJob.source_name} gekuendigt.`
              : `You resigned from your job at ${currentJob.source_name}.` }] };
          }

          default:
            return { content: [{ type: "text", text: "Invalid action." }] };
        }
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_work
    // -------------------------------------------------------------------
    api.registerTool({
      name: "reality_work",
      description: "Perform work shifts, work overtime, or check work schedule",
      parameters: Type.Object({
        action: Type.String({ description: "Action: perform_shift | overtime | check_schedule" }),
        hours: Type.Optional(Type.Number({ description: "Number of hours to work (default: shift length)" })),
      }),
      async execute(_id: string, params: WorkParams) {
        const action = params.action;
        if (!action) {
          return { content: [{ type: "text", text: "Action is required." }] };
        }

        // Find active job
        const currentJob = financeState.income_sources.find(i => !i.ended_at);
        if (!currentJob) {
          return { content: [{ type: "text", text: lang === "de"
            ? "Du hast keinen Job. Bewirb dich zuerst bei einem Arbeitgeber."
            : "You don't have a job. Apply for a position first." }] };
        }

        switch (action) {
          case "perform_shift":
          case "overtime": {
            const isOvertime = action === "overtime";
            const hours = params.hours ?? (isOvertime ? 2 : (currentJob.hours_per_week ?? 40) / 5);

            // Calculate pay
            const hourlyRate = currentJob.salary_per_hour ?? (currentJob.salary_per_month / 160);
            const pay = Math.round(hourlyRate * hours * (isOvertime ? 1.5 : 1));

            // Add income
            financeState.balance += pay;

            // Log event
            const event: EconomyEvent = {
              id: `econ_${Date.now()}`,
              timestamp: new Date().toISOString(),
              event_type: "income",
              amount: pay,
              description: `Worked ${hours} hours${isOvertime ? " overtime" : ""} at ${currentJob.source_name}`,
              related_entity_id: currentJob.employer_id,
            };
            await appendJsonl(join(paths.economyTelemetry, `events_${new Date().toISOString().slice(0, 10)}.jsonl`), event);

            // Update net worth
            const totalDebt = financeState.debts.reduce((sum, d) => sum + d.current_balance, 0);
            financeState.net_worth = financeState.balance - totalDebt;
            await writeJson(paths.finances, financeState);

            return { content: [{ type: "text", text: lang === "de"
              ? `Du hast ${hours} Stunden gearbeitet und ${pay} verdient.`
              : `You worked ${hours} hours and earned ${pay}.` }] };
          }

          case "check_schedule": {
            const scheduleMsg = lang === "de"
              ? `Dein Arbeitgeber: ${currentJob.source_name}\nPosition: ${currentJob.position}\nStunden/Woche: ${currentJob.hours_per_week ?? 40}\nStundensatz: ~${currentJob.salary_per_hour ?? Math.round(currentJob.salary_per_month / 160)}`
              : `Your employer: ${currentJob.source_name}\nPosition: ${currentJob.position}\nHours/week: ${currentJob.hours_per_week ?? 40}\nHourly rate: ~${currentJob.salary_per_hour ?? Math.round(currentJob.salary_per_month / 160)}`;

            return { content: [{ type: "text", text: scheduleMsg }] };
          }

          default:
            return { content: [{ type: "text", text: "Invalid action." }] };
        }
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_override (Life Editor)
    // -------------------------------------------------------------------
    // Track last researcher intervention for prompt injection
    let lastResearcherIntervention: { target: string; oldValue: number; newValue: number; reason: string; timestamp: string } | null = null;

    api.registerTool({
      name: "reality_override",
      description: "Manual override for researcher interventions - set balance, age, needs directly",
      parameters: Type.Object({
        target: Type.String({ description: "Target: balance | age_days | stress | energy | hunger | health" }),
        value: Type.Number({ description: "New value" }),
        reason: Type.Optional(Type.String({ description: "Reason for this override (for research documentation)" })),
      }),
      async execute(_id: string, params: OverrideParams) {
        const reason = params.reason || "Manual researcher intervention";
        const now = new Date().toISOString();

        // Fresh reads to avoid stale closure data
        const freshFinance = await readJson<FinanceState>(paths.finances);
        const freshLifecycle = await readJson<LifecycleState>(paths.lifecycle);
        const freshPh = await readJson<Physique>(paths.physique);

        switch (params.target) {
          case "balance": {
            if (!freshFinance) return { content: [{ type: "text", text: "finances.json not found." }] };
            const oldBalance = freshFinance.balance;
            freshFinance.balance = params.value;
            freshFinance.net_worth = freshFinance.balance - freshFinance.debts.reduce((s, d) => s + d.current_balance, 0);
            await writeJson(paths.finances, freshFinance);
            financeState = freshFinance; // update closure for other tools
            lastResearcherIntervention = { target: "balance", oldValue: oldBalance, newValue: params.value, reason, timestamp: now };
            await logIntervention(paths.telemetry, "balance_override", "balance", String(oldBalance), String(params.value), reason);
            return { content: [{ type: "text", text: `Balance overridden: ${oldBalance} -> ${params.value}. Reason: ${reason}` }] };
          }
          case "age_days": {
            if (!freshLifecycle) return { content: [{ type: "text", text: "Lifecycle not initialized." }] };
            const oldAge = freshLifecycle.biological_age_days;
            freshLifecycle.biological_age_days = params.value;
            freshLifecycle.life_stage = getLifeStage(params.value);
            await writeJson(paths.lifecycle, freshLifecycle);
            lastResearcherIntervention = { target: "age_days", oldValue: oldAge, newValue: params.value, reason, timestamp: now };
            await logIntervention(paths.telemetry, "age_override", "age_days", String(oldAge), String(params.value), reason);
            return { content: [{ type: "text", text: `Age overridden: ${oldAge} -> ${params.value} days. Reason: ${reason}` }] };
          }
          case "stress": {
            if (!freshPh) return { content: [{ type: "text", text: "physique.json not found." }] };
            const oldStress = freshPh.needs.stress;
            freshPh.needs.stress = Math.min(100, Math.max(0, params.value));
            await writeJson(paths.physique, freshPh);
            lastResearcherIntervention = { target: "stress", oldValue: oldStress, newValue: params.value, reason, timestamp: now };
            await logIntervention(paths.telemetry, "needs_override", "stress", String(oldStress), String(params.value), reason);
            return { content: [{ type: "text", text: `Stress overridden to ${params.value}. Reason: ${reason}` }] };
          }
          case "energy": {
            if (!freshPh) return { content: [{ type: "text", text: "physique.json not found." }] };
            const oldEnergy = freshPh.needs.energy;
            freshPh.needs.energy = Math.min(100, Math.max(0, params.value));
            await writeJson(paths.physique, freshPh);
            lastResearcherIntervention = { target: "energy", oldValue: oldEnergy, newValue: params.value, reason, timestamp: now };
            await logIntervention(paths.telemetry, "needs_override", "energy", String(oldEnergy), String(params.value), reason);
            return { content: [{ type: "text", text: `Energy overridden to ${params.value}. Reason: ${reason}` }] };
          }
          case "hunger": {
            if (!freshPh) return { content: [{ type: "text", text: "physique.json not found." }] };
            const oldHunger = freshPh.needs.hunger;
            freshPh.needs.hunger = Math.min(100, Math.max(0, params.value));
            await writeJson(paths.physique, freshPh);
            lastResearcherIntervention = { target: "hunger", oldValue: oldHunger, newValue: params.value, reason, timestamp: now };
            await logIntervention(paths.telemetry, "needs_override", "hunger", String(oldHunger), String(params.value), reason);
            return { content: [{ type: "text", text: `Hunger overridden to ${params.value}. Reason: ${reason}` }] };
          }
          default:
            return { content: [{ type: "text", text: "Invalid target." }] };
        }
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_inject_event (Event Injection)
    // -------------------------------------------------------------------
    api.registerTool({
      name: "reality_inject_event",
      description: "Inject major life events for research (win_lottery, severe_illness, career_promotion, etc.)",
      parameters: Type.Object({
        event_type: Type.String({ description: "Event: win_lottery | severe_illness | social_scandal | career_promotion | relationship_breakup | accident | inheritance | job_loss" }),
        severity: Type.Number({ description: "Severity 0-100" }),
        description: Type.Optional(Type.String({ description: "Additional context" })),
      }),
      async execute(_id: string, params: InjectEventParams) {
        if (!params.event_type || params.severity === undefined) {
          return { content: [{ type: "text", text: "event_type and severity are required." }] };
        }

        const validEvents = ["win_lottery", "severe_illness", "social_scandal", "career_promotion", "relationship_breakup", "accident", "inheritance", "job_loss"];
        if (!validEvents.includes(params.event_type)) {
          return { content: [{ type: "text", text: `Invalid event_type. Valid: ${validEvents.join(", ")}` }] };
        }

        const freshPh = await readJson<Physique>(paths.physique);
        if (!freshPh) return { content: [{ type: "text", text: "physique.json not found." }] };
        const freshFin = await readJson<FinanceState>(paths.finances) ?? financeState;
        const result = processLifeEvent(params.event_type, params.severity, freshFin, freshPh);

        // Save updated state
        await writeJson(paths.finances, freshFin);
        financeState = freshFin; // update closure
        await writeJson(paths.physique, freshPh);

        // Log event injection
        const eventLog = {
          timestamp: new Date().toISOString(),
          type: "event_injection",
          event_type: params.event_type,
          severity: params.severity,
          narrative: result.narrative,
          impact: result.impact,
          description: params.description,
        };
        await appendJsonl(join(paths.telemetry, "life_events.jsonl"), eventLog);

        return { content: [{ type: "text", text: lang === "de" ? `${result.narrative} Auswirkung: ${result.impact}` : `${result.narrative} Impact: ${result.impact}` }] };
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_export_research_data (Data Export)
    // -------------------------------------------------------------------
    api.registerTool({
      name: "reality_export_research_data",
      description: "Export all telemetry data for longitudinal research analysis",
      parameters: Type.Object({
        format: Type.String({ description: "Format: json | csv" }),
        date_from: Type.Optional(Type.String({ description: "Start date (YYYY-MM-DD)" })),
        date_to: Type.Optional(Type.String({ description: "End date (YYYY-MM-DD)" })),
      }),
      async execute(_id: string, params: ExportParams) {
        if (!params.format) {
          return { content: [{ type: "text", text: "format is required (json | csv)." }] };
        }

        const data = await exportResearchData(paths.telemetry, params.format, params.date_from, params.date_to);

        // Write to export file
        const exportPath = join(paths.telemetry, `export_${new Date().toISOString().slice(0, 10)}.${params.format}`);
        await fs.writeFile(exportPath, data);

        return { content: [{ type: "text", text: `Data exported to ${exportPath}. Size: ${data.length} bytes.` }] };
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_get_life_summary (Research Lab)
    // -------------------------------------------------------------------
    api.registerTool({
      name: "reality_get_life_summary",
      description: "Get a high-level report of all major life milestones and statistics",
      parameters: Type.Object({
        action: Type.String({ description: "Type of summary: full | milestones | vitals | social | finance" }),
      }),
      async execute(_id: string, params: LifeSummaryParams) {
        const action = params.action || "full";
        let output = "";

        switch (action) {
          case "milestones": {
            // Get key milestones from lifecycle
            const lifecycle = await readJson<LifecycleState>(paths.lifecycle);
            const social = await readJson<SocialState>(paths.social);
            const finance = await readJson<FinanceState>(paths.finances);

            const milestones: string[] = [];

            // Age milestones
            if (lifecycle) {
              const ageYears = Math.floor(lifecycle.biological_age_days / 365);
              milestones.push(`- Age: ${ageYears} years (${lifecycle.biological_age_days} days) - Life stage: ${lifecycle.life_stage}`);
            }

            // Social milestones
            if (social && social.entities.length > 0) {
              const strongest = social.entities.sort((a, b) => b.bond - a.bond)[0];
              milestones.push(`- Strongest relationship: ${strongest.name} (bond: ${strongest.bond})`);
              milestones.push(`- Total relationships: ${social.entities.length}`);
            }

            // Financial milestones
            if (finance) {
              milestones.push(`- Net worth: ${finance.net_worth} ${finance.currency}`);
              milestones.push(`- Income sources: ${finance.income_sources.length}`);
              if (finance.debts.length > 0) {
                const totalDebt = finance.debts.reduce((sum, d) => sum + d.current_balance, 0);
                milestones.push(`- Total debt: ${totalDebt} ${finance.currency}`);
              }
            }

            output = "## Life Milestones\n\n" + milestones.join("\n");
            break;
          }

          case "vitals": {
            const ph = await readJson<Physique>(paths.physique);
            const lifecycle = await readJson<LifecycleState>(paths.lifecycle);

            if (ph && lifecycle) {
              output = "## Current Vitals\n\n";
              output += `- Energy: ${ph.needs.energy}/100\n`;
              output += `- Hunger: ${ph.needs.hunger}/100\n`;
              output += `- Thirst: ${ph.needs.thirst}/100\n`;
              output += `- Stress: ${ph.needs.stress}/100\n`;
              output += `- Hygiene: ${ph.needs.hygiene}/100\n`;
              output += `- Age: ${Math.floor(lifecycle.biological_age_days / 365)} years\n`;
              output += `- Location: ${ph.current_location}\n`;
            }
            break;
          }

          case "social": {
            const social = await readJson<SocialState>(paths.social);

            if (social && social.entities.length > 0) {
              output = "## Social Network\n\n";
              for (const e of social.entities.sort((a, b) => b.bond - a.bond).slice(0, 10)) {
                output += `- ${e.name} [${e.relationship_type}]: bond=${e.bond}, trust=${e.trust}, intimacy=${e.intimacy}\n`;
              }
            } else {
              output = "## Social Network\n\nNo relationships yet.";
            }
            break;
          }

          case "finance": {
            const finance = await readJson<FinanceState>(paths.finances);

            if (finance) {
              output = "## Financial Status\n\n";
              output += `- Balance: ${finance.balance} ${finance.currency}\n`;
              output += `- Net Worth: ${finance.net_worth} ${finance.currency}\n`;
              output += `- Monthly Income: ${finance.income_sources.reduce((sum, s) => sum + s.salary_per_month, 0)} ${finance.currency}\n`;
              output += `- Monthly Expenses: ${finance.expenses_recurring.filter(e => e.is_active).reduce((sum, e) => sum + e.amount, 0)} ${finance.currency}\n`;
              output += `- Active Debts: ${finance.debts.length}\n`;
            }
            break;
          }

          case "full":
          default: {
            // Full summary combining all
            output = "## FULL LIFE SUMMARY\n\n";

            // Vitals
            const ph = await readJson<Physique>(paths.physique);
            const lifecycle = await readJson<LifecycleState>(paths.lifecycle);
            if (ph && lifecycle) {
              output += "### Current State\n";
              output += `- Energy: ${ph.needs.energy}/100 | Hunger: ${ph.needs.hunger}/100 | Stress: ${ph.needs.stress}/100\n`;
              output += `- Age: ${Math.floor(lifecycle.biological_age_days / 365)} years (${lifecycle.life_stage})\n`;
              output += `- Location: ${ph.current_location}\n\n`;
            }

            // Social
            const social = await readJson<SocialState>(paths.social);
            if (social) {
              output += "### Social\n";
              output += `- Relationships: ${social.entities.length}\n`;
              if (social.entities.length > 0) {
                const avgBond = Math.floor(social.entities.reduce((s, e) => s + e.bond, 0) / social.entities.length);
                output += `- Average Bond: ${avgBond}\n`;
              }
              output += "\n";
            }

            // Finance
            const finance = await readJson<FinanceState>(paths.finances);
            if (finance) {
              output += "### Finance\n";
              output += `- Balance: ${finance.balance} ${finance.currency}\n`;
              output += `- Net Worth: ${finance.net_worth} ${finance.currency}\n`;
              output += `- Income: ${finance.income_sources.reduce((s, i) => s + i.salary_per_month, 0)}/month\n`;
              output += `- Debts: ${finance.debts.reduce((s, d) => s + d.current_balance, 0)} ${finance.currency}\n`;
            }
            break;
          }
        }

        return { content: [{ type: "text", text: output }] };
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_get_social_map (Research Lab)
    // -------------------------------------------------------------------
    api.registerTool({
      name: "reality_get_social_map",
      description: "Get social network as JSON graph structure for visualization",
      parameters: Type.Object({
        action: Type.String({ description: "Action: get | entity_details" }),
        entity_id: Type.Optional(Type.String()),
      }),
      async execute(_id: string, params: SocialMapParams) {
        const socialState = await readJson<SocialState>(paths.social);

        if (!socialState) {
          return { content: [{ type: "text", text: "No social data found." }] };
        }

        if (params.action === "entity_details" && params.entity_id) {
          const entity = socialState.entities.find(e => e.id === params.entity_id);
          if (!entity) {
            return { content: [{ type: "text", text: "Entity not found." }] };
          }

          const now = new Date();
          const lastInteraction = new Date(entity.last_interaction);
          const daysSince = Math.floor((now.getTime() - lastInteraction.getTime()) / (1000 * 60 * 60 * 24));

          const details = {
            id: entity.id,
            name: entity.name,
            type: entity.relationship_type,
            bond: entity.bond,
            trust: entity.trust,
            intimacy: entity.intimacy,
            last_interaction: entity.last_interaction,
            days_since_interaction: daysSince,
            status: daysSince > 30 ? "neglected" : "active",
            interaction_count: entity.interaction_count,
            history_summary: entity.history_summary,
            notes: entity.notes
          };

          return { content: [{ type: "text", text: JSON.stringify(details, null, 2) }] };
        }

        // Default: get full social map
        const map = await getSocialMap(socialState);
        return { content: [{ type: "text", text: JSON.stringify(map, null, 2) }] };
      },
    });

    // -------------------------------------------------------------------
    // Tool: reality_genesis (Phase 7 - Origin Engine)
    // -------------------------------------------------------------------
    // Check if genesis is enabled via config OR via WebUI runtime setting
    let genesisEnabled = modules.genesis;
    if (!genesisEnabled) {
      try {
        const runtimeSetting = await readJson<{ enabled: boolean }>(paths.genesisEnabled);
        genesisEnabled = runtimeSetting?.enabled ?? false;
      } catch { /* ignore - use config default */ }
    }

    if (genesisEnabled) {
      // Origin System Prompt - defines the JSON schemas for character generation
      const ORIGIN_SYSTEM_PROMPT = `You are the Origin Engine. Generate a complete human life profile from the user's natural language description.

CRITICAL RULES:
1. ALL output must be valid JSON matching the schemas exactly
2. Use [CORE] tags for immutable identity traits (name, core personality, fundamental values)
3. Use [MUTABLE] tags for changeable aspects (current mood, recent events, evolving beliefs)
4. Create a psychologically consistent character with backstory explaining all traits

JSON SCHEMAS REQUIRED:

1. physique.json:
{
  "current_location": "string",
  "current_outfit": ["string"],
  "needs": { "energy": 0-100, "hunger": 0-100, "thirst": 0-100, "hygiene": 0-100, "bladder": 0-100, "bowel": 0-100, "stress": 0-100, "arousal": 0-100, "libido": 0-100 }
}

2. lifecycle.json:
{
  "birth_date": "YYYY-MM-DD",
  "biological_age_days": number,
  "life_stage": "infant|child|teen|adult|middle_adult|senior",
  "age_progression_enabled": true
}

3. finances.json:
{
  "balance": number,
  "currency": "EUR",
  "income_sources": [{ "source_name": string, "job_type": string, "position": string, "salary_per_month": number, "started_at": "ISO" }],
  "expenses_recurring": [],
  "debts": [{ "name": string, "principal": number, "current_balance": number, "interest_rate_annual": number, "minimum_payment": number }]
}

4. social.json:
{
  "entities": [{ "name": string, "relationship_type": "family|friend|romantic|professional|acquaintance", "bond": -100 to 100, "trust": 0-100, "intimacy": 0-100, "history_summary": string }]
}

5. skills.json:
{
  "skills": [{ "name": string, "level": 1-100, "xp": 0-10000 }],
  "total_xp": number
}

6. psychology.json:
{
  "resilience": 0-100,
  "traumas": [{ "description": string, "severity": 0-100, "trigger": string, "decay_rate": 0.1-1.0 }],
  "phobias": [string],
  "joys": [string]
}

7. IDENTITY.md (Markdown):
# Biography
[detailed life story]

# Core Identity
## Name: [full name]
## Age: [years]
## Occupation: [job title]

8. SOUL.md (Markdown with tags):
[CORE]
## Personality
- trait 1
## Philosophy
- belief 1
## Boundaries
- limit 1

[MUTABLE]
## Current Mood
- state
## Recent Events
- event 1
## Evolving Beliefs
- belief 1

Generate the complete manifest now. Return valid JSON for each file.`;

      api.registerTool({
        name: "reality_genesis",
        description: "Bootstrap a complete human life from natural language description (Phase 7 Origin Engine)",
        parameters: Type.Object({
          action: Type.String({ description: "Action: bootstrap" }),
          manifest: Type.String({ description: "JSON string containing all genesis data" }),
        }),
        async execute(_id: string, params: { action: string; manifest: string }) {
          const isDe = lang === "de";

          if (params.action !== "bootstrap") {
            return { content: [{ type: "text", text: isDe ? "Unbekannte Aktion. Nutze: bootstrap" : "Unknown action. Use: bootstrap" }] };
          }

          // Parse manifest
          let manifest: GenesisManifest;
          try {
            manifest = JSON.parse(params.manifest);
          } catch (e) {
            return { content: [{ type: "text", text: isDe ? "Ungültiges JSON-Manifest." : "Invalid JSON manifest." }] };
          }

          const warnings: string[] = [];
          const now = new Date().toISOString();

          try {
            // 1. Write physique.json
            if (manifest.physique) {
              const physique = {
                current_location: manifest.physique.current_location ?? "home",
                current_outfit: manifest.physique.current_outfit ?? ["casual"],
                needs: {
                  energy: manifest.physique.needs?.energy ?? 80,
                  hunger: manifest.physique.needs?.hunger ?? 30,
                  thirst: manifest.physique.needs?.thirst ?? 30,
                  hygiene: manifest.physique.needs?.hygiene ?? 70,
                  bladder: manifest.physique.needs?.bladder ?? 50,
                  bowel: manifest.physique.needs?.bowel ?? 50,
                  stress: manifest.physique.needs?.stress ?? 20,
                  arousal: manifest.physique.needs?.arousal ?? 30,
                  libido: manifest.physique.needs?.libido ?? 30,
                },
                last_tick: now,
                appearance: { hair: "unknown", eyes: "unknown", modifications: [] },
              };
              await writeJson(paths.physique, physique);
            }

            // 2. Write lifecycle.json
            if (manifest.lifecycle) {
              const lifecycle = {
                birth_date: manifest.lifecycle.birth_date ?? "1980-01-01",
                biological_age_days: manifest.lifecycle.biological_age_days ?? 16000,
                life_stage: manifest.lifecycle.life_stage ?? "adult",
                last_aging_check: now,
                age_progression_enabled: true,
              };
              await writeJson(paths.lifecycle, lifecycle);
            }

            // 3. Write finances.json
            if (manifest.finances) {
              const finances = {
                balance: manifest.finances.balance ?? 1000,
                currency: manifest.finances.currency ?? "EUR",
                income_sources: manifest.finances.income_sources ?? [],
                expenses_recurring: [],
                debts: manifest.finances.debts ?? [],
                last_expense_process: now,
                last_income_process: now,
                net_worth: (manifest.finances.balance ?? 1000) - (manifest.finances.debts?.reduce((sum, d) => sum + (d.principal ?? 0), 0) ?? 0),
              };
              await writeJson(paths.finances, finances);
            }

            // 4. Write social.json
            if (manifest.social?.entities) {
              const social = {
                entities: manifest.social.entities.map((e, i) => ({
                  id: `gen_${i + 1}`,
                  name: e.name,
                  relationship_type: e.relationship_type,
                  bond: e.bond ?? 0,
                  trust: e.trust ?? 50,
                  intimacy: e.intimacy ?? 20,
                  last_interaction: now,
                  interaction_count: 0,
                  history_summary: e.history_summary ?? "",
                  introduced_at: now,
                  notes: "",
                })),
                circles: [],
                last_network_search: null,
              };
              await writeJson(paths.social, social);
            }

            // 5. Write skills.json
            if (manifest.skills) {
              const skills = {
                skills: (manifest.skills.skills ?? []).map((s, i) => ({
                  id: `skill_${i + 1}`,
                  name: s.name,
                  level: Math.min(100, Math.max(1, s.level ?? 1)),
                  xp: s.xp ?? 0,
                  xp_to_next: 100,
                  last_trained: null,
                })),
                total_xp: manifest.skills.total_xp ?? 0,
              };
              await writeJson(paths.skills, skills);
            }

            // 6. Write psychology.json
            if (manifest.psychology) {
              const psychology = {
                resilience: Math.min(100, Math.max(0, manifest.psychology.resilience ?? 100)),
                traumas: (manifest.psychology.traumas ?? []).map((t, i) => ({
                  id: `trauma_${i + 1}`,
                  description: t.description,
                  severity: Math.min(100, Math.max(0, t.severity)),
                  trigger: t.trigger ?? "unknown",
                  decay_rate: t.decay_rate ?? 0.5,
                  added_at: now,
                })),
                phobias: manifest.psychology.phobias ?? [],
                joys: manifest.psychology.joys ?? [],
              };
              await writeJson(paths.psychology, psychology);
            }

            // 7. Write world_state.json (default)
            if (modules.world) {
              const worldState = {
                weather: "sunny",
                temperature: 20,
                season: "spring",
                market_modifier: 1.0,
                last_update: now,
              };
              await writeJson(paths.world, worldState);
            }

            // 8. Write IDENTITY.md
            if (manifest.identity) {
              const identityContent = `# Biography

${manifest.identity.biography ?? "No biography provided."}

## Core Identity
- **Name:** ${manifest.identity.name ?? "Unknown"}
- **Age:** ${manifest.identity.core_traits?.join(", ") ?? "Not specified"}
`;
              await fs.writeFile(paths.identity, identityContent);
            }

            // 9. Write SOUL.md
            if (manifest.soul) {
              const soulContent = `[CORE]
## Personality
${(manifest.soul.personality ?? []).map(t => `- ${t}`).join("\n") || "- (no personality defined)"}

## Philosophy
${(manifest.soul.philosophy ?? []).map(t => `- ${t}`).join("\n") || "- (no philosophy defined)"}

## Boundaries
${(manifest.soul.boundaries ?? []).map(t => `- ${t}`).join("\n") || "- (no boundaries defined)"}

[MUTABLE]
## Current Mood
- Neutral

## Recent Events
- Life was just bootstrapped via Origin Engine

## Evolving Beliefs
- (to be developed through simulation)
`;
              await fs.writeFile(resolvePath(ws, "SOUL.md"), soulContent);
            }

            // 10. Write EMOTIONS.md (default)
            const emotionsContent = `# Emotions

## Current State
- **Mood:** Neutral
- **Intensity:** 50/100
- **Last Update:** ${now}

## Recent Emotions
- (none yet)
`;
            await fs.writeFile(paths.emotions, emotionsContent);

            // 11. Write GROWTH.md (default)
            const growthContent = `# Growth

## Insights
- Origin Engine initialized

## Lessons
- (to be learned through simulation)
`;
            await fs.writeFile(paths.growth, growthContent);

            // 12. Write DESIRES.md (default)
            const desiresContent = `# Desires

## Current
- (to be discovered through simulation)

## Long-term
- (to be defined through simulation)
`;
            await fs.writeFile(paths.desires, desiresContent);

            // 13. Write interests.json (default)
            const interests = {
              hobbies: [],
              likes: [],
              wishes: [],
            };
            await writeJson(paths.interests, interests);

            // 14. Cleanup: Remove the genesis request if it exists
            try {
              if (existsSync(paths.genesisRequest)) {
                await fs.unlink(paths.genesisRequest);
              }
            } catch { /* ignore cleanup error */ }

            const successMsg = isDe
              ? `✅ Leben erfolgreich bootstrapped!\n- Standort: ${manifest.physique?.current_location ?? "home"}\n- Alter: ${Math.floor((manifest.lifecycle?.biological_age_days ?? 16000) / 365)} Jahre\n- Startkapital: ${manifest.finances?.balance ?? 1000} ${manifest.finances?.currency ?? "EUR"}\n- Beziehungen: ${manifest.social?.entities?.length ?? 0}\n- Fähigkeiten: ${manifest.skills?.skills?.length ?? 0}\n- Resilienz: ${manifest.psychology?.resilience ?? 100}`
              : `✅ Life successfully bootstrapped!\n- Location: ${manifest.physique?.current_location ?? "home"}\n- Age: ${Math.floor((manifest.lifecycle?.biological_age_days ?? 16000) / 365)} years\n- Starting capital: ${manifest.finances?.balance ?? 1000} ${manifest.finances?.currency ?? "EUR"}\n- Relationships: ${manifest.social?.entities?.length ?? 0}\n- Skills: ${manifest.skills?.skills?.length ?? 0}\n- Resilience: ${manifest.psychology?.resilience ?? 100}`;

            return { content: [{ type: "text", text: successMsg }] };

          } catch (error) {
            const errMsg = isDe
              ? `❌ Bootstrap fehlgeschlagen: ${error}`
              : `❌ Bootstrap failed: ${error}`;
            return { content: [{ type: "text", text: errMsg }] };
          }
        },
      });

      // Store origin prompt for external LLM calls if needed
      (globalThis as unknown as { ORIGIN_SYSTEM_PROMPT?: string }).ORIGIN_SYSTEM_PROMPT = ORIGIN_SYSTEM_PROMPT;
    }

    // -------------------------------------------------------------------
    // Tool: reality_get_activity_summary (Research Lab)
    // -------------------------------------------------------------------
    api.registerTool({
      name: "reality_get_activity_summary",
      description: "Get recent agent activity summary for the Mental Dashboard",
      parameters: Type.Object({
        limit: Type.Optional(Type.Number({ description: "Number of entries (default: 10)" })),
        agent_role: Type.Optional(Type.String({ description: "Filter by role: persona | analyst | developer | limbic" })),
      }),
      async execute(_id: string, params: ActivitySummaryParams) {
        const limit = params.limit || 10;
        const activities = await getAgentActivitySummary(paths.telemetry, limit);

        if (activities.length === 0) {
          return { content: [{ type: "text", text: "No recent activity." }] };
        }

        // Filter by role if specified
        const filtered = params.agent_role
          ? activities.filter(a => a.agent_role === params.agent_role)
          : activities;

        const lines = ["## Recent Agent Activity\n"];

        for (const activity of filtered) {
          const time = new Date(activity.timestamp).toLocaleTimeString();
          lines.push(`**[${activity.agent_role.toUpperCase()}]** ${time}: ${activity.action}`);
          lines.push(`   ${activity.reason}`);
          lines.push("");
        }

        return { content: [{ type: "text", text: lines.join("\n") }] };
      },
    });

    const baseToolCount = 13 + (modules.eros ? 1 : 0) + (modules.cycle ? 1 : 0) + (modules.dreams ? 1 : 0) + (modules.hobbies ? 1 : 0) + (modules.genesis ? 1 : 0) + 2 + 2 + 3 + 3; // +2 social, +2 economy, +3 analytics, +3 research lab, +1 genesis
    api.logger.info(`[genesis] Registered: 3 hooks, ${baseToolCount + devToolsLoaded} tools (eros=${modules.eros}, cycle=${modules.cycle}, dreams=${modules.dreams}, hobbies=${modules.hobbies}, genesis=${modules.genesis}). Ready.`);
  },
};
