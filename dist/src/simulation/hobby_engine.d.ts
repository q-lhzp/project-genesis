import type { Physique } from "../types/index.js";
/**
 * Research state configuration
 */
interface HobbyConfig {
    energyThreshold: number;
    researchDurationMs: number;
    cooldownMinutes: number;
}
/**
 * Current research state
 */
interface ResearchState {
    isResearching: boolean;
    currentTopic: string | null;
    currentPhase: "idle" | "selecting" | "searching" | "summarizing" | "deciding";
    lastResearchTime: string | null;
    sentiment: number;
}
/**
 * Check if Q should start researching
 */
export declare function shouldStartResearch(physique: Physique, config?: HobbyConfig): boolean;
/**
 * Process hobby/research activity
 * Call this from tick handler
 */
export declare function processHobbyActivity(workspacePath: string, physique: Physique, config?: HobbyConfig): Promise<{
    isResearching: boolean;
    currentTopic: string | null;
    findings: string | null;
    sentiment: number;
}>;
/**
 * Get current research state (for UI/3D sync)
 */
export declare function getResearchState(): ResearchState;
/**
 * Check if currently researching
 */
export declare function isCurrentlyResearching(): boolean;
/**
 * Get research summary for context injection
 */
export declare function getResearchContext(): string | null;
export {};
//# sourceMappingURL=hobby_engine.d.ts.map