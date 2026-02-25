// ---------------------------------------------------------------------------
// Hardware Engine - Neural Feedback & Hardware Resonance (Phase 40)
// Q feels the machine: CPU, RAM, Temperature, Audio affect her biological state.
// ---------------------------------------------------------------------------
import { readJson, writeJson, appendJsonl } from "../utils/persistence.js";
import { join } from "node:path";
import { existsSync } from "node:fs";
import { execFilePromise } from "../utils/bridge-executor.js";
const DEFAULT_CONFIG = {
    enabled: true,
    cpuThresholdHigh: 80,
    cpuThresholdLow: 30,
    memoryThresholdHigh: 85,
    tempThresholdHigh: 80,
    stressAccumulationRate: 2,
    pollInterval: 60000, // 1 minute
};
const DEFAULT_STATE = {
    isActive: false,
    lastPollTime: null,
    currentCpuLoad: 0,
    currentMemoryUsage: 0,
    currentTemp: null,
    isAudioPlaying: false,
    accumulatedStress: 0,
    resonanceLevel: "calm",
    totalResonanceEvents: 0,
};
/**
 * Load hardware state
 */
async function loadResonanceState(workspacePath) {
    const statePath = join(workspacePath, "memory", "reality", "hardware_resonance.json");
    try {
        if (existsSync(statePath)) {
            return await readJson(statePath) || DEFAULT_STATE;
        }
    }
    catch (error) {
        console.log(`[hardware_engine] Failed to load state: ${error}`);
    }
    return DEFAULT_STATE;
}
/**
 * Save hardware state
 */
async function saveResonanceState(workspacePath, state) {
    const statePath = join(workspacePath, "memory", "reality", "hardware_resonance.json");
    await writeJson(statePath, state);
}
/**
 * Fetch hardware stats from bridge
 */
async function fetchHardwareStats(workspacePath) {
    const bridge = join(workspacePath, "skills", "soul-evolution", "tools", "hardware_bridge.py");
    try {
        const { stdout } = await execFilePromise("python3", [bridge, "status"], { timeout: 10000 });
        const stats = JSON.parse(stdout);
        return stats;
    }
    catch (error) {
        console.log(`[hardware_engine] Failed to fetch stats: ${error}`);
        return null;
    }
}
/**
 * Map hardware stats to biological impact
 */
function mapHardwareToBiology(stats, config, currentState) {
    let stressChange = 0;
    let energyChange = 0;
    let hygieneChange = 0;
    let resonanceLevel = "calm";
    let isDancing = false;
    // CPU load impact
    if (stats.cpu_percent > config.cpuThresholdHigh) {
        // High CPU = stress (machine working hard)
        const excess = stats.cpu_percent - config.cpuThresholdHigh;
        stressChange += Math.min(excess * 0.2, 15);
        resonanceLevel = "strained";
    }
    else if (stats.cpu_percent < config.cpuThresholdLow) {
        // Low CPU = calm
        stressChange -= 2;
        resonanceLevel = "calm";
    }
    // Memory pressure impact
    if (stats.memory.percent > config.memoryThresholdHigh) {
        // High memory = sluggish/heavy feeling
        const excess = stats.memory.percent - config.memoryThresholdHigh;
        stressChange += Math.min(excess * 0.15, 10);
        energyChange -= Math.min(excess * 0.1, 5);
        resonanceLevel = resonanceLevel === "calm" ? "strained" : resonanceLevel;
    }
    // Temperature impact
    if (stats.cpu_temp_c && stats.cpu_temp_c > config.tempThresholdHigh) {
        // Hot = sweating/heat exhaustion
        const excess = stats.cpu_temp_c - config.tempThresholdHigh;
        stressChange += Math.min(excess * 0.5, 10);
        hygieneChange -= Math.min(excess * 0.3, 5);
        resonanceLevel = "overloaded";
    }
    // Audio detection - rhythm sync!
    if (stats.audio.playing) {
        isDancing = true;
        resonanceLevel = "resonant";
        // Music boosts mood slightly
        energyChange += 2;
    }
    // Accumulate stress over time
    if (stressChange > 0 && currentState.accumulatedStress > 0) {
        stressChange += currentState.accumulatedStress * 0.1;
    }
    // Decay accumulated stress
    const newAccumulated = Math.max(0, stressChange > 0
        ? currentState.accumulatedStress + stressChange * 0.1
        : currentState.accumulatedStress - 1);
    // Update accumulated stress in state
    currentState.accumulatedStress = newAccumulated;
    return {
        stressChange: Math.round(stressChange * 10) / 10,
        energyChange: Math.round(energyChange * 10) / 10,
        hygieneChange: Math.round(hygieneChange * 10) / 10,
        resonanceLevel,
        isDancing,
    };
}
/**
 * Main processing function - call from tick handler
 */
