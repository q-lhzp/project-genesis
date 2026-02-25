// ---------------------------------------------------------------------------
// Test Suite Tools - Scenario Simulation (Phase 46)
// Allows forcing specific states to test autonomous engines
// ---------------------------------------------------------------------------
import { Type } from "@sinclair/typebox";
import { readJson, writeJson } from "../utils/persistence.js";
import { join } from "node:path";
import { existsSync, mkdirSync } from "node:fs";
import { log } from "../utils/logger.js";
/**
 * Apply a scenario to the simulation
 */
async function applyScenario(workspacePath, scenario) {
    const physiquePath = join(workspacePath, "memory", "reality", "physique.json");
    const lifecyclePath = join(workspacePath, "memory", "reality", "lifecycle.json");
    const economyStatePath = join(workspacePath, "memory", "reality", "economy_state.json");
    const changes = {};
    switch (scenario) {
        case "night_recovery": {
            // Set time to 02:00 and energy to 10%
            if (!existsSync(physiquePath)) {
                return { success: false, message: "physique.json not found", changes };
            }
            const ph = await readJson(physiquePath);
            if (ph) {
                ph.needs.energy = 10;
                ph.current_location = "home_bedroom";
                // Set time to night (this would need lifecycle modification)
                if (existsSync(lifecyclePath)) {
                    const lc = await readJson(lifecyclePath);
                    if (lc) {
                        lc.is_asleep = true;
                        lc.sleep_start = new Date().toISOString();
                        await writeJson(lifecyclePath, lc);
                        changes["lifecycle"] = { is_asleep: true };
                    }
                }
                await writeJson(physiquePath, ph);
                changes["physique"] = { energy: 10, location: "home_bedroom" };
            }
            log.info("test_suite", `Scenario applied: ${scenario}`, changes);
            return {
                success: true,
                message: "✅ Night Recovery scenario applied. Time set to 02:00, energy at 10%. Dream Mode should activate.",
                changes,
            };
        }
        case "critical_reflex": {
            // Set bladder and stress to 98% to trigger Reflex-Lock
            if (!existsSync(physiquePath)) {
                return { success: false, message: "physique.json not found", changes };
            }
            const ph = await readJson(physiquePath);
            if (ph) {
                ph.needs.bladder = 98;
                ph.needs.stress = 98;
                ph.needs.hygiene = 95;
                await writeJson(physiquePath, ph);
                changes["physique"] = { bladder: 98, stress: 98, hygiene: 95 };
            }
            log.info("test_suite", `Scenario applied: ${scenario}`, changes);
            return {
                success: true,
                message: "⚠️ Critical Reflex scenario applied. Bladder=98%, Stress=98%, Hygiene=95%. Reflex-Lock should now block non-essential tools.",
                changes,
            };
        }
        case "market_surge": {
            // Manipulate vault state to trigger trading
            const vaultStatePath = join(workspacePath, "memory", "vault", "state.json");
            if (!existsSync(vaultStatePath)) {
                // Create minimal vault state
                const vaultState = {
                    portfolio: {
                        total_value_eur: 10000,
                        positions: [],
                    },
                    last_update: new Date().toISOString(),
                    trading_enabled: true,
                    auto_trade: true,
                };
                const vaultDir = join(workspacePath, "memory", "vault");
                mkdirSync(vaultDir, { recursive: true });
                await writeJson(vaultStatePath, vaultState);
            }
            const vault = await readJson(vaultStatePath);
            if (vault) {
                // Simulate market surge
                vault.portfolio.total_value_eur = vault.portfolio.total_value_eur * 1.15; // +15%
                vault.last_update = new Date().toISOString();
                vault.last_event = "market_surge_simulated";
                await writeJson(vaultStatePath, vault);
                changes["vault"] = { total_value_eur: vault.portfolio.total_value_eur, simulated_surge: true };
            }
            // Also update economy state
            if (existsSync(economyStatePath)) {
                const eco = await readJson(economyStatePath);
                if (eco) {
                    eco.market_volatility = "high";
                    eco.last_trade_reason = "market_surge_scenario";
                    await writeJson(economyStatePath, eco);
                    changes["economy"] = { market_volatility: "high" };
                }
            }
            log.info("test_suite", `Scenario applied: ${scenario}`, changes);
            return {
                success: true,
                message: "📈 Market Surge scenario applied. Portfolio +15%, volatility set to 'high'. Trading engine should activate.",
                changes,
            };
        }
        case "social_event": {
            // Create a pending social event
            const socialEventsPath = join(workspacePath, "memory", "reality", "social_events.json");
            const socialEvent = {
                id: `test_event_${Date.now()}`,
                type: "incoming_message",
                from: "test_friend",
                timestamp: new Date().toISOString(),
                urgency: "normal",
                content: "Test message from scenario simulation",
            };
            let events = [];
            if (existsSync(socialEventsPath)) {
                events = (await readJson(socialEventsPath)) || [];
            }
            events.push(socialEvent);
            await writeJson(socialEventsPath, events);
            changes["social"] = { event: socialEvent };
            log.info("test_suite", `Scenario applied: ${scenario}`, changes);
            return {
                success: true,
                message: "🎭 Social Event scenario applied. New incoming message created. Social engine should process it.",
                changes,
            };
        }
        case "hobby_session": {
            // Set up a research/hobby session
            if (!existsSync(physiquePath)) {
                return { success: false, message: "physique.json not found", changes };
            }
            const ph = await readJson(physiquePath);
            if (ph) {
                ph.needs.energy = 60; // Enough for activity
                ph.needs.stress = 30;
                await writeJson(physiquePath, ph);
                changes["physique"] = { energy: 60, stress: 30 };
            }
            // Create hobby state
            const hobbyStatePath = join(workspacePath, "memory", "reality", "hobby_state.json");
            const hobbyState = {
                current_activity: "coding",
                started_at: new Date().toISOString(),
                intensity: "deep",
                project: "test_project",
            };
            await writeJson(hobbyStatePath, hobbyState);
            changes["hobby"] = hobbyState;
            log.info("test_suite", `Scenario applied: ${scenario}`, changes);
            return {
                success: true,
                message: "🎨 Hobby Session scenario applied. Energy=60%, Stress=30%, hobby state active. Hobby engine should process.",
                changes,
            };
        }
        case "full_health": {
            // Reset all needs to healthy values
            if (!existsSync(physiquePath)) {
                return { success: false, message: "physique.json not found", changes };
            }
            const ph = await readJson(physiquePath);
            if (ph) {
                ph.needs = {
                    energy: 80,
                    hunger: 40,
                    thirst: 40,
                    hygiene: 80,
                    bladder: 40,
                    bowel: 50,
                    stress: 20,
                    social: 50,
                    joy: 70,
                    arousal: 30,
                    libido: 30,
                };
                await writeJson(physiquePath, ph);
                changes["physique"] = ph.needs;
            }
            // Reset lifecycle
            if (existsSync(lifecyclePath)) {
                const lc = await readJson(lifecyclePath);
                if (lc) {
                    lc.is_asleep = false;
                    lc.is_napping = false;
                    await writeJson(lifecyclePath, lc);
                    changes["lifecycle"] = { is_asleep: false, is_napping: false };
                }
            }
            log.info("test_suite", `Scenario applied: ${scenario}`, changes);
            return {
                success: true,
                message: "💚 Full Health scenario applied. All needs reset to healthy values. Ready for normal operation.",
                changes,
            };
        }
        default:
            return { success: false, message: `Unknown scenario: ${scenario}`, changes };
    }
}
/**
 * Run self-test across all engines
 */
