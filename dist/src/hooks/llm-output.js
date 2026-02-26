// ---------------------------------------------------------------------------
// LLM Output Hook - Phase 6-21
// ---------------------------------------------------------------------------
import { join } from "node:path";
import { readJson, writeJson, appendJsonl } from "../utils/persistence.js";
export function registerLlmOutputHook(api, paths, modules) {
    api.on("llm_output", async (event, _ctx) => {
        const text = event.lastAssistant ?? "";
        if (!text || text.length < 20)
            return;
        const ph = await readJson(paths.physique);
        const entry = {
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
        const socialEvents = await readJson(paths.socialEvents);
        if (socialEvents?.pending?.some(e => !e.processed)) {
            socialEvents.pending.forEach(e => e.processed = true);
            await writeJson(paths.socialEvents, socialEvents);
        }
    });
}
//# sourceMappingURL=llm-output.js.map