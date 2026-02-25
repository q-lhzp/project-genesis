import type { Physique } from "../types/index.js";
/**
 * Dream state configuration
 */
interface DreamConfig {
    sleepStartHour: number;
    sleepEndHour: number;
    energyThreshold: number;
    dreamDurationMs: number;
}
/**
 * Dream state tracking
 */
interface DreamState {
    isDreaming: boolean;
    sleepStartTime: string | null;
    dreamCount: number;
    lastWakeTime: string | null;
    lastDreamSummary: string | null;
}
/**
 * Check if Q should enter dream mode
 */
export declare function shouldEnterDreamMode(physique: Physique, config?: DreamConfig): boolean;
/**
 * Check if Q should wake up
 */
export declare function shouldWakeUp(physique: Physique, config?: DreamConfig): boolean;
/**
 * Main dream cycle handler - call this from tick
 */
export declare function processDreamState(workspacePath: string, physique: Physique): Promise<{
    isDreaming: boolean;
    dreamSummary: string | null;
    vitalsRecovered: boolean;
}>;
/**
 * Get current dream state (for UI display)
 */
export declare function getDreamState(): DreamState;
/**
 * Check if sleep is currently locked (during dream mode)
 */
export declare function isSleepLocked(): boolean;
/**
 * Get morning report (for context injection after waking)
 */
export declare function getMorningReport(): string | null;
export {};
//# sourceMappingURL=dream_engine.d.ts.map