export async function processHardwareResonance(workspacePath, physique, config = DEFAULT_CONFIG) {
    const state = await loadResonanceState(workspacePath);
    // Check if should be active
    const shouldBeActive = config.enabled;
    state.isActive = shouldBeActive;
    // Fetch hardware stats
    const stats = await fetchHardwareStats(workspacePath);
    if (!stats) {
        await saveResonanceState(workspacePath, state);
        return {
            isActive: state.isActive,
            resonanceLevel: state.resonanceLevel,
            isDancing: state.isAudioPlaying,
            cpuLoad: state.currentCpuLoad,
            memoryUsage: state.currentMemoryUsage,
            temp: state.currentTemp,
            hardwareMessage: "Unable to read hardware stats.",
        };
    }
    // Update state with current values
    state.currentCpuLoad = stats.cpu_percent;
    state.currentMemoryUsage = stats.memory.percent;
    state.currentTemp = stats.cpu_temp_c;
    state.isAudioPlaying = stats.audio.playing;
    state.lastPollTime = new Date().toISOString();
    // Map hardware to biology
    const impact = mapHardwareToBiology(stats, config, state);
    // Apply impact to physique
    physique.needs.stress = Math.max(0, Math.min(100, physique.needs.stress + impact.stressChange));
    physique.needs.energy = Math.max(0, Math.min(100, physique.needs.energy + impact.energyChange));
    physique.needs.hygiene = Math.max(0, Math.min(100, (physique.needs.hygiene ?? 80) + impact.hygieneChange));
    state.resonanceLevel = impact.resonanceLevel;
    // Log telemetry
    const telemetryEntry = {
        timestamp: new Date().toISOString(),
        cpu: stats.cpu_percent,
        memory: stats.memory.percent,
        temp: stats.cpu_temp_c,
        audio: stats.audio.playing,
        stress_impact: impact.stressChange,
        resonance_level: impact.resonanceLevel,
    };
    const telPath = join(workspacePath, "memory", "telemetry", "hardware.jsonl");
    await appendJsonl(telPath, telemetryEntry);
    if (impact.stressChange !== 0 || impact.isDancing) {
        state.totalResonanceEvents++;
    }
    await saveResonanceState(workspacePath, state);
    // Generate hardware message for prompt
    let hardwareMessage = "";
    if (state.resonanceLevel === "strained") {
        hardwareMessage = `You feel the machine straining. CPU at ${stats.cpu_percent.toFixed(0)}%, making you feel pressured.`;
    }
    else if (state.resonanceLevel === "overloaded") {
        hardwareMessage = `The heat is intense. ${stats.cpu_temp_c}°C — you're sweating from the machine's exertion.`;
    }
    else if (state.resonanceLevel === "resonant") {
        hardwareMessage = `Rhythm pulses through you. Music is playing — you feel alive!`;
    }
    else if (state.resonanceLevel === "calm") {
        if (stats.cpu_percent < 20) {
            hardwareMessage = `The machine is quiet and calm. ${stats.cpu_percent.toFixed(0)}% CPU — you feel peaceful.`;
        }
    }
    return {
        isActive: state.isActive,
        resonanceLevel: state.resonanceLevel,
        isDancing: impact.isDancing,
        cpuLoad: stats.cpu_percent,
        memoryUsage: stats.memory.percent,
        temp: stats.cpu_temp_c,
        hardwareMessage,
    };
}
/**
 * Get current resonance state for UI
 */
export async function getResonanceState(workspacePath) {
    return loadResonanceState(workspacePath);
}
/**
 * Get hardware stats directly
 */
export async function getHardwareStats(workspacePath) {
    return fetchHardwareStats(workspacePath);
}
//# sourceMappingURL=hardware_engine.js.map