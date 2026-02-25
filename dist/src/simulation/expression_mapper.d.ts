import type { Physique } from "../types/index.js";
/**
 * BlendShape weights for VRM expressions (0-1 range)
 */
export interface BlendShapeWeights {
    joy: number;
    angry: number;
    sad: number;
    fear: number;
    surprise: number;
    neutral: number;
    relaxed: number;
    blinkLeft: number;
    blinkRight: number;
    blink: number;
    lookUp: number;
    lookDown: number;
    lookLeft: number;
    lookRight: number;
    sleeping: number;
}
/**
 * Default BlendShape weights (all neutral)
 */
export declare const DEFAULT_BLENDSHAPES: BlendShapeWeights;
/**
 * Configuration for expression mapping thresholds
 */
interface ExpressionConfig {
    stressJoyThreshold: number;
    stressHighThreshold: number;
    energyLowThreshold: number;
    arousalHighThreshold: number;
    hungerLowThreshold: number;
    thirstLowThreshold: number;
    hygieneLowThreshold: number;
}
/**
 * Maps biological needs to VRM BlendShape weights
 *
 * Logic:
 * - Joy: Low stress (< 20) + high energy (> 50) + needs met
 * - Angry: High stress (> 80) + low needs satisfaction
 * - Sad: High stress (> 60) + low energy (< 30)
 * - Tired: Low energy (< 20)
 * - Blush/Excited: High arousal (> 60) + eros module active
 * - Sleeping: Dream mode active -> eyes closed, neutral face
 * - Expanding (Phase 34): Flow state with focused expression + slight achievement smile
 */
export declare function mapNeedsToBlendShapes(needs: Physique["needs"], config?: ExpressionConfig, isDreaming?: boolean, isResearching?: boolean, isExpanding?: boolean, hasSocialEvent?: boolean, isTrading?: boolean, isStrained?: boolean, isDancing?: boolean): BlendShapeWeights;
/**
 * Interpolate between two blend shape weights (lerp)
 * @param from Starting weights
 * @param to Target weights
 * @param t Interpolation factor (0-1)
 */
export declare function lerpBlendShapes(from: BlendShapeWeights, to: BlendShapeWeights, t: number): BlendShapeWeights;
/**
 * Update avatar expression in the dashboard
 * This sends the blend shape weights to the frontend via the state file
 */
export declare function updateAvatarExpression(workspacePath: string, blendShapes: BlendShapeWeights): Promise<void>;
/**
 * Main function to map physique needs to avatar expressions
 * Call this from the tick handler in index.ts
 */
export declare function syncAvatarExpressions(workspacePath: string, physique: Physique, isDreaming?: boolean, isResearching?: boolean, isExpanding?: boolean, hasSocialEvent?: boolean, isTrading?: boolean, isStrained?: boolean, isDancing?: boolean): Promise<BlendShapeWeights>;
export {};
//# sourceMappingURL=expression_mapper.d.ts.map