import type { Physique, SocialEvent } from "../types/index.js";
/**
 * Social engine configuration
 */
interface SocialConfig {
    triggerChance: number;
    cooldownMinutes: number;
    maxPendingEvents: number;
    bondHighThreshold: number;
    bondLowThreshold: number;
}
/**
 * Social state tracking
 */
interface SocialState {
    lastEventTime: string | null;
    pendingCount: number;
    totalEventsTriggered: number;
}
/**
 * Main process function - call from tick handler
 */
export declare function processSocialDynamics(workspacePath: string, physique: Physique, config?: SocialConfig, isDe?: boolean): Promise<{
    hasNewEvent: boolean;
    event: SocialEvent | null;
    emotionalImpact: {
        stressChange: number;
        joyChange: number;
    } | null;
}>;
/**
 * Get pending events for UI
 */
export declare function getPendingEvents(workspacePath: string): Promise<SocialEvent[]>;
/**
 * Mark event as processed
 */
export declare function markEventProcessed(workspacePath: string, eventId: string): Promise<void>;
/**
 * Get current social engine state
 */
export declare function getSocialEngineState(workspacePath: string): Promise<SocialState>;
export {};
//# sourceMappingURL=social_engine.d.ts.map