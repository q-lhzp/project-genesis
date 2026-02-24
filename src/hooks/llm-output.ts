// ---------------------------------------------------------------------------
// LLM Output Hook - Phase 6-21
// ---------------------------------------------------------------------------

import { join } from "node:path";
import { readJson, writeJson, appendJsonl } from "../utils/persistence.js";
import type { 
  OpenClawPluginApi, 
  Physique, 
  SocialEvent,
  ExperienceEntry,
  LlmOutputEvent
} from "../types/index.js";

export function registerLlmOutputHook(api: OpenClawPluginApi, paths: any, modules: any) {
  api.on("llm_output", async (event: unknown, _ctx: unknown) => {
    const text: string = (event as LlmOutputEvent).lastAssistant ?? "";
    if (!text || text.length < 20) return;

    const ph = await readJson<Physique>(paths.physique);
    const entry: ExperienceEntry = {
      id: "exp_" + Date.now().toString(36),
      timestamp: new Date().toISOString(),
      source: "conversation",
      content: text.length > 500 ? text.slice(0, 500) + "..." : text,
      significance: "routine",
      significance_reason: "",
      reflected: false,
    };
    if (ph) {
      entry.somatic_context = {
        energy: ph.needs.energy,
        hunger: ph.needs.hunger,
        stress: ph.needs.stress,
        arousal: modules.eros ? ph.needs.arousal : undefined,
        libido: modules.eros ? (ph.needs.libido ?? 0) : undefined,
      };
    }

    const todayStr = new Date().toISOString().slice(0, 10);
    const expPath = join(paths.experiences, `${todayStr}.jsonl`);
    await appendJsonl(expPath, entry);

    // Phase 12: Mark social events as processed
    const socialEvents = await readJson<{ pending: SocialEvent[] }>(paths.socialEvents);
    if (socialEvents && socialEvents.pending.some(e => !e.processed)) {
      socialEvents.pending.forEach(e => e.processed = true);
      await writeJson(paths.socialEvents, socialEvents);
    }
  });
}
