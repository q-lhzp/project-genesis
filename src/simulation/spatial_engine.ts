// ---------------------------------------------------------------------------
// Spatial Engine - VRM-to-Desktop Input Bridge
// Phase 36: Spatial Sovereignty (VRM-to-Desktop Input)
// ---------------------------------------------------------------------------

import { readJson, writeJson } from "../utils/persistence.js";
import { join } from "node:path";
import { existsSync } from "node:fs";
import { exec } from "node:child_process";
import type { Physique } from "../types/index.js";

/**
 * Spatial interaction configuration
 */
interface SpatialConfig {
  mouseMoveEnabled: boolean;       // Enable ghost mouse movements
  keyStrokeEnabled: boolean;         // Enable ghost keystrokes
  scrollEnabled: boolean;           // Enable scrolling during research
  sovereigntyOverride: boolean;    // Stop on reflex lock
  mouseMoveInterval: number;       // ms between movements
  keyStrokeProbability: number;    // 0-1 chance per tick
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

const DEFAULT_CONFIG: SpatialConfig = {
  mouseMoveEnabled: true,
  keyStrokeEnabled: true,
  scrollEnabled: true,
  sovereigntyOverride: true,
  mouseMoveInterval: 5000,
  keyStrokeProbability: 0.3,
};

const DEFAULT_STATE: SpatialState = {
  isActive: false,
  currentMode: "idle",
  lastInputTime: null,
  mouseMovesCount: 0,
  keyStrokesCount: 0,
  scrollCount: 0,
};

/**
 * Load spatial engine state
 */
async function loadSpatialState(workspacePath: string): Promise<SpatialState> {
  const statePath = join(workspacePath, "memory", "reality", "spatial_state.json");
  try {
    if (existsSync(statePath)) {
      return await readJson(statePath) || DEFAULT_STATE;
    }
  } catch (error) {
    console.log(`[spatial_engine] Failed to load state: ${error}`);
  }
  return DEFAULT_STATE;
}

/**
 * Save spatial engine state
 */
async function saveSpatialState(workspacePath: string, state: SpatialState): Promise<void> {
  const statePath = join(workspacePath, "memory", "reality", "spatial_state.json");
  await writeJson(statePath, state);
}

/**
 * Perform mouse movement via desktop bridge
 */
async function performMouseMove(workspacePath: string, dx: number, dy: number): Promise<void> {
  return new Promise((resolve) => {
    const desktopBridge = join(workspacePath, "skills", "soul-evolution", "tools", "desktop_bridge.py");
    const args = ["move", JSON.stringify({ dx, dy })];

    exec(`python3 ${desktopBridge} ${args.join(" ")}`, (error) => {
      if (error) {
        console.log(`[spatial_engine] Mouse move error: ${error}`);
      }
      resolve();
    });
  });
}

/**
 * Perform key stroke via desktop bridge
 */
async function performKeyStroke(workspacePath: string, key: string): Promise<void> {
  return new Promise((resolve) => {
    const desktopBridge = join(workspacePath, "skills", "soul-evolution", "tools", "desktop_bridge.py");
    const args = ["key", JSON.stringify({ combo: key })];

    exec(`python3 ${desktopBridge} ${args.join(" ")}`, (error) => {
      if (error) {
        console.log(`[spatial_engine] Key stroke error: ${error}`);
      }
      resolve();
    });
  });
}

/**
 * Perform scroll via desktop bridge
 */
async function performScroll(workspacePath: string, direction: "up" | "down"): Promise<void> {
  return new Promise((resolve) => {
    const desktopBridge = join(workspacePath, "skills", "soul-evolution", "tools", "desktop_bridge.py");
    const scrollKey = direction === "up" ? "Up" : "Down";
    const args = ["key", JSON.stringify({ combo: scrollKey })];

    exec(`python3 ${desktopBridge} ${args.join(" ")}`, (error) => {
      if (error) {
        console.log(`[spatial_engine] Scroll error: ${error}`);
      }
      resolve();
    });
  });
}

/**
 * Generate random mouse movement
 */
function generateRandomMovement(): { dx: number; dy: number } {
  // Small random movements to simulate "alive" cursor
  const dx = Math.floor(Math.random() * 20) - 10;
  const dy = Math.floor(Math.random() * 20) - 10;
  return { dx, dy };
}

/**
 * Generate ghost keystrokes for coding
 */
function generateGhostKeystroke(): string {
  const keys = [
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
    "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
    "Return", "Tab", "space"
  ];
  return keys[Math.floor(Math.random() * keys.length)];
}

/**
 * Check if Q is in reflex lock (sovereignty override)
 */
function isInReflexLock(physique: Physique): boolean {
  const needs = physique.needs;
  const reflexThreshold = 95;

  // Check if any critical need is at crisis level
  const stressAtThreshold = (needs.stress ?? 0) >= reflexThreshold;
  const hungerAtThreshold = (needs.hunger ?? 0) >= reflexThreshold;
  const thirstAtThreshold = (needs.thirst ?? 0) >= reflexThreshold;
  const bladderAtThreshold = (needs.bladder ?? 0) >= reflexThreshold;

  return stressAtThreshold || hungerAtThreshold || thirstAtThreshold || bladderAtThreshold;
}

/**
 * Main process function - call from tick handler
 */
export async function processSpatialInteraction(
  workspacePath: string,
  physique: Physique,
  isResearching: boolean,
  isExpanding: boolean,
  config: SpatialConfig = DEFAULT_CONFIG
): Promise<{
  isActive: boolean;
  mode: string;
  triggeredInput: boolean;
}> {
  const now = new Date();
  let state = await loadSpatialState(workspacePath);

  // Phase 36: Sovereignty Override - Stop all input if in reflex lock
  if (config.sovereigntyOverride && isInReflexLock(physique)) {
    if (state.isActive && state.currentMode !== "sovereignty_override") {
      state.currentMode = "sovereignty_override";
      state.isActive = false;
      await saveSpatialState(workspacePath, state);
      console.log("[spatial_engine] Sovereignty override triggered - stopping inputs");
    }
    return { isActive: false, mode: "sovereignty_override", triggeredInput: false };
  }

  // Determine current mode
  let currentMode: SpatialState["currentMode"] = "idle";
  let shouldBeActive = false;

  if (isExpanding) {
    currentMode = "coding";
    shouldBeActive = config.keyStrokeEnabled;
  } else if (isResearching) {
    currentMode = "researching";
    shouldBeActive = config.scrollEnabled || config.mouseMoveEnabled;
  }

  // If not active but should be
  if (shouldBeActive && !state.isActive) {
    state.isActive = true;
    state.currentMode = currentMode;
    console.log(`[spatial_engine] Started: ${currentMode}`);
  } else if (!shouldBeActive && state.isActive) {
    state.isActive = false;
    state.currentMode = "idle";
    console.log("[spatial_engine] Stopped");
  }

  await saveSpatialState(workspacePath, state);

  // If not active, return early
  if (!state.isActive) {
    return { isActive: false, mode: state.currentMode, triggeredInput: false };
  }

  // Process inputs based on mode
  let triggeredInput = false;

  if (currentMode === "coding" && config.keyStrokeEnabled) {
    // Ghost typing for coding
    if (Math.random() < config.keyStrokeProbability) {
      const key = generateGhostKeystroke();
      await performKeyStroke(workspacePath, key);
      state.keyStrokesCount++;
      triggeredInput = true;
    }
  } else if (currentMode === "researching") {
    // Mouse movement during research/browsing
    if (config.mouseMoveEnabled && Math.random() < 0.2) {
      const { dx, dy } = generateRandomMovement();
      await performMouseMove(workspacePath, dx, dy);
      state.mouseMovesCount++;
      triggeredInput = true;
    }

    // Occasional scrolling
    if (config.scrollEnabled && Math.random() < 0.1) {
      const direction = Math.random() < 0.5 ? "up" : "down";
      await performScroll(workspacePath, direction);
      state.scrollCount++;
      triggeredInput = true;
    }
  }

  // Update state
  state.lastInputTime = now.toISOString();
  await saveSpatialState(workspacePath, state);

  return {
    isActive: state.isActive,
    mode: currentMode,
    triggeredInput,
  };
}

/**
 * Get current spatial state for UI
 */
export async function getSpatialState(workspacePath: string): Promise<SpatialState> {
  return loadSpatialState(workspacePath);
}

/**
 * Force stop spatial interaction (emergency override)
 */
export async function forceStopSpatial(workspacePath: string): Promise<void> {
  const state = await loadSpatialState(workspacePath);
  state.isActive = false;
  state.currentMode = "idle";
  await saveSpatialState(workspacePath, state);
  console.log("[spatial_engine] Force stopped by user");
}

/**
 * Get head tracking target position for 3D avatar
 */
export function getHeadTrackingTarget(screenX: number, screenY: number): { x: number; y: number; z: number } {
  // Convert screen coordinates to 3D look-at target
  // Normalize to -1 to 1 range
  const normalizedX = (screenX / 1920) * 2 - 1;
  const normalizedY = -((screenY / 1080) * 2 - 1);

  return {
    x: normalizedX * 0.5,
    y: normalizedY * 0.3 + 0.1,
    z: -2.0, // Looking forward
  };
}
