import type { Physique } from "../types/index.js";
/**
 * Spatial interaction configuration
 */
interface SpatialConfig {
    mouseMoveEnabled: boolean;
    keyStrokeEnabled: boolean;
    scrollEnabled: boolean;
    sovereigntyOverride: boolean;
    mouseMoveInterval: number;
    keyStrokeProbability: number;
}
/**
 * Spatial interaction state
 */
interface SpatialState {
    isActive: boolean;
    currentMode: "idle" | "coding" | "researching" | "browsing" | "sovereignty_override";
    lastInputTime: string | null;
    mouseMovesCount: number;
    keyStrokesCount: number;
    scrollCount: number;
}
/**
 * Main process function - call from tick handler
 */
export declare function processSpatialInteraction(workspacePath: string, physique: Physique, isResearching: boolean, isExpanding: boolean, config?: SpatialConfig): Promise<{
    isActive: boolean;
    mode: string;
    triggeredInput: boolean;
}>;
/**
 * Get current spatial state for UI
 */
export declare function getSpatialState(workspacePath: string): Promise<SpatialState>;
/**
 * Force stop spatial interaction (emergency override)
 */
export declare function forceStopSpatial(workspacePath: string): Promise<void>;
/**
 * Get head tracking target position for 3D avatar
 */
export declare function getHeadTrackingTarget(screenX: number, screenY: number): {
    x: number;
    y: number;
    z: number;
};
export {};
//# sourceMappingURL=spatial_engine.d.ts.map