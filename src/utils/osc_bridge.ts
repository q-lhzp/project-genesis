// ---------------------------------------------------------------------------
// OSC/VMC Bridge - Stream avatar data to external 3D applications
// Phase 32: External Presence & VMC/OSC Integration
// ---------------------------------------------------------------------------

import dgram from "node:dgram";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

/**
 * VMC/OSC Configuration
 */
interface VmcConfig {
  enabled: boolean;
  targetIp: string;
  targetPort: number;
}

const DEFAULT_CONFIG: VmcConfig = {
  enabled: false,
  targetIp: "127.0.0.1",
  targetPort: 39539
};

let currentConfig: VmcConfig = { ...DEFAULT_CONFIG };
let udpSocket: dgram.Socket | null = null;
let isInitialized = false;

/**
 * Initialize UDP socket for OSC
 */
export function initOSCBridge(): boolean {
  if (isInitialized) return true;

  try {
    udpSocket = dgram.createSocket("udp4");
    udpSocket.bind(() => {
      console.log("[osc_bridge] UDP socket initialized");
    });
    isInitialized = true;
    return true;
  } catch (error) {
    console.log("[osc_bridge] Failed to initialize: " + error);
    return false;
  }
}

/**
 * Load configuration from file
 */
export async function loadOSCConfig(workspacePath: string): Promise<VmcConfig> {
  const configPath = join(workspacePath, "memory", "reality", "osc_config.json");

  try {
    if (existsSync(configPath)) {
      const data = readFileSync(configPath, "utf-8");
      const config = JSON.parse(data);
      currentConfig = { ...DEFAULT_CONFIG, ...config };
    }
  } catch (error) {
    console.log("[osc_bridge] Failed to load config: " + error);
  }

  return currentConfig;
}

/**
 * Save configuration to file
 */
export async function saveOSCConfig(workspacePath: string, config: Partial<VmcConfig>): Promise<void> {
  const configPath = join(workspacePath, "memory", "reality", "osc_config.json");

  currentConfig = { ...currentConfig, ...config };

  try {
    writeFileSync(configPath, JSON.stringify(currentConfig, null, 2));
    console.log("[osc_bridge] Configuration saved");
  } catch (error) {
    console.log("[osc_bridge] Failed to save config: " + error);
  }
}

/**
 * Enable/disable streaming
 */
export function setStreamingEnabled(enabled: boolean): void {
  currentConfig.enabled = enabled;

  if (enabled && !isInitialized) {
    initOSCBridge();
  }
}

/**
 * Convert number to OSC float bytes
 */
function floatToBytes(value: number): Buffer {
  const buffer = Buffer.alloc(4);
  buffer.writeFloatBE(value);
  return buffer;
}

/**
 * Convert string to OSC string bytes (null-terminated, padded to 4 bytes)
 */
function stringToBytes(str: string): Buffer {
  let bytes = Buffer.from(str + "\0");
  // Pad to 4 bytes
  while (bytes.length % 4 !== 0) {
    bytes = Buffer.concat([bytes, Buffer.from([0])]);
  }
  return bytes;
}

/**
 * Build OSC address pattern
 */
function buildOSCAddress(address: string): Buffer {
  return stringToBytes(address);
}

/**
 * Send OSC message via UDP
 */
function sendOSCMessage(address: string, args: Buffer[]): void {
  if (!currentConfig.enabled || !udpSocket) return;

  try {
    // OSC message format: [address, types, ...args]
    const addressBytes = buildOSCAddress(address);
    const typeBytes = Buffer.from(",");

    // Combine all parts
    const message = Buffer.concat([addressBytes, typeBytes, ...args]);

    udpSocket.send(message, currentConfig.targetPort, currentConfig.targetIp, (err) => {
      if (err) {
        console.log("[osc_bridge] Send error: " + err);
      }
    });
  } catch (error) {
    console.log("[osc_bridge] Message build error: " + error);
  }
}

/**
 * Send blend shape value (VMC protocol)
 * Format: /vmc/ext/blend/val name value
 */
export function sendBlendShape(name: string, value: number): void {
  if (!currentConfig.enabled) return;

  // Clamp value 0-1
  value = Math.max(0, Math.min(1, value));

  const address = "/vmc/ext/blend/val";
  const nameBytes = stringToBytes(name);
  const valueBytes = floatToBytes(value);

  sendOSCMessage(address, [nameBytes, valueBytes]);
}

/**
 * Send all blend shapes at once
 */
export function sendBlendShapes(blendShapes: Record<string, number>): void {
  if (!currentConfig.enabled) return;

  for (const [name, value] of Object.entries(blendShapes)) {
    sendBlendShape(name, value);
  }
}

/**
 * Send bone position (VMC protocol)
 */
export function sendBonePosition(name: string, x: number, y: number, z: number): void {
  if (!currentConfig.enabled) return;

  const address = "/vmc/ext/bone/pos";
  const nameBytes = stringToBytes(name);
  const xBytes = floatToBytes(x);
  const yBytes = floatToBytes(y);
  const zBytes = floatToBytes(z);

  sendOSCMessage(address, [nameBytes, xBytes, yBytes, zBytes]);
}

/**
 * Send bone rotation (VMC protocol)
 */
export function sendBoneRotation(name: string, x: number, y: number, z: number, w: number): void {
  if (!currentConfig.enabled) return;

  const address = "/vmc/ext/bone/rot";
  const nameBytes = stringToBytes(name);
  const xBytes = floatToBytes(x);
  const yBytes = floatToBytes(y);
  const zBytes = floatToBytes(z);
  const wBytes = floatToBytes(w);

  sendOSCMessage(address, [nameBytes, xBytes, yBytes, zBytes, wBytes]);
}

/**
 * Send lip-sync values (VMC protocol)
 */
export function sendLipSync(vowel: string, value: number): void {
  if (!currentConfig.enabled) return;

  const address = "/vmc/ext/lip/val";
  const vowelBytes = stringToBytes(vowel);
  const valueBytes = floatToBytes(value);

  sendOSCMessage(address, [vowelBytes, valueBytes]);
}

/**
 * Send all lip-sync values at once
 */
export function sendLipSyncAll(vowels: { a: number; i: number; u: number; e: number; o: number }): void {
  if (!currentConfig.enabled) return;

  sendLipSync("A", vowels.a);
  sendLipSync("I", vowels.i);
  sendLipSync("U", vowels.u);
  sendLipSync("E", vowels.e);
  sendLipSync("O", vowels.o);
}

/**
 * Close OSC bridge
 */
export function closeOSCBridge(): void {
  if (udpSocket) {
    udpSocket.close();
    udpSocket = null;
    isInitialized = false;
    console.log("[osc_bridge] UDP socket closed");
  }
}

/**
 * Get current configuration
 */
export function getOSCConfig(): VmcConfig {
  return { ...currentConfig };
}

/**
 * Check if streaming is enabled
 */
export function isStreamingEnabled(): boolean {
  return currentConfig.enabled;
}
