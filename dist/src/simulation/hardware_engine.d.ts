import type { Physique } from "../types/index.js";
/**
 * Hardware statistics from system
 */
interface HardwareStats {
    timestamp: number;
    cpu_percent: number;
    memory: {
        total_mb: number;
        used_mb: number;
        percent: number;
    };
    cpu_temp_c: number | null;
    uptime: {
        seconds: number;
        hours: number;
        minutes: number;
    };
    audio: {
        playing: boolean;
        sink: string | null;
        mode: string | null;
    };
    load_average: {
        "1min": number;
        "5min": number;
        "15min": number;
    };
}
/**
 * Hardware resonance configuration
 */
interface ResonanceConfig {
    enabled: boolean;
    cpuThresholdHigh: number;
    cpuThresholdLow: number;
    memoryThresholdHigh: number;
    tempThresholdHigh: number;
    stressAccumulationRate: number;
    pollInterval: number;
}
/**
 * Hardware resonance state
 */
interface ResonanceState {
    isActive: boolean;
    lastPollTime: string | null;
    currentCpuLoad: number;
    currentMemoryUsage: number;
    currentTemp: number | null;
    isAudioPlaying: boolean;
    accumulatedStress: number;
    resonanceLevel: "calm" | "strained" | "resonant" | "overloaded";
    totalResonanceEvents: number;
}
/**
 * Main processing function - call from tick handler
 */
export declare function processHardwareResonance(workspacePath: string, physique: Physique, config?: ResonanceConfig): Promise<{
    isActive: boolean;
    resonanceLevel: string;
    isDancing: boolean;
    cpuLoad: number;
    memoryUsage: number;
    temp: number | null;
    hardwareMessage: string;
}>;
/**
 * Get current resonance state for UI
 */
export declare function getResonanceState(workspacePath: string): Promise<ResonanceState>;
/**
 * Get hardware stats directly
 */
export declare function getHardwareStats(workspacePath: string): Promise<HardwareStats | null>;
export {};
//# sourceMappingURL=hardware_engine.d.ts.map