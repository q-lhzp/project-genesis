import type { Physique } from "../types/index.js";
/**
 * Self-expansion project types
 */
export type ProjectType = "script" | "tool" | "skill_upgrade" | "utility" | "documentation";
/**
 * Project status
 */
export type ProjectStatus = "brainstorm" | "planning" | "implementing" | "completed" | "paused";
/**
 * Self-expansion project definition
 */
export interface SelfDevProject {
    id: string;
    name: string;
    description: string;
    type: ProjectType;
    status: ProjectStatus;
    createdAt: string;
    updatedAt: string;
    completedAt?: string;
    topic: string;
    skillFocus?: string;
    filePath?: string;
    progress: number;
    logs: string[];
}
/**
 * Self-expansion state
 */
export interface SelfExpansionState {
    isExpanding: boolean;
    currentProject: SelfDevProject | null;
    totalProjectsCreated: number;
    lastExpansionTime: string | null;
    expansionCount: number;
}
/**
 * Default self-expansion state
 */
export declare const DEFAULT_EXPANSION_STATE: SelfExpansionState;
/**
 * Self-expansion configuration
 */
interface ExpansionConfig {
    energyThreshold: number;
    sentimentThreshold: number;
    cooldownMinutes: number;
    maxActiveProjects: number;
}
/**
 * Get current expansion state
 */
export declare function getExpansionState(): SelfExpansionState;
/**
 * Check if expansion is active
 */
export declare function isSelfExpanding(): boolean;
/**
 * Get current project for context
 */
export declare function getCurrentProject(): SelfDevProject | null;
/**
 * Main process function - call this from tick handler
 */
export declare function processSelfExpansion(workspacePath: string, physique: Physique, config?: ExpansionConfig): Promise<{
    isExpanding: boolean;
    project: SelfDevProject | null;
    newlyStarted: boolean;
}>;
/**
 * Load expansion state from file
 */
export declare function loadExpansionState(workspacePath: string): Promise<SelfExpansionState>;
/**
 * Get projects summary for UI
 */
export declare function getProjectsSummary(workspacePath: string): Promise<{
    total: number;
    completed: number;
    active: {
        name: string;
        progress: number;
        type: string;
    }[];
}>;
export {};
//# sourceMappingURL=self_expansion_engine.d.ts.map