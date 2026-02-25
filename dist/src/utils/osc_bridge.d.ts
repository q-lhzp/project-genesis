/**
 * VMC/OSC Configuration
 */
interface VmcConfig {
    enabled: boolean;
    targetIp: string;
    targetPort: number;
}
/**
 * Initialize UDP socket for OSC
 */
export declare function initOSCBridge(): boolean;
/**
 * Load configuration from file
 */
export declare function loadOSCConfig(workspacePath: string): Promise<VmcConfig>;
/**
 * Save configuration to file
 */
export declare function saveOSCConfig(workspacePath: string, config: Partial<VmcConfig>): Promise<void>;
/**
 * Enable/disable streaming
 */
export declare function setStreamingEnabled(enabled: boolean): void;
/**
 * Send blend shape value (VMC protocol)
 * Format: /vmc/ext/blend/val name value
 */
export declare function sendBlendShape(name: string, value: number): void;
/**
 * Send all blend shapes at once
 */
export declare function sendBlendShapes(blendShapes: Record<string, number>): void;
/**
 * Send bone position (VMC protocol)
 */
export declare function sendBonePosition(name: string, x: number, y: number, z: number): void;
/**
 * Send bone rotation (VMC protocol)
 */
export declare function sendBoneRotation(name: string, x: number, y: number, z: number, w: number): void;
/**
 * Send lip-sync values (VMC protocol)
 */
export declare function sendLipSync(vowel: string, value: number): void;
/**
 * Send all lip-sync values at once
 */
export declare function sendLipSyncAll(vowels: {
    a: number;
    i: number;
    u: number;
    e: number;
    o: number;
}): void;
/**
 * Close OSC bridge
 */
export declare function closeOSCBridge(): void;
/**
 * Get current configuration
 */
export declare function getOSCConfig(): VmcConfig;
/**
 * Check if streaming is enabled
 */
export declare function isStreamingEnabled(): boolean;
export {};
//# sourceMappingURL=osc_bridge.d.ts.map