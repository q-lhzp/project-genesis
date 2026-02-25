// ---------------------------------------------------------------------------
// Expression Mapper - Maps biological needs and emotions to VRM BlendShapes
// Phase 23: Emotional Expressiveness (Face-Sync)
// ---------------------------------------------------------------------------
import { writeJson } from "../utils/persistence.js";
import { join } from "node:path";
/**
 * Default BlendShape weights (all neutral)
 */
export const DEFAULT_BLENDSHAPES = {
    joy: 0,
    angry: 0,
    sad: 0,
    fear: 0,
    surprise: 0,
    neutral: 1,
    relaxed: 0,
    blinkLeft: 0,
    blinkRight: 0,
    blink: 0,
    lookUp: 0,
    lookDown: 0,
    lookLeft: 0,
    lookRight: 0,
    sleeping: 0,
};
const DEFAULT_CONFIG = {
    stressJoyThreshold: 20, // Low stress = happy
    stressHighThreshold: 80, // High stress = angry/sad
    energyLowThreshold: 20, // Low energy = tired
    arousalHighThreshold: 60, // High arousal = excited
    hungerLowThreshold: 30, // Hungry = unhappy
    thirstLowThreshold: 30, // Thirsty = unhappy
    hygieneLowThreshold: 30, // Dirty = unhappy
};
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
export function mapNeedsToBlendShapes(needs, config = DEFAULT_CONFIG, isDreaming = false, isResearching = false, isExpanding = false, hasSocialEvent = false, isTrading = false, isStrained = false, isDancing = false) {
    const weights = { ...DEFAULT_BLENDSHAPES };
    // Phase 27: SLEEP STATE - Override all expressions
    if (isDreaming) {
        weights.joy = 0;
        weights.angry = 0;
        weights.sad = 0;
        weights.fear = 0;
        weights.neutral = 0.8;
        weights.relaxed = 1.0;
        weights.blinkLeft = 1.0;
        weights.blinkRight = 1.0;
        weights.blink = 1.0;
        weights.sleeping = 1.0;
        return weights;
    }
    // Phase 28: RESEARCH STATE - Concentrated/Focused expression
    if (isResearching) {
        weights.joy = 0.2; // Slight interest
        weights.angry = 0;
        weights.sad = 0;
        weights.fear = 0;
        weights.surprise = 0;
        weights.neutral = 0.8; // Focused
        weights.relaxed = 0.3;
        weights.blinkLeft = 0.1; // Occasional blink
        weights.blinkRight = 0.1;
        weights.blink = 0.1;
        weights.sleeping = 0;
        return weights;
    }
    // Phase 34: EXPANDING STATE - Flow state (focused + achievement)
    if (isExpanding) {
        weights.joy = 0.6; // Achievement satisfaction
        weights.angry = 0;
        weights.sad = 0;
        weights.fear = 0;
        weights.surprise = 0;
        weights.neutral = 0.3;
        weights.relaxed = 0.4;
        weights.blinkLeft = 0.15;
        weights.blinkRight = 0.15;
        weights.blink = 0.15;
        weights.sleeping = 0;
        return weights;
    }
    // Phase 35: SOCIAL STATE - Surprised/curious about message
    if (hasSocialEvent) {
        weights.joy = 0.2;
        weights.angry = 0;
        weights.sad = 0;
        weights.fear = 0;
        weights.surprise = 0.8; // Surprised! Got a message
        weights.neutral = 0.1;
        weights.relaxed = 0.2;
        weights.blinkLeft = 0.05;
        weights.blinkRight = 0.05;
        weights.blink = 0.05;
        weights.sleeping = 0;
        return weights;
    }
    // Phase 37: TRADING STATE - Focused + slight nervous excitement
    if (isTrading) {
        weights.joy = 0.3; // Slight excitement from potential gains
        weights.angry = 0;
        weights.sad = 0;
        weights.fear = 0;
        weights.surprise = 0.1;
        weights.neutral = 0.5; // Focused concentration
        weights.relaxed = 0.1;
        weights.blinkLeft = 0.1;
        weights.blinkRight = 0.1;
        weights.blink = 0.1;
        weights.sleeping = 0;
        return weights;
    }
    // Phase 40: STRAINED STATE - Hardware overload
    if (isStrained) {
        weights.joy = 0;
        weights.angry = 0.2; // Frustration
        weights.sad = 0.3; // Exhaustion sadness
        weights.fear = 0.1;
        weights.surprise = 0;
        weights.neutral = 0.4;
        weights.relaxed = 0;
        weights.blinkLeft = 0.2; // Tired eyes
        weights.blinkRight = 0.2;
        weights.blink = 0.2;
        weights.sleeping = 0;
        return weights;
    }
    // Phase 40: DANCING STATE - Music is playing!
    if (isDancing) {
        weights.joy = 0.7; // Pure joy!
        weights.angry = 0;
        weights.sad = 0;
        weights.fear = 0;
        weights.surprise = 0.1;
        weights.neutral = 0.1;
        weights.relaxed = 0.2;
        weights.blinkLeft = 0.1;
        weights.blinkRight = 0.1;
        weights.blink = 0.1;
        weights.sleeping = 0;
        return weights;
    }
    const stress = needs.stress ?? 0;
    const energy = needs.energy ?? 50;
    const arousal = needs.arousal ?? 0;
    const hunger = needs.hunger ?? 50;
    const thirst = needs.thirst ?? 50;
    const hygiene = needs.hygiene ?? 50;
    // Reset neutral to calculate new state
    weights.neutral = 0;
    // === JOY / HAPPINESS ===
    // Conditions: Low stress, high energy, basic needs met
    if (stress < config.stressJoyThreshold && energy > 50) {
        // Calculate joy intensity based on how well needs are met
        const needsSatisfaction = (hunger + thirst + hygiene) / 3;
        if (needsSatisfaction > 50) {
            weights.joy = Math.min(1, (100 - stress) / 100 * energy / 100 * needsSatisfaction / 100 + 0.2);
            weights.neutral = 0;
        }
    }
    // === ANGER ===
    // Conditions: Very high stress (> 80)
    if (stress > config.stressHighThreshold) {
        weights.angry = Math.min(1, (stress - config.stressHighThreshold) / 20);
        weights.neutral = 0;
    }
    // === SAD / GRIEF ===
    // Conditions: High stress + low energy
    if (stress > 60 && energy < 40) {
        const sadnessIntensity = Math.min(1, (stress - 40) / 60 * (40 - energy) / 40);
        weights.sad = Math.max(weights.sad, sadnessIntensity);
        weights.neutral = 0;
    }
    // === TIRED / EXHAUSTED ===
    // Conditions: Low energy (< 20)
    if (energy < config.energyLowThreshold) {
        const tiredness = 1 - (energy / config.energyLowThreshold);
        weights.sad = Math.max(weights.sad, tiredness * 0.5);
        // Heavy lids - this would affect eye blend shapes in a full VRM
        weights.blink = tiredness * 0.3; // Partially closed eyes
        weights.neutral = 0;
    }
    // === SURPRISE ===
    // Conditions: Sudden need drop (thirst or hunger very low)
    if (thirst < 10 || hunger < 10) {
        weights.surprise = Math.min(1, Math.max(weights.surprise, 0.5));
        weights.neutral = 0;
    }
    // === FEAR / WORRY ===
    // Conditions: Very low hygiene + high stress
    if (hygiene < config.hygieneLowThreshold && stress > 40) {
        weights.fear = Math.min(1, (config.hygieneLowThreshold - hygiene) / 50 * stress / 100);
        weights.neutral = 0;
    }
    // === BLUSH / EXCITED (if eros active) ===
    // Note: Actual blush requires VRM-specific blend shape
    // This would set a blush-specific morph target in full implementation
    if (arousal > config.arousalHighThreshold) {
        // In a full VRM implementation, this would trigger a blush morph
        // weights.blush = (arousal - config.arousalHighThreshold) / 40;
    }
    // === NEUTRAL (fallback if nothing else) ===
    if (weights.joy < 0.1 && weights.angry < 0.1 && weights.sad < 0.1 &&
        weights.fear < 0.1 && weights.surprise < 0.1) {
        weights.neutral = 1;
    }
    return weights;
}
/**
 * Interpolate between two blend shape weights (lerp)
 * @param from Starting weights
 * @param to Target weights
 * @param t Interpolation factor (0-1)
 */
