import type { Physique } from "../types/index.js";
/**
 * Physical motion states for the avatar
 */
export interface MotionState {
    idle: "neutral" | "energetic" | "slumped" | "fidgeting" | "shaking" | "breathing_heavy" | "walking" | "sleeping" | "researching" | "expanding" | "social" | "trading" | "strained" | "dancing";
    breathingRate: number;
    posture: number;
    movementIntensity: number;
    shakeAmplitude: number;
    fidgetFrequency: number;
    isSleeping: boolean;
}
/**
 * Default motion state
 */
export declare const DEFAULT_MOTION: MotionState;
/**
 * Configuration for motion thresholds
 */
interface MotionConfig {
    bladderHighThreshold: number;
    stressHighThreshold: number;
    energyVeryHighThreshold: number;
    energyLowThreshold: number;
}
/**
 * Maps biological needs to body motion states
 */
export declare function mapNeedsToMotion(needs: Physique["needs"], config?: MotionConfig, isDreaming?: boolean, isResearching?: boolean, isExpanding?: boolean, hasSocialEvent?: boolean, isTrading?: boolean, isStrained?: boolean, isDancing?: boolean): MotionState;
/**
 * Get current location from physique
 */
export declare function getCurrentLocation(physique: Physique): string;
/**
 * Detect if location has changed and return walking state
 */
export declare function detectMovement(physique: Physique, forceLocation?: string | null): {
    isMoving: boolean;
    targetPose: string;
};
/**
 * Update avatar motion in the dashboard
 */
export declare function updateAvatarMotion(workspacePath: string, motion: MotionState, isMoving?: boolean): Promise<void>;
/**
 * Main function to sync avatar motion
 * Call this from the tick handler in index.ts
 */
export declare function syncAvatarMotion(workspacePath: string, physique: Physique, isDreaming?: boolean, isResearching?: boolean, isExpanding?: boolean, hasSocialEvent?: boolean, isTrading?: boolean, isStrained?: boolean, isDancing?: boolean): Promise<MotionState>;
/**
 * Trigger walking animation when location changes
 * Call this from reality_move tool
 */
export declare function triggerWalkingAnimation(workspacePath: string, fromLocation: string, toLocation: string): Promise<void>;
export {};
//# sourceMappingURL=motion_mapper.d.ts.map