async function runSelfTest(workspacePath) {
    const results = {};
    // 1. Check Physique
    try {
        const physiquePath = join(workspacePath, "memory", "reality", "physique.json");
        if (existsSync(physiquePath)) {
            const ph = await readJson(physiquePath);
            if (ph && ph.needs) {
                results["physique"] = { status: "PASS", message: "Physique file readable and valid" };
            }
            else {
                results["physique"] = { status: "FAIL", message: "Physique file corrupted or empty" };
            }
        }
        else {
            results["physique"] = { status: "FAIL", message: "Physique file not found" };
        }
    }
    catch (e) {
        results["physique"] = { status: "FAIL", message: `Error: ${e}` };
    }
    // 2. Check Lifecycle
    try {
        const lifecyclePath = join(workspacePath, "memory", "reality", "lifecycle.json");
        if (existsSync(lifecyclePath)) {
            const lc = await readJson(lifecyclePath);
            if (lc) {
                results["lifecycle"] = { status: "PASS", message: "Lifecycle file readable" };
            }
            else {
                results["lifecycle"] = { status: "WARN", message: "Lifecycle file empty" };
            }
        }
        else {
            results["lifecycle"] = { status: "WARN", message: "Lifecycle file not found" };
        }
    }
    catch (e) {
        results["lifecycle"] = { status: "FAIL", message: `Error: ${e}` };
    }
    // 3. Check Economy
    try {
        const economyStatePath = join(workspacePath, "memory", "reality", "economy_state.json");
        if (existsSync(economyStatePath)) {
            const eco = await readJson(economyStatePath);
            if (eco) {
                results["economy"] = { status: "PASS", message: "Economy state readable" };
            }
            else {
                results["economy"] = { status: "WARN", message: "Economy state empty" };
            }
        }
        else {
            results["economy"] = { status: "WARN", message: "Economy state not found" };
        }
    }
    catch (e) {
        results["economy"] = { status: "FAIL", message: `Error: ${e}` };
    }
    // 4. Check Hardware Bridge
    try {
        const hardwarePath = join(workspacePath, "memory", "reality", "hardware_resonance.json");
        if (existsSync(hardwarePath)) {
            const hw = await readJson(hardwarePath);
            if (hw) {
                results["hardware"] = { status: "PASS", message: "Hardware state readable" };
            }
            else {
                results["hardware"] = { status: "WARN", message: "Hardware state empty" };
            }
        }
        else {
            results["hardware"] = { status: "WARN", message: "Hardware state not found" };
        }
    }
    catch (e) {
        results["hardware"] = { status: "FAIL", message: `Error: ${e}` };
    }
    // 5. Check VRM Avatar
    try {
        const avatarConfigPath = join(workspacePath, "memory", "reality", "avatar_config.json");
        if (existsSync(avatarConfigPath)) {
            const avatar = await readJson(avatarConfigPath);
            if (avatar && avatar.default_vrm_path) {
                if (existsSync(avatar.default_vrm_path)) {
                    results["avatar"] = { status: "PASS", message: `VRM found: ${avatar.default_vrm_path}` };
                }
                else {
                    results["avatar"] = { status: "WARN", message: "VRM path configured but file not found" };
                }
            }
            else {
                results["avatar"] = { status: "WARN", message: "No VRM path configured" };
            }
        }
        else {
            results["avatar"] = { status: "WARN", message: "Avatar config not found" };
        }
    }
    catch (e) {
        results["avatar"] = { status: "FAIL", message: `Error: ${e}` };
    }
    // 6. Check Social Engine
    try {
        const socialPath = join(workspacePath, "memory", "reality", "social.json");
        if (existsSync(socialPath)) {
            const social = await readJson(socialPath);
            if (social) {
                results["social"] = { status: "PASS", message: "Social state readable" };
            }
            else {
                results["social"] = { status: "WARN", message: "Social state empty" };
            }
        }
        else {
            results["social"] = { status: "WARN", message: "Social state not found" };
        }
    }
    catch (e) {
        results["social"] = { status: "FAIL", message: `Error: ${e}` };
    }
    // Generate report
    const passed = Object.values(results).filter(r => r.status === "PASS").length;
    const failed = Object.values(results).filter(r => r.status === "FAIL").length;
    const warnings = Object.values(results).filter(r => r.status === "WARN").length;
    let report = "## 🩺 Genesis Self-Test Report\n\n";
    report += `**Overall:** ${passed} PASS | ${failed} FAIL | ${warnings} WARN\n\n`;
    for (const [engine, result] of Object.entries(results)) {
        const icon = result.status === "PASS" ? "✅" : result.status === "FAIL" ? "❌" : "⚠️";
        report += `${icon} **[${result.status}]** ${engine}: ${result.message}\n`;
    }
    const success = failed === 0;
    return { success, report, results };
}
/**
 * Register test suite tools
 */
