import type { LifecycleState, LifeStage, LifeStageMultipliers } from "../types/index.js";
/**
 * Calculate biological age in days from birthDate and initialAgeDays
 */
export declare function calculateAgeDays(birthDate: string, initialAgeDays: number): number;
/**
 * Convert age in days to years (decimal)
 */
export declare function daysToYears(days: number): number;
/**
 * Determine life stage based on age in days
 */
export declare function getLifeStage(ageDays: number): LifeStage;
/**
 * Get metabolism rate multipliers based on life stage
 */
export declare function getLifeStageMultipliers(stage: LifeStage): LifeStageMultipliers;
/**
 * Create default lifecycle state
 */
export declare function getDefaultLifecycleState(birthDate?: string, initialAgeDays?: number): LifecycleState;
/**
 * Update lifecycle - calculate aging and stage transitions
 */
export declare function updateLifecycle(lifecycle: LifecycleState): boolean;
/**
 * Advance lifecycle state - calculates aging and stage transitions
 */
export declare function advanceLifecycle(lifecycleState: LifecycleState, birthDate: string, initialAgeDays: number): {
    changed: boolean;
    newStage?: LifeStage;
};
/**
 * Get age sensation based on life stage
 */
export declare function getAgeSensation(ageDays: number, stage: LifeStage): string | null;
//# sourceMappingURL=lifecycle.d.ts.map