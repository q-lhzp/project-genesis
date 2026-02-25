import type { Physique, LifecycleState, SocialState, FinanceState, CycleState, CycleProfile, DreamState, SkillState, PsychState, ReputationState, SocialEvent, WorldState, SocialEntity } from "../types/index.js";
/**
 * Build persona context (State of Being narrative only)
 */
export declare function buildPersonaContext(ph: Physique, lifecycleState: LifecycleState | null, socialState: SocialState | null): string;
/**
 * Get social context for sensory injection
 */
export declare function getSocialContext(socialState: SocialState): {
    urgency: string | null;
    neglected: SocialEntity[];
};
/**
 * Calculate total monthly expenses
 */
export declare function calculateMonthlyExpenses(finance: FinanceState): number;
/**
 * Calculate total monthly income
 */
export declare function calculateMonthlyIncome(finance: FinanceState): number;
/**
 * Get financial context for sensory injection
 */
export declare function getFinancialContext(finance: FinanceState): {
    urgency: string | null;
    upcomingExpenses: string[];
};
/**
 * Calculate urge priority scores
 */
export declare function calculateUrgePriority(ph: Physique, finance: FinanceState | null, socialState: SocialState | null, lifecycleState: LifecycleState | null): {
    type: string;
    score: number;
    reason: string;
}[];
/**
 * Build state of being narrative
 */
export declare function buildStateOfBeing(urgencies: {
    type: string;
    score: number;
    reason: string;
}[], ph: Physique, finance: FinanceState | null, socialState: SocialState | null): string;
/**
 * Build a cohesive sensory context string for injection into the prompt (Always English).
 */
export declare function buildSensoryContext(ph: Physique, lang: "de" | "en", modules: {
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
}, cycleState?: CycleState | null, cycleProfile?: CycleProfile | null, emotionState?: string | null, desireState?: string | null, identityLine?: string | null, growthContext?: string | null, dreamState?: DreamState | null, hobbySuggestion?: string | null, lifecycleState?: LifecycleState | null, socialState?: SocialState | null, financeState?: FinanceState | null, worldState?: WorldState | null, skillState?: SkillState | null, psychState?: PsychState | null, reputationState?: ReputationState | null, socialEvent?: SocialEvent | null): string;
export interface Mem0Config {
    enabled: boolean;
    apiKey: string;
    userId: string;
}
/**
 * Query Mem0 for relevant long-term memories (English Mind).
 */
export declare function queryMem0(query: string, config: Mem0Config, limit?: number): Promise<string>;
/**
 * Store a fact in Mem0 long-term memory.
 */
export declare function storeMem0Fact(fact: string, config: Mem0Config): Promise<boolean>;
/**
 * Get morning market report directive for The Vault
 */
export declare function getVaultMorningReportDirective(): string;
//# sourceMappingURL=context-engine.d.ts.map