// ---------------------------------------------------------------------------
// Expression Mapper - Maps biological needs and emotions to VRM BlendShapes
// Phase 23: Emotional Expressiveness (Face-Sync)
// ---------------------------------------------------------------------------

import { readJson, writeJson } from "../utils/persistence.js";
import { join } from "node:path";
import type { Physique } from "../types/index.js";
import type { SimulationPaths } from "../types/paths.js";

/**
 * BlendShape weights for VRM expressions (0-1 range)
 * Extended from 16 to 52+ expressions for comprehensive facial animation
 */
export interface BlendShapeWeights {
  // Core emotions (8)
  joy: number;           // Happy/Smile
  angry: number;        // Angry expression
  sad: number;          // Sad/Grief expression
  fear: number;         // Fear expression
  surprise: number;     // Surprised expression
  neutral: number;      // Neutral face
  relaxed: number;      // Relaxed
  disgusted: number;    // Disgust expression

  // Eye states (10)
  blinkLeft: number;    // Left eye blink
  blinkRight: number;   // Right eye blink
  blink: number;        // Both eyes blink
  lookUp: number;       // Eyes looking up
  lookDown: number;     // Eyes looking down
  lookLeft: number;     // Eyes looking left
  lookRight: number;    // Eyes looking right
  eyeWiden: number;     // Eyes widen (surprise/delight)
  eyeSquint: number;     // Squinting (concentration/pain)
  eyeClose: number;      // Eyes fully closed

  // Eyebrow expressions (6)
  browUp: number;       // Brows raised
  browDown: number;     // Brows furrowed
  browOuterUp: number;  // Outer brow raise
  browInnerUp: number;  // Inner brow raise
  browLeft: number;     // Brows to left
  browRight: number;    // Brows to right

  // Nose expressions (2)
  noseSneer: number;    // Nose sneer
  noseWrinkle: number;  // Nose wrinkle

  // Mouth expressions (20)
  mouthOpen: number;    // Mouth open
  mouthClose: number;   // Mouth closed
  jawOpen: number;      // Jaw open
  jawClose: number;     // Jaw close
  jawLeft: number;      // Jaw to left
  jawRight: number;     // Jaw to right
  mouthFunnel: number;  // Mouth funnel (kissing)
  mouthPucker: number;  // Puckered lips
  mouthLeft: number;    // Mouth to left
  mouthRight: number;   // Mouth to right
  mouthSmileLeft: number;   // Smile left side
  mouthSmileRight: number;  // Smile right side
  mouthFrownLeft: number;   // Frown left side
  mouthFrownRight: number;  // Frown right side
  mouthGrimace: number;     // Grimace
  mouthLaugh: number;       // Laughing
  mouthShrugUpper: number;  // Upper lip shrug
  mouthShrugLower: number;  // Lower lip shrug
  mouthRoll: number;        // Tongue rolling
  tongueOut: number;        // Tongue out

  // Cheek expressions (4)
  cheekPuff: number;    // Cheeks puffed
  cheekSquintLeft: number;  // Left cheek raise
  cheekSquintRight: number; // Right cheek raise
  cheekSuck: number;     // Cheeks sucked in

  // Chin expressions (4)
  chinUp: number;       // Chin up
  chinDown: number;     // Chin down
  chinSideLeft: number; // Chin to left
  chinSideRight: number;// Chin to right

  // Special states (4)
  sleeping: number;     // Sleep state (0=awake, 1=fully asleep)
  breathing: number;    // Breathing animation
  yawning: number;      // Yawning
  swallowing: number;   // Swallowing
}

/**
 * Default BlendShape weights (all neutral)
 */
export const DEFAULT_BLENDSHAPES: BlendShapeWeights = {
  // Core emotions
  joy: 0,
  angry: 0,
  sad: 0,
  fear: 0,
  surprise: 0,
  neutral: 1,
  relaxed: 0,
  disgusted: 0,
  // Eye states
  blinkLeft: 0,
  blinkRight: 0,
  blink: 0,
  lookUp: 0,
  lookDown: 0,
  lookLeft: 0,
  lookRight: 0,
  eyeWiden: 0,
  eyeSquint: 0,
  eyeClose: 0,
  // Eyebrows
  browUp: 0,
  browDown: 0,
  browOuterUp: 0,
  browInnerUp: 0,
  browLeft: 0,
  browRight: 0,
  // Nose
  noseSneer: 0,
  noseWrinkle: 0,
  // Mouth
  mouthOpen: 0,
  mouthClose: 1,
  jawOpen: 0,
  jawClose: 1,
  jawLeft: 0,
  jawRight: 0,
  mouthFunnel: 0,
  mouthPucker: 0,
  mouthLeft: 0,
  mouthRight: 0,
  mouthSmileLeft: 0,
  mouthSmileRight: 0,
  mouthFrownLeft: 0,
  mouthFrownRight: 0,
  mouthGrimace: 0,
  mouthLaugh: 0,
  mouthShrugUpper: 0,
  mouthShrugLower: 0,
  mouthRoll: 0,
  tongueOut: 0,
  // Cheeks
  cheekPuff: 0,
  cheekSquintLeft: 0,
  cheekSquintRight: 0,
  cheekSuck: 0,
  // Chin
  chinUp: 0,
  chinDown: 0,
  chinSideLeft: 0,
  chinSideRight: 0,
  // Special states
  sleeping: 0,
  breathing: 0,
  yawning: 0,
  swallowing: 0,
};

