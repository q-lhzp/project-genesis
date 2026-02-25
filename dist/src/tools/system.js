// ---------------------------------------------------------------------------
// System Tools - Extracted from index.ts
// ---------------------------------------------------------------------------
import { Type } from "@sinclair/typebox";
import { execFilePromise } from "../utils/bridge-executor.js";
import { join } from "node:path";
import { setDesktopState } from "../simulation/desktop_mapper.js";
import { forceStopSpatial, getSpatialState } from "../simulation/spatial_engine.js";
export function registerSystemTools(api, workspacePath) {
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
        async execute(_id, params) {
            const browserScript = join(workspacePath, "skills", "soul-evolution", "tools", "browser_bridge.py");
            try {
                const { stdout } = await execFilePromise("python3", [browserScript, params.action, params.query || "", params.text || "", params.selector || ""], { timeout: 60000 });
                return { content: [{ type: "text", text: stdout }] };
            }
            catch (error) {
                return { content: [{ type: "text", text: "Browser error: " + String(error) }] };
            }
        },
    });
    // Tool: reality_desktop
    api.registerTool({
        name: "reality_desktop",
        description: "Control the desktop: key presses, mouse, screenshots, wallpaper, theme, automation.",
        parameters: Type.Object({
            action: Type.String({ description: "Action: key | mouse | screenshot | apps | wallpaper | theme | automation | stop" }),
            combo: Type.Optional(Type.String({ description: "Key combination (e.g., ctrl+c)" })),
            x: Type.Optional(Type.Number({ description: "X coordinate" })),
            y: Type.Optional(Type.Number({ description: "Y coordinate" })),
            button: Type.Optional(Type.String({ description: "Mouse button" })),
            value: Type.Optional(Type.String({ description: "Value for wallpaper (location key) or theme (light/dark)" })),
        }),
        async execute(_id, params) {
            // Phase 26: Handle wallpaper and theme actions directly
            if (params.action === "wallpaper" || params.action === "theme") {
                const result = await setDesktopState(workspacePath, params.action, params.value || "");
                return {
                    content: [{ type: "text", text: result.message }]
                };
            }
            // Phase 36: Handle automation control
            if (params.action === "automation" || params.action === "stop") {
                if (params.action === "stop") {
                    await forceStopSpatial(workspacePath);
                    return { content: [{ type: "text", text: "Desktop automation stopped." }] };
                }
                // Get automation status
                const state = await getSpatialState(workspacePath);
                return {
                    content: [{
                            type: "text",
                            text: `Automation: ${state.isActive ? "Active" : "Inactive"} | Mode: ${state.currentMode} | Keys: ${state.keyStrokesCount} | Moves: ${state.mouseMovesCount}`
                        }]
                };
            }
            // Original desktop bridge actions
            const desktopBridge = join(workspacePath, "skills", "soul-evolution", "tools", "desktop_bridge.py");
            try {
                const { stdout } = await execFilePromise("python3", [
                    desktopBridge,
                    params.action,
                    JSON.stringify({ combo: params.combo, x: params.x, y: params.y, button: params.button })
                ], { timeout: 30000 });
                return { content: [{ type: "text", text: stdout }] };
            }
            catch (error) {
                return { content: [{ type: "text", text: "Desktop error: " + String(error) }] };
            }
        },
    });
}
//# sourceMappingURL=system.js.map