export function lerpBlendShapes(from, to, t) {
    // Clamp t to 0-1
    t = Math.max(0, Math.min(1, t));
    const result = { ...to };
    for (const key of Object.keys(from)) {
        result[key] = from[key] + (to[key] - from[key]) * t;
    }
    return result;
}
/**
 * Update avatar expression in the dashboard
 * This sends the blend shape weights to the frontend via the state file
 */
export async function updateAvatarExpression(workspacePath, blendShapes) {
    const avatarStatePath = join(workspacePath, "memory", "reality", "avatar_state.json");
    const state = {
        action: "expression",
        blendShapes: blendShapes,
        timestamp: new Date().toISOString()
    };
    await writeJson(avatarStatePath, state);
    // Also try to notify via HTTP (non-blocking)
    notifyDashboardHttp(blendShapes).catch(() => {
        // Ignore HTTP errors - dashboard may not be running
    });
}
/**
 * Non-blocking HTTP notification to dashboard
 */
async function notifyDashboardHttp(blendShapes) {
    try {
        const http = await import("node:http");
        const postData = JSON.stringify({
            action: "expression",
            blendShapes: blendShapes
        });
        const options = {
            hostname: "127.0.0.1",
            port: 8080,
            path: "/api/avatar/update",
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Content-Length": Buffer.byteLength(postData)
            }
        };
        return new Promise((resolve) => {
            const req = http.request(options, (res) => {
                resolve();
            });
            req.on("error", () => resolve());
            req.write(postData);
            req.end();
        });
    }
    catch {
        // Module not available or other error
    }
}
/**
 * Main function to map physique needs to avatar expressions
 * Call this from the tick handler in index.ts
 */
export async function syncAvatarExpressions(workspacePath, physique, isDreaming = false, isResearching = false, isExpanding = false, hasSocialEvent = false, isTrading = false, isStrained = false, isDancing = false) {
    // Calculate blend shapes from needs (pass isDreaming/isResearching/isExpanding/hasSocialEvent/isTrading/isStrained/isDancing for special states)
    const blendShapes = mapNeedsToBlendShapes(physique.needs, DEFAULT_CONFIG, isDreaming, isResearching, isExpanding, hasSocialEvent, isTrading, isStrained, isDancing);
    // Update avatar in dashboard
    await updateAvatarExpression(workspacePath, blendShapes);
    return blendShapes;
}
//# sourceMappingURL=expression_mapper.js.map