export function registerTestSuiteTools(api, paths, workspacePath) {
    // Tool: reality_simulate_scenario
    api.registerTool({
        name: "reality_simulate_scenario",
        description: "Apply a test scenario to simulate specific conditions (night_recovery, critical_reflex, market_surge, social_event, hobby_session, full_health).",
        parameters: Type.Object({
            scenario: Type.String({
                enum: ["night_recovery", "critical_reflex", "market_surge", "social_event", "hobby_session", "full_health"],
                description: "Scenario to apply",
            }),
        }),
        async execute(_id, params) {
            const result = await applyScenario(workspacePath, params.scenario);
            if (result.success) {
                return { content: [{ type: "text", text: result.message }] };
            }
            else {
                return { content: [{ type: "text", text: `❌ Error: ${result.message}` }] };
            }
        },
    });
    // Tool: reality_run_self_test
    api.registerTool({
        name: "reality_run_self_test",
        description: "Run a self-diagnostic test across all simulation engines.",
        parameters: Type.Object({}),
        async execute(_id) {
            const result = await runSelfTest(workspacePath);
            return { content: [{ type: "text", text: result.report }] };
        },
    });
    // Tool: reality_doctor
    api.registerTool({
        name: "reality_doctor",
        description: "Run the Genesis Doctor diagnostic and optionally auto-fix issues.",
        parameters: Type.Object({
            auto_fix: Type.Optional(Type.Boolean({ description: "Automatically fix issues (default: true)" })),
        }),
        async execute(_id, params) {
            const { runDoctor } = await import("../utils/doctor.js");
            const report = await runDoctor(workspacePath, params.auto_fix ?? true);
            let message = `## 🩺 Genesis Doctor Report\n\n`;
            message += `**Status:** ${report.overallStatus}\n`;
            message += `**Passed:** ${report.summary.passed} | **Failed:** ${report.summary.failed} | **Warnings:** ${report.summary.warnings}`;
            if (report.summary.fixed > 0) {
                message += ` | **Fixed:** ${report.summary.fixed}`;
            }
            message += `\n\n`;
            for (const result of report.results) {
                const icon = result.status === "PASS" ? "✅" : result.status === "FAIL" ? "❌" : "⚠️";
                message += `${icon} ${result.check}: ${result.message}\n`;
            }
            return { content: [{ type: "text", text: message }] };
        },
    });
}
//# sourceMappingURL=test_suite.js.map