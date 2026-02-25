import type { OpenClawPluginApi } from "../types/index.js";
import type { SimulationPaths, ToolModules } from "../types/paths.js";
import type { PluginConfig } from "../types/config.js";
export declare function registerBeforePromptHook(api: OpenClawPluginApi, paths: SimulationPaths, cfg: Partial<PluginConfig> | undefined, modules: ToolModules, rates: any, reflexThreshold: number, ws: string, lang: "de" | "en"): void;
//# sourceMappingURL=before-prompt.d.ts.map