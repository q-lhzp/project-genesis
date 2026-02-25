// ---------------------------------------------------------------------------
// Motion Mapper - Maps biological needs to body poses and animations
// Phase 25: Physical Reaction (Idle Animations)
// ---------------------------------------------------------------------------
import { writeJson } from "../utils/persistence.js";
import { join } from "node:path";
/**
 * Default motion state
 */
export const DEFAULT_MOTION = {
    idle: "neutral",
    breathingRate: 1.0,
    posture: 0.5,
    movementIntensity: 0.1,
    shakeAmplitude: 0,
    fidgetFrequency: 0,
    isSleeping: false,
};
const DEFAULT_CONFIG = {
    bladderHighThreshold: 80,
    stressHighThreshold: 80,
    energyVeryHighThreshold: 90,
    energyLowThreshold: 20,
};
/**
 * Maps biological needs to body motion states
 */
export function mapNeedsToMotion(needs, config = DEFAULT_CONFIG, isDreaming = false, isResearching = false, isExpanding = false, hasSocialEvent = false, isTrading = false, isStrained = false, isDancing = false) {
    const motion = { ...DEFAULT_MOTION };
    // Phase 27: SLEEP STATE - Override all motion
    if (isDreaming) {
        motion.idle = "sleeping";
        motion.breathingRate = 0.4; // Very slow, deep breathing
        motion.posture = 0.1; // Lying down/slumped
        motion.movementIntensity = 0; // Completely still
        motion.shakeAmplitude = 0;
        motion.fidgetFrequency = 0;
        motion.isSleeping = true;
        return motion;
    }
    // Phase 28: RESEARCH STATE - Focused sitting at desk
    if (isResearching) {
        motion.idle = "researching";
        motion.breathingRate = 0.8; // Calm, focused breathing
        motion.posture = 0.9; // Upright, attentive
        motion.movementIntensity = 0.05; // Very still, slight movement
        motion.shakeAmplitude = 0;
        motion.fidgetFrequency = 0;
        motion.isSleeping = false;
        return motion;
    }
    // Phase 34: EXPANDING STATE - Intense coding/development
    if (isExpanding) {
        motion.idle = "expanding";
        motion.breathingRate = 0.9; // Slightly elevated, focused
        motion.posture = 0.95; // Very upright, leaning forward
        motion.movementIntensity = 0.2; // Slight typing/working motion
        motion.shakeAmplitude = 0;
        motion.fidgetFrequency = 0;
        motion.isSleeping = false;
        return motion;
    }
    // Phase 35: SOCIAL STATE - Checking phone/notification
    if (hasSocialEvent) {
        motion.idle = "social";
        motion.breathingRate = 1.1; // Slightly elevated, curious
        motion.posture = 0.85; // Attentive, looking at phone/device
        motion.movementIntensity = 0.15; // Slight movement, checking device
        motion.shakeAmplitude = 0;
        motion.fidgetFrequency = 0.2; // Fidgeting with phone
        motion.isSleeping = false;
        return motion;
    }
    // Phase 37: TRADING STATE - Focused monitoring markets
    if (isTrading) {
        motion.idle = "trading";
        motion.breathingRate = 1.0; // Controlled, focused
        motion.posture = 0.9; // Upright, attentive to screen
        motion.movementIntensity = 0.1; // Subtle movements, checking prices
        motion.shakeAmplitude = 0;
        motion.fidgetFrequency = 0.15; // Slight nervous energy
        motion.isSleeping = false;
        return motion;
    }
    // Phase 40: STRAINED STATE - Hardware overload makes Q feel exhausted
    if (isStrained) {
        motion.idle = "strained";
        motion.breathingRate = 1.3; // Heavy breathing from strain
        motion.posture = 0.4; // Slumped, tired
        motion.movementIntensity = 0.15; // Weak movements
        motion.shakeAmplitude = 0.1; // Slight tremor
        motion.fidgetFrequency = 0.3; // Restless
        motion.isSleeping = false;
        return motion;
    }
    // Phase 40: DANCING STATE - Music is playing, Q feels the rhythm
    if (isDancing) {
        motion.idle = "dancing";
        motion.breathingRate = 1.2; // Rhythmic breathing
        motion.posture = 0.8; // Upright, moving
        motion.movementIntensity = 0.6; // Active movement
        motion.shakeAmplitude = 0;
        motion.fidgetFrequency = 0.5; // Rhythmic fidgeting
        motion.isSleeping = false;
        return motion;
    }
    const bladder = needs.bladder ?? 50;
    const stress = needs.stress ?? 0;
    const energy = needs.energy ?? 50;
    const hygiene = needs.hygiene ?? 50;
    // === FIDGETING (High Bladder) ===
    if (bladder > config.bladderHighThreshold) {
        motion.idle = "fidgeting";
        motion.fidgetFrequency = (bladder - config.bladderHighThreshold) / 20; // 0-1
        motion.movementIntensity = 0.3 + motion.fidgetFrequency * 0.4;
    }
    // === SHAKING / TREMBLING (High Stress) ===
    else if (stress > config.stressHighThreshold) {
        motion.idle = "shaking";
        motion.shakeAmplitude = (stress - config.stressHighThreshold) / 20; // 0-1
        motion.movementIntensity = 0.3 + motion.shakeAmplitude * 0.5;
        motion.breathingRate = 1.5 + motion.shakeAmplitude; // Fast breathing
    }
    // === HEAVY BREATHING (Moderate-High Stress) ===
    else if (stress > 50) {
        motion.idle = "breathing_heavy";
        motion.breathingRate = 1.2 + (stress - 50) / 50; // 1.2 - 1.8
        motion.movementIntensity = 0.2;
    }
    // === ENERGETIC (Very High Energy) ===
    else if (energy > config.energyVeryHighThreshold) {
        motion.idle = "energetic";
        motion.posture = 1.0; // Upright
        motion.movementIntensity = 0.3;
        motion.breathingRate = 1.2;
    }
    // === SLUMPED (Low Energy) ===
    else if (energy < config.energyLowThreshold) {
        motion.idle = "slumped";
        motion.posture = 0.0; // Slumped
        motion.movementIntensity = 0.05;
        motion.breathingRate = 0.6; // Slow breathing
    }
    // === NEUTRAL (Default) ===
    else {
        motion.idle = "neutral";
        motion.posture = 0.5;
        motion.movementIntensity = 0.1;
        motion.breathingRate = 1.0;
    }
    return motion;
}
/**
 * Get current location from physique
 */
