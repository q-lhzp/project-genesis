// ---------------------------------------------------------------------------
// System Tools - Extracted from index.ts
// ---------------------------------------------------------------------------

import { Type } from "@sinclair/typebox";
import { execFilePromise } from "../utils/bridge-executor.js";
import { join } from "node:path";

interface ToolApi {
  registerTool: (tool: unknown) => void;
}

export function registerSystemTools(api: ToolApi, workspacePath: string): void {
  // Tool: reality_browse
  api.registerTool({
    name: "reality_browse",
    description: "Browse the web using the visual browser.",
    parameters: Type.Object({
      action: Type.String({ description: "Action: browse | click | type | screenshot" }),
      query: Type.Optional(Type.String({ description: "URL or search query" })),
      text: Type.Optional(Type.String({ description: "Text to type" })),
      selector: Type.Optional(Type.String({ description: "CSS selector to click" })),
    }),
    async execute(_id: string, params: { action: string; query?: string; text?: string; selector?: string }) {
      const browserScript = join(workspacePath, "skills", "soul-evolution", "tools", "browser_bridge.py");

      try {
        const { stdout } = await execFilePromise("python3", [browserScript, params.action, params.query || "", params.text || "", params.selector || ""], { timeout: 60000 });
        return { content: [{ type: "text", text: stdout }] };
      } catch (error) {
        return { content: [{ type: "text", text: "Browser error: " + String(error) }] };
      }
    },
  });

  // Tool: reality_desktop
  api.registerTool({
    name: "reality_desktop",
    description: "Control the desktop: key presses, mouse, screenshots.",
    parameters: Type.Object({
      action: Type.String({ description: "Action: key | mouse | screenshot | apps" }),
      combo: Type.Optional(Type.String({ description: "Key combination (e.g., ctrl+c)" })),
      x: Type.Optional(Type.Number({ description: "X coordinate" })),
      y: Type.Optional(Type.Number({ description: "Y coordinate" })),
      button: Type.Optional(Type.String({ description: "Mouse button" })),
    }),
    async execute(_id: string, params: { action: string; combo?: string; x?: number; y?: number; button?: string }) {
      const desktopBridge = join(workspacePath, "skills", "soul-evolution", "tools", "desktop_bridge.py");

      try {
        const { stdout } = await execFilePromise("python3", [
          desktopBridge,
          params.action,
          JSON.stringify({ combo: params.combo, x: params.x, y: params.y, button: params.button })
        ], { timeout: 30000 });
        return { content: [{ type: "text", text: stdout }] };
      } catch (error) {
        return { content: [{ type: "text", text: "Desktop error: " + String(error) }] };
      }
    },
  });
}
