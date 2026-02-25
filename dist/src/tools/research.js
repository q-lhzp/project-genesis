// Research & Intervention Tools - Life Editor, Event Injection, Telemetry Export
// Ported from v3.x for v5.2.0
import { Type } from "@sinclair/typebox";
import { join } from "node:path";
import { promises as fs } from "node:fs";
import { readJson, writeJson, todayStr } from "../utils/persistence.js";
export function registerResearchTools(api, paths, workspacePath) {
    // Tool: reality_override - Manual Intervention (Life Editor)
    api.registerTool({
        name: "reality_override",
        description: "Manually override any simulation state (Life Editor - use with caution)",
        parameters: Type.Object({
            target: Type.String({ enum: ["physique", "location", "needs", "economy", "lifecycle", "all"], description: "What to override" }),
            field: Type.Optional(Type.String({ description: "Specific field to change (e.g., 'energy', 'balance')" })),
            value: Type.Optional(Type.Unknown({ description: "New value" })),
            reset: Type.Optional(Type.Boolean({ description: "Reset to default values" })),
        }),
        async execute(_id, params) {
            try {
                const physiquePath = join(workspacePath, "memory", "reality", "physique.json");
                if (params.reset) {
                    if (params.target === "needs") {
                        const physique = await readJson(physiquePath);
                        if (physique) {
                            physique.needs = {
                                energy: 50,
                                hunger: 30,
                                thirst: 30,
                                bladder: 30,
                                bowel: 20,
                                hygiene: 70,
                                stress: 20,
                                arousal: 30,
                                libido: 30
                            };
                            await writeJson(physiquePath, physique);
                            return { content: [{ type: "text", text: "✅ Needs reset to default values." }] };
                        }
                    }
                    return { content: [{ type: "text", text: "Reset not implemented for this target." }] };
                }
                if (params.target === "physique" && params.field && params.value !== undefined) {
                    const physique = await readJson(physiquePath);
                    if (physique) {
                        const keys = params.field.split(".");
                        let obj = physique;
                        for (let i = 0; i < keys.length - 1; i++) {
                            obj = obj[keys[i]];
                        }
                        obj[keys[keys.length - 1]] = params.value;
                        await writeJson(physiquePath, physique);
                        return { content: [{ type: "text", text: `✅ Set ${params.field} to ${JSON.stringify(params.value)}` }] };
                    }
                }
                if (params.target === "location" && params.value) {
                    const physique = await readJson(physiquePath);
                    if (physique) {
                        physique.current_location = params.value;
                        await writeJson(physiquePath, physique);
                        return { content: [{ type: "text", text: `✅ Location changed to ${params.value}` }] };
                    }
                }
                return { content: [{ type: "text", text: "Override not supported for this target/field combination." }] };
            }
            catch (err) {
                return { content: [{ type: "text", text: `Override failed: ${err.message}` }] };
            }
        },
    });
    // Tool: reality_inject_event - Major Life Event Injection
    api.registerTool({
        name: "reality_inject_event",
        description: "Inject a major life event that affects the simulation",
        parameters: Type.Object({
            type: Type.String({ enum: ["positive", "negative", "neutral"], description: "Event type" }),
            event: Type.String({ description: "Event description" }),
            impact: Type.Optional(Type.Number({ minimum: 1, maximum: 10, description: "Impact level (1-10)" })),
            duration: Type.Optional(Type.Number({ description: "Duration in ticks" })),
        }),
        async execute(_id, params) {
            const impact = params.impact || 5;
            const duration = params.duration || 10;
            const event = {
                id: `EVENT-${Date.now()}`,
                type: params.type,
                event: params.event,
                impact: impact,
                duration: duration,
                ticks_remaining: duration,
                timestamp: new Date().toISOString(),
                active: true,
            };
            const eventsFile = join(workspacePath, "memory", "reality", "active_events.json");
            let events = [];
            try {
                events = await readJson(eventsFile) || [];
            }
            catch { }
            events.push(event);
            await writeJson(eventsFile, events);
            const historyFile = join(workspacePath, "memory", "reality", "event_history.jsonl");
            await fs.appendFile(historyFile, JSON.stringify(event) + "\n", "utf-8");
            const physiquePath = join(workspacePath, "memory", "reality", "physique.json");
            const physique = await readJson(physiquePath);
            if (physique && physique.needs) {
                const stressMod = params.type === "positive" ? -impact : params.type === "negative" ? impact * 1.5 : 0;
                physique.needs.stress = Math.max(0, Math.min(100, (physique.needs.stress || 50) + stressMod));
                await writeJson(physiquePath, physique);
            }
            return {
                content: [{
                        type: "text",
                        text: `✅ Event injected!\n\nType: ${params.type}\nEvent: ${params.event}\nImpact: ${impact}/10\nDuration: ${duration} ticks`
                    }]
            };
        },
    });
    // Tool: reality_export_research_data - Telemetry Export
    api.registerTool({
        name: "reality_export_research_data",
        description: "Export telemetry and research data for analysis",
        parameters: Type.Object({
            format: Type.Optional(Type.String({ enum: ["json", "csv", "markdown"], description: "Export format" })),
            timeframe: Type.Optional(Type.String({ enum: ["today", "week", "month", "all"], description: "Timeframe" })),
            type: Type.Optional(Type.String({ enum: ["vitality", "social", "economy", "all"], description: "Data type" })),
        }),
        async execute(_id, params) {
            const format = params.format || "markdown";
            const type = params.type || "all";
            const output = [];
            const physiquePath = join(workspacePath, "memory", "reality", "physique.json");
            const lifecyclePath = join(workspacePath, "memory", "reality", "lifecycle.json");
            const socialPath = join(workspacePath, "memory", "reality", "social.json");
            const vaultPath = join(workspacePath, "memory", "reality", "vault_state.json");
            if (type === "all" || type === "vitality") {
                try {
                    const physique = await readJson(physiquePath);
                    const lifecycle = await readJson(lifecyclePath);
                    if (format === "markdown") {
                        output.push("## Vitality Data");
                        output.push("");
                        output.push("### Current State");
                        output.push(`- Location: ${physique?.current_location || "unknown"}`);
                        output.push(`- Energy: ${physique?.needs?.energy || 0}/100`);
                        output.push(`- Hunger: ${physique?.needs?.hunger || 0}/100`);
                        output.push(`- Stress: ${physique?.needs?.stress || 0}/100`);
                        output.push("");
                        output.push("### Lifecycle");
                        output.push(`- Age: ${lifecycle?.biological_age_days || 0} days`);
                        output.push(`- Stage: ${lifecycle?.life_stage || "unknown"}`);
                    }
                }
                catch { }
            }
            if (type === "all" || type === "social") {
                try {
                    const social = await readJson(socialPath);
                    if (format === "markdown") {
                        output.push("");
                        output.push("## Social Data");
                        output.push("");
                        output.push(`Total Contacts: ${social?.entities?.length || 0}`);
                    }
                }
                catch { }
            }
            if (type === "all" || type === "economy") {
                try {
                    const vault = await readJson(vaultPath);
                    if (format === "markdown") {
                        output.push("");
                        output.push("## Economy Data");
                        output.push("");
                        output.push(`Balance: $${vault?.portfolio?.balance || 0}`);
                        output.push(`Total Value: $${vault?.portfolio?.total_value || 0}`);
                    }
                }
                catch { }
            }
            const ext = format === "csv" ? "csv" : format === "json" ? "json" : "md";
            const exportDir = join(workspacePath, "memory", "exports");
            await fs.mkdir(exportDir, { recursive: true });
            const exportFile = join(exportDir, `export_${type}_${todayStr()}.${ext}`);
            await fs.writeFile(exportFile, output.join("\n"), "utf-8");
            return {
                content: [{
                        type: "text",
                        text: `✅ Data exported!\n\nFile: ${exportFile}\nFormat: ${format}\nType: ${type}`
                    }]
            };
        },
    });
    api.logger.info("[research-tools] Registered: override, inject_event, export_research_data");
}
//# sourceMappingURL=research.js.map