export function getCurrentLocation(physique) {
    return physique.current_location || "unknown";
}
/**
 * Previous location tracking for movement detection
 */
let previousLocation = null;
/**
 * Detect if location has changed and return walking state
 */
export function detectMovement(physique, forceLocation = null) {
    const currentLocation = forceLocation || getCurrentLocation(physique);
    if (previousLocation && previousLocation !== currentLocation) {
        // Location changed - trigger walking
        previousLocation = currentLocation;
        return { isMoving: true, targetPose: "walking" };
    }
    previousLocation = currentLocation;
    return { isMoving: false, targetPose: "idle" };
}
/**
 * Update avatar motion in the dashboard
 */
export async function updateAvatarMotion(workspacePath, motion, isMoving = false) {
    const avatarStatePath = join(workspacePath, "memory", "reality", "avatar_state.json");
    const state = {
        action: isMoving ? "motion_walking" : "motion",
        motion: motion,
        isWalking: isMoving,
        timestamp: new Date().toISOString()
    };
    await writeJson(avatarStatePath, state);
    // Also try to notify via HTTP (non-blocking)
    notifyDashboardHttp(motion, isMoving).catch(() => {
        // Ignore HTTP errors
    });
}
/**
 * Non-blocking HTTP notification to dashboard
 */
async function notifyDashboardHttp(motion, isWalking) {
    try {
        const http = await import("node:http");
        const postData = JSON.stringify({
            action: isWalking ? "motion_walking" : "motion",
            motion: motion,
            isWalking: isWalking
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
        // Module not available
    }
}
/**
 * Main function to sync avatar motion
 * Call this from the tick handler in index.ts
 */
export async function syncAvatarMotion(workspacePath, physique, isDreaming = false, isResearching = false, isExpanding = false, hasSocialEvent = false, isTrading = false, isStrained = false, isDancing = false) {
    // Calculate motion from needs (pass isDreaming/isResearching/isExpanding/hasSocialEvent/isTrading/isStrained/isDancing for special states)
    const motion = mapNeedsToMotion(physique.needs, DEFAULT_CONFIG, isDreaming, isResearching, isExpanding, hasSocialEvent, isTrading, isStrained, isDancing);
    // Check for movement (only if not sleeping, researching, expanding, or processing social)
    const { isMoving } = (isDreaming || isResearching || isExpanding || hasSocialEvent) ? { isMoving: false } : detectMovement(physique);
    // Update avatar in dashboard
    await updateAvatarMotion(workspacePath, motion, isMoving);
    return motion;
}
/**
 * Trigger walking animation when location changes
 * Call this from reality_move tool
 */
export async function triggerWalkingAnimation(workspacePath, fromLocation, toLocation) {
    const avatarStatePath = join(workspacePath, "memory", "reality", "avatar_state.json");
    const state = {
        action: "motion_walking",
        motion: {
            idle: "walking",
            breathingRate: 1.5,
            posture: 0.8,
            movementIntensity: 0.8,
            shakeAmplitude: 0,
            fidgetFrequency: 0
        },
        isWalking: true,
        from: fromLocation,
        to: toLocation,
        timestamp: new Date().toISOString()
    };
    await writeJson(avatarStatePath, state);
    // Also notify via HTTP
    notifyDashboardHttpWalking(toLocation).catch(() => { });
}
/**
 * Notify dashboard of walking to new location
 */
async function notifyDashboardHttpWalking(toLocation) {
    try {
        const http = await import("node:http");
        const postData = JSON.stringify({
            action: "motion_walking",
            motion: {
                idle: "walking",
                breathingRate: 1.5,
                posture: 0.8,
                movementIntensity: 0.8,
                shakeAmplitude: 0,
                fidgetFrequency: 0
            },
            isWalking: true,
            toLocation: toLocation
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
        // Ignore errors
    }
}
//# sourceMappingURL=motion_mapper.js.map