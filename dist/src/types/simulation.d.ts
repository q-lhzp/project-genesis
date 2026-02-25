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
    social?: number;
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
export type LifeStage = "infant" | "child" | "teen" | "adult" | "middle_adult" | "senior";
export interface LifecycleState {
    birth_date: string;
    biological_age_days: number;
    life_stage: LifeStage;
    last_aging_check: string;
    age_progression_enabled: boolean;
    is_asleep?: boolean;
    is_napping?: boolean;
    sleep_start?: string;
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
export interface ReputationEvent {
    timestamp: string;
    circle: string;
    change: number;
    reason: string;
}
export interface ReputationState {
    global_score: number;
    circles: {
        name: string;
        score: number;
    }[];
    events: ReputationEvent[];
    last_propagation: string | null;
}
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
    face_template_id?: string;
    generated_at?: string;
    portrait_style?: "photorealistic" | "anime" | "cyberpunk" | "illustration";
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
    category: "chat" | "request" | "conflict" | "support" | "invitation" | "gossip";
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
export interface Interests {
    hobbies: string[];
    likes: string[];
    wishes: string[];
}
export interface CycleState {
    cycle_length: number;
    current_day: number;
    start_date: string;
    last_advance: string;
    phase: "menstruation" | "follicular" | "ovulation" | "luteal";
    hormones: {
        estrogen: number;
        progesterone: number;
        lh: number;
        fsh: number;
    };
    symptom_modifiers: {
        cramps: number;
        bloating: number;
        fatigue: number;
        mood_swings: number;
        headache: number;
        breast_tenderness: number;
        acne: number;
        appetite_changes: number;
        back_pain: number;
        insomnia: number;
    };
    simulator: {
        active: boolean;
        simulated_day: number;
        custom_modifiers: Record<string, number>;
    };
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
export declare const SENSATIONS: Record<string, Record<string, string[]>>;
export declare const HORMONE_ESTROGEN: number[];
export declare const HORMONE_PROGESTERONE: number[];
export declare const HORMONE_LH: number[];
export declare const HORMONE_FSH: number[];
export declare function getRealWorldSeason(): WorldState["season"];
export declare function getEstimatedWeather(season: WorldState["season"]): {
    weather: WorldState["weather"];
    temp: number;
};
export declare function getSkillMultiplier(skillState: SkillState | null, skillName: string, base?: number): number;
/**
 * Get a sensory description for a need value.
 */
export declare function getSensation(value: number, type: string): string | null;
export declare function getCycleHormones(day: number): CycleState["hormones"];
export declare function getAgeSensation(ageDays: number, stage: LifeStage): string | null;
//# sourceMappingURL=simulation.d.ts.map