/**
 * Configuration for expression mapping thresholds
 */
interface ExpressionConfig {
  stressJoyThreshold: number;       // Below this stress -> happy (0-100)
  stressHighThreshold: number;      // Above this stress -> angry/sad (0-100)
  energyLowThreshold: number;       // Below this energy -> tired/neutral (0-100)
  arousalHighThreshold: number;     // Above this arousal -> blush/excited (0-100)
  hungerLowThreshold: number;       // Below this hunger -> unhappy (0-100)
  thirstLowThreshold: number;       // Below this thirst -> unhappy (0-100)
  hygieneLowThreshold: number;       // Below this hygiene -> unhappy (0-100)
}

const DEFAULT_CONFIG: ExpressionConfig = {
  stressJoyThreshold: 20,       // Low stress = happy
  stressHighThreshold: 80,      // High stress = angry/sad
  energyLowThreshold: 20,       // Low energy = tired
  arousalHighThreshold: 60,    // High arousal = excited
  hungerLowThreshold: 30,      // Hungry = unhappy
  thirstLowThreshold: 30,      // Thirsty = unhappy
  hygieneLowThreshold: 30,      // Dirty = unhappy
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
export function mapNeedsToBlendShapes(
  needs: Physique["needs"],
  config: ExpressionConfig = DEFAULT_CONFIG,
  isDreaming: boolean = false,
  isResearching: boolean = false,
  isExpanding: boolean = false,
  hasSocialEvent: boolean = false,
  isTrading: boolean = false,
  isStrained: boolean = false,
  isDancing: boolean = false
): BlendShapeWeights {
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
    weights.eyeClose = 1.0;
    weights.sleeping = 1.0;
    weights.mouthClose = 1.0;
    weights.jawClose = 1.0;
    return weights;
  }

  // Phase 28: RESEARCH STATE - Concentrated/Focused expression
  if (isResearching) {
    weights.joy = 0.2;  // Slight interest
    weights.angry = 0;
    weights.sad = 0;
    weights.fear = 0;
    weights.surprise = 0;
    weights.neutral = 0.8;  // Focused
    weights.relaxed = 0.3;
    weights.blinkLeft = 0.1;  // Occasional blink
    weights.blinkRight = 0.1;
    weights.blink = 0.1;
    weights.sleeping = 0;
    return weights;
  }

  // Phase 34: EXPANDING STATE - Flow state (focused + achievement)
  if (isExpanding) {
    weights.joy = 0.6;   // Achievement satisfaction
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
    weights.surprise = 0.8;  // Surprised! Got a message
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
    weights.joy = 0.3;  // Slight excitement from potential gains
    weights.angry = 0;
    weights.sad = 0;
    weights.fear = 0;
    weights.surprise = 0.1;
    weights.neutral = 0.5;  // Focused concentration
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
    weights.angry = 0.2;   // Frustration
    weights.sad = 0.3;      // Exhaustion sadness
    weights.fear = 0.1;
    weights.surprise = 0;
    weights.neutral = 0.4;
    weights.relaxed = 0;
    weights.blinkLeft = 0.2;  // Tired eyes
    weights.blinkRight = 0.2;
    weights.blink = 0.2;
    weights.sleeping = 0;
    return weights;
  }

  // Phase 40: DANCING STATE - Music is playing!
  if (isDancing) {
    weights.joy = 0.7;   // Pure joy!
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
      weights.mouthSmileLeft = weights.joy * 0.8;
      weights.mouthSmileRight = weights.joy * 0.8;
      weights.cheekSquintLeft = weights.joy * 0.3;
      weights.cheekSquintRight = weights.joy * 0.3;
      weights.neutral = 0;
    }
  }

  // === ANGER ===
  // Conditions: Very high stress (> 80)
  if (stress > config.stressHighThreshold) {
    weights.angry = Math.min(1, (stress - config.stressHighThreshold) / 20);
    weights.browDown = weights.angry * 0.8;
    weights.noseSneer = weights.angry * 0.5;
    weights.mouthGrimace = weights.angry * 0.4;
    weights.neutral = 0;
  }

  // === SAD / GRIEF ===
  // Conditions: High stress + low energy
  if (stress > 60 && energy < 40) {
    const sadnessIntensity = Math.min(1, (stress - 40) / 60 * (40 - energy) / 40);
    weights.sad = Math.max(weights.sad, sadnessIntensity);
    weights.browOuterUp = weights.sad * 0.6;
    weights.mouthFrownLeft = weights.sad * 0.5;
    weights.mouthFrownRight = weights.sad * 0.5;
    weights.neutral = 0;
  }

  // === TIRED / EXHAUSTED ===
  // Conditions: Low energy (< 20)
  if (energy < config.energyLowThreshold) {
    const tiredness = 1 - (energy / config.energyLowThreshold);
    weights.sad = Math.max(weights.sad, tiredness * 0.5);
    weights.blink = tiredness * 0.3; // Partially closed eyes
    weights.eyeSquint = tiredness * 0.4;
    weights.cheekSuck = tiredness * 0.3;
    weights.neutral = 0;
  }

  // === SURPRISE ===
  // Conditions: Sudden need drop (thirst or hunger very low)
  if (thirst < 10 || hunger < 10) {
    weights.surprise = Math.min(1, Math.max(weights.surprise, 0.5));
    weights.eyeWiden = weights.surprise * 0.7;
    weights.browUp = weights.surprise * 0.6;
    weights.mouthOpen = weights.surprise * 0.4;
    weights.jawOpen = weights.surprise * 0.3;
    weights.neutral = 0;
  }

  // === FEAR / WORRY ===
  // Conditions: Very low hygiene + high stress
  if (hygiene < config.hygieneLowThreshold && stress > 40) {
    weights.fear = Math.min(1, (config.hygieneLowThreshold - hygiene) / 50 * stress / 100);
    weights.browUp = Math.max(weights.browUp, weights.fear * 0.5);
    weights.eyeWiden = weights.fear * 0.4;
    weights.mouthOpen = weights.fear * 0.3;
    weights.neutral = 0;
  }

  // === DISGUST (new) ===
  // Conditions: Very low hygiene + moderate stress
  if (hygiene < 20 && stress > 30) {
    weights.disgusted = Math.min(1, (20 - hygiene) / 20 * stress / 100);
    weights.noseSneer = Math.max(weights.noseSneer, weights.disgusted * 0.7);
    weights.noseWrinkle = weights.disgusted * 0.5;
    weights.mouthFunnel = weights.disgusted * 0.3;
    weights.browDown = Math.max(weights.browDown, weights.disgusted * 0.4);
    weights.neutral = 0;
  }

  // === BLUSH / EXCITED (if eros active) ===
  if (arousal > config.arousalHighThreshold) {
    const blushIntensity = (arousal - config.arousalHighThreshold) / 40;
    weights.cheekSquintLeft = Math.max(weights.cheekSquintLeft, blushIntensity * 0.5);
    weights.cheekSquintRight = Math.max(weights.cheekSquintRight, blushIntensity * 0.5);
    weights.eyeWiden = Math.max(weights.eyeWiden, blushIntensity * 0.3);
  }

  // === BREATHING (idle animation) ===
  // Subtle breathing when awake
  if (!isDreaming && energy > 20) {
    weights.breathing = 0.1;
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
export function lerpBlendShapes(from: BlendShapeWeights, to: BlendShapeWeights, t: number): BlendShapeWeights {
  // Clamp t to 0-1
  t = Math.max(0, Math.min(1, t));

  const result = { ...to };

  for (const key of Object.keys(from) as (keyof BlendShapeWeights)[]) {
    result[key] = from[key] + (to[key] - from[key]) * t;
  }

  return result;
}

/**
 * Update avatar expression in the dashboard
 * This sends the blend shape weights to the frontend via the state file
 */
export async function updateAvatarExpression(
  workspacePath: string,
  blendShapes: BlendShapeWeights
): Promise<void> {
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
async function notifyDashboardHttp(blendShapes: BlendShapeWeights): Promise<void> {
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
  } catch {
    // Module not available or other error
  }
}

/**
 * Main function to map physique needs to avatar expressions
 * Call this from the tick handler in index.ts
 */
export async function syncAvatarExpressions(
  workspacePath: string,
  physique: Physique,
  isDreaming: boolean = false,
  isResearching: boolean = false,
  isExpanding: boolean = false,
  hasSocialEvent: boolean = false,
  isTrading: boolean = false,
  isStrained: boolean = false,
  isDancing: boolean = false
): Promise<BlendShapeWeights> {
  // Calculate blend shapes from needs (pass isDreaming/isResearching/isExpanding/hasSocialEvent/isTrading/isStrained/isDancing for special states)
  const blendShapes = mapNeedsToBlendShapes(physique.needs, DEFAULT_CONFIG, isDreaming, isResearching, isExpanding, hasSocialEvent, isTrading, isStrained, isDancing);

  // Update avatar in dashboard
  await updateAvatarExpression(workspacePath, blendShapes);

  return blendShapes;
}
