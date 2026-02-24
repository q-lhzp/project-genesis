// ---------------------------------------------------------------------------
// Identity Tools - Extracted from index.ts
// ---------------------------------------------------------------------------

import { Type } from "@sinclair/typebox";
import { readJson, writeJson } from "../utils/persistence.js";
import { execFilePromise } from "../utils/bridge-executor.js";
import { join } from "node:path";
import type { Physique } from "../types/index.js";
import type { SimulationPaths } from "../types/paths.js";

interface ToolApi {
  registerTool: (tool: unknown) => void;
}

export function registerIdentityTools(api: ToolApi, paths: SimulationPaths, workspacePath: string): void {
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
}
