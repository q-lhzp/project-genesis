// ---------------------------------------------------------------------------
// Identity Tools - Extracted from index.ts
// ---------------------------------------------------------------------------

import { Type } from "@sinclair/typebox";
import { readJson, writeJson } from "../utils/persistence.js";
import { execFilePromise } from "../utils/bridge-executor.js";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { promises as fs, existsSync } from "node:fs";
import type { Physique } from "../types/index.js";
import type { SimulationPaths } from "../types/paths.js";
import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { bootstrapCharacter, activateSlot, deleteSlot, getSlots, getGenesisState } from "../simulation/genesis_engine.js";

export function registerIdentityTools(api: OpenClawPluginApi, paths: SimulationPaths, workspacePath: string): void {
  // Tool: reality_profile
  api.registerTool({
    name: "reality_profile",
    description: "View your current profile (physique, needs, location).",
    parameters: Type.Object({}),
    async execute(_id: string) {
      const ph = await readJson<Physique>(paths.physique);
      if (!ph) return { content: [{ type: "text", text: "physique.json not found." }] };

      const lines = [
        "## Your Profile",
        `- Location: ${ph.current_location}`,
        `- Outfit: ${ph.current_outfit.join(", ") || "none"}`,
        "",
        "### Needs",
        `- Energy: ${ph.needs.energy}/100`,
        `- Hunger: ${ph.needs.hunger}/100`,
        `- Thirst: ${ph.needs.thirst}/100`,
        `- Hygiene: ${ph.needs.hygiene}/100`,
        `- Stress: ${ph.needs.stress}/100`,
      ];

      return { content: [{ type: "text", text: lines.join("\n") }] };
    },
  });

  // Tool: reality_avatar (Phase 22 - 3D VRM Avatar Control)
  api.registerTool({
    name: "reality_avatar",
    description: "Control your 3D avatar (expressions, poses, clothing sync).",
    parameters: Type.Object({
      action: Type.String({ enum: ["pose", "emote", "calibrate", "sync_wardrobe"], description: "Action to perform on the avatar" }),
      value: Type.Optional(Type.String({ description: "Value for the action (e.g., emote name or pose ID)" })),
    }),
    async execute(_id: string, params: { action: string; value?: string }) {
      const action = params.action;
      const value = params.value || "idle";

      api.logger.info(`[genesis] Avatar action requested: ${action} (${value})`);

      // Build avatar state
      const avatarState = {
        action: action,
        value: value,
        timestamp: new Date().toISOString()
      };

      // Write to avatar state file for soul-viz.py to pick up
      const avatarStatePath = join(workspacePath, "memory", "reality", "avatar_state.json");
      await writeJson(avatarStatePath, avatarState);

      // Try to notify the dashboard via HTTP (optional - won't fail if dashboard is not running)
      try {
        const http = await import("node:http");
        const postData = JSON.stringify(avatarState);

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

        const req = http.request(options, (res) => {
          if (res.statusCode === 200) {
            api.logger.info("[genesis] Dashboard notified of avatar update");
          }
        });
        req.on("error", () => {
          // Ignore HTTP errors - dashboard may not be running
        });
        req.write(postData);
        req.end();
      } catch {
        // Ignore HTTP errors - module may not be available or dashboard not running
      }

      // Handle different actions
      let message = "";
      switch (action) {
        case "pose":
          message = `Avatar pose changed to '${value}'. Your 3D avatar is now in ${value} position.`;
          break;
        case "emote":
          message = `Avatar expression set to '${value}'. Your 3D avatar is now showing ${value} emotion.`;
          break;
        case "sync_wardrobe":
          message = `Wardrobe synced with 3D avatar. Current outfit from physique.json applied to VRM model.`;
          break;
        case "calibrate":
          message = `Avatar calibrated and reset to idle pose.`;
          break;
        default:
          message = `Avatar action '${action}' processed.`;
      }

      return { content: [{ type: "text", text: message }] };
    },
  });

  // Tool: reality_camera
  api.registerTool({
    name: "reality_camera",
    description: "Take a photo using the webcam.",
    parameters: Type.Object({
      prompt: Type.Optional(Type.String({ description: "Prompt for neural photography" })),
    }),
    async execute(_id: string, params: { prompt?: string }) {
      // Neural photography - uses vision bridge
      const visionBridge = join(workspacePath, "tools", "vision", "camera_bridge.py");

      try {
        const { stdout } = await execFilePromise("python3", [visionBridge, params.prompt || "self portrait"], { timeout: 60000 });
        return { content: [{ type: "text", text: stdout }] };
      } catch (error) {
        return { content: [{ type: "text", text: "Camera error: " + String(error) }] };
      }
    },
  });

  // Tool: reality_vision_analyze
  api.registerTool({
    name: "reality_vision_analyze",
    description: "Analyze an image using Face-ID and AI.",
    parameters: Type.Object({
      action: Type.String({ description: "Action: analyze | generate" }),
      image_path: Type.Optional(Type.String({ description: "Path to image" })),
      prompt: Type.Optional(Type.String({ description: "Generation prompt" })),
    }),
    async execute(_id: string, params: { action: string; image_path?: string; prompt?: string }) {
      const analyzeScript = join(workspacePath, "tools", "vision", "face_analysis.py");

      if (params.action === "analyze" && params.image_path) {
        try {
          const { stdout } = await execFilePromise("python3", [analyzeScript, "analyze", "--image", params.image_path], { timeout: 60000 });
          return { content: [{ type: "text", text: stdout }] };
        } catch (error) {
          return { content: [{ type: "text", text: "Analysis error: " + String(error) }] };
        }
      }

      return { content: [{ type: "text", text: "Use: reality_vision_analyze(action: 'analyze', image_path: '/path/to/image.jpg')" }] };
    },
  });

  // Tool: reality_genesis (Phase 38 - Neural Life Bootstrapping)
  api.registerTool({
    name: "reality_genesis",
    description: "Bootstrap a new character or manage character slots (Genesis Engine).",
    parameters: Type.Object({
      action: Type.String({ enum: ["bootstrap", "activate", "delete", "list"], description: "Action: bootstrap (create new), activate (switch to), delete, or list slots" }),
      name: Type.Optional(Type.String({ description: "Character name for bootstrap/activate/delete" })),
      prompt: Type.Optional(Type.String({ description: "Description for bootstrapping new character" })),
      vrm_path: Type.Optional(Type.String({ description: "Path to VRM model file for this persona" })),
    }),
    async execute(_id: string, params: { action: string; name?: string; prompt?: string; vrm_path?: string }) {
      if (params.action === "bootstrap") {
        if (!params.name || !params.prompt) {
          return { content: [{ type: "text", text: "Bootstrap requires 'name' and 'prompt' parameters. Example: reality_genesis(action: 'bootstrap', name: 'Alex', prompt: 'A creative introvert who loves coding and art')" }] };
        }
        const result = await bootstrapCharacter(workspacePath, params.name, params.prompt);
        return { content: [{ type: "text", text: result.message }] };
      }

      if (params.action === "activate") {
        if (!params.name) {
          return { content: [{ type: "text", text: "Activate requires 'name' parameter. Example: reality_genesis(action: 'activate', name: 'Alex', vrm_path: '/path/to/avatar.vrm')" }] };
        }
        const result = await activateSlot(workspacePath, params.name, params.vrm_path);
        return { content: [{ type: "text", text: result.message }] };
      }

      if (params.action === "delete") {
        if (!params.name) {
          return { content: [{ type: "text", text: "Delete requires 'name' parameter. Example: reality_genesis(action: 'delete', name: 'Alex')" }] };
        }
        const result = await deleteSlot(workspacePath, params.name);
        return { content: [{ type: "text", text: result.message }] };
      }

      if (params.action === "list" || !params.action) {
        const slots = await getSlots(workspacePath);
        const state = await getGenesisState(workspacePath);

        if (slots.length === 0) {
          return { content: [{ type: "text", text: "No character slots exist. Bootstrap a new character with: reality_genesis(action: 'bootstrap', name: 'Name', prompt: 'Description')" }] };
        }

        const lines = ["## Character Slots", ""];
        for (const slot of slots) {
          const active = slot.is_active ? " (ACTIVE)" : "";
          lines.push(`- **${slot.name}**${active}`);
          lines.push(`  - Created: ${slot.created_at}`);
          lines.push(`  - Description: ${slot.description}`);
        }
        lines.push("");
        lines.push("Use: `reality_genesis(action: 'bootstrap', name: 'Name', prompt: 'Description')` to create a new character.");

        return { content: [{ type: "text", text: lines.join("\n") }] };
      }

      return { content: [{ type: "text", text: "Unknown action. Use: bootstrap, activate, delete, or list." }] };
    },
  });

  // Tool: reality_voice (Phase 20 - Voice Synthesis)
  // Triggers Python voice_bridge.py for TTS generation
  api.registerTool({
    name: "reality_voice",
    description: "Generate speech audio using local TTS (Chatterbox-Turbo or edge-tts fallback).",
    parameters: Type.Object({
      text: Type.String({ description: "Text to speak" }),
      emotion: Type.Optional(Type.String({ enum: ["neutral", "happy", "sad", "angry", "excited"], description: "Emotional tone" })),
      duration: Type.Optional(Type.Number({ description: "Maximum duration in seconds (default: 30)" })),
    }),
    async execute(_id: string, params: { text: string; emotion?: string; duration?: number }) {
      const voiceScript = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "skills", "soul-evolution", "tools", "voice", "voice_bridge.py");

      // Check if script exists
      try {
        await fs.access(voiceScript);
      } catch {
        return { content: [{ type: "text", text: `Voice bridge not found at: ${voiceScript}. Please ensure voice tools are installed.` }] };
      }

      const outputDir = join(workspacePath, "memory", "reality", "media", "voice");
      await fs.mkdir(outputDir, { recursive: true });

      const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
      const outputFile = join(outputDir, `voice_${timestamp}.mp3`);

      // Build command
      const args = [
        voiceScript,
        "--text", params.text,
        "--output", outputFile,
      ];

      if (params.emotion) {
        args.push("--emotion", params.emotion);
      }
      if (params.duration) {
        args.push("--duration", params.duration.toString());
      }

      try {
        const { execFile } = await import("node:child_process");
        const result = await new Promise<{ stdout: string; stderr: string }>((resolve, reject) => {
          execFile("python3", args, { timeout: 60000 }, (error, stdout, stderr) => {
            if (error) reject({ stdout, stderr });
            else resolve({ stdout, stderr });
          });
        });

        if (existsSync(outputFile)) {
          return {
            content: [{
              type: "text",
              text: `✅ Voice generated: ${outputFile}\n\nText: "${params.text}"\nEmotion: ${params.emotion || "neutral"}`
            }]
          };
        } else {
          return { content: [{ type: "text", text: `Voice generation may have failed. Check logs.` }] };
        }
      } catch (err: any) {
        return { content: [{ type: "text", text: `Voice generation failed: ${err.stderr || err.message}` }] };
      }
    },
  });
}
