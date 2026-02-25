// ---------------------------------------------------------------------------
// Genesis Doctor - Self-Healing Diagnostic Engine (Phase 46)
// Autonomous validation and self-healing for Project Genesis
// ---------------------------------------------------------------------------
import { readJson, writeJson } from "./persistence.js";
import { join } from "node:path";
import { existsSync, chmodSync, statSync } from "node:fs";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
const execFileAsync = promisify(execFile);
/**
 * Required system tools
 */
const REQUIRED_SYSTEM_TOOLS = [
    { name: "python3", command: "python3", args: ["--version"] },
    { name: "top", command: "top", args: ["-bn1"] },
    { name: "pactl", command: "pactl", args: ["--version"] },
    { name: "free", command: "free", args: ["-m"] },
];
/**
 * Required bridge files
 */
function getRequiredBridges(workspacePath) {
    return [
        { path: join(workspacePath, "skills", "soul-evolution", "tools", "soul-viz.py"), name: "soul-viz.py", required: true },
        { path: join(workspacePath, "skills", "soul-evolution", "tools", "godmode_bridge.py"), name: "godmode_bridge.py", required: false },
        { path: join(workspacePath, "tools", "vision", "camera_bridge.py"), name: "camera_bridge.py", required: false },
        { path: join(workspacePath, "tools", "vision", "face_analysis.py"), name: "face_analysis.py", required: false },
        { path: join(workspacePath, "skills", "soul-evolution", "tools", "voice", "voice_bridge.py"), name: "voice_bridge.py", required: false },
    ];
}
/**
 * Required state files
 */
function getRequiredStateFiles(workspacePath) {
    return [
        join(workspacePath, "memory", "reality", "physique.json"),
        join(workspacePath, "memory", "reality", "world.json"),
        join(workspacePath, "memory", "reality", "interests.json"),
        join(workspacePath, "memory", "reality", "wardrobe.json"),
    ];
}
/**
 * Default physique template
 */
function getPhysiqueTemplate() {
    return {
        age_days: 9125, // ~25 years
        biological_age_days: 9125,
        current_location: "home_bedroom",
        current_outfit: ["Casual clothes"],
        vitals: {
            heart_rate: 70,
            blood_pressure_systolic: 120,
            blood_pressure_diastolic: 80,
            body_temperature: 36.6,
        },
        needs: {
            energy: 70,
            hunger: 50,
            thirst: 50,
            hygiene: 70,
            bladder: 50,
            stress: 30,
            social: 50,
            joy: 50,
            arousal: 20,
        },
    };
}
/**
 * Default world template
 */
function getWorldTemplate() {
    return {
        locations: [
            { id: "home_bedroom", name: "Bedroom", type: "indoor", address: "Home" },
            { id: "home_living", name: "Living Room", type: "indoor", address: "Home" },
            { id: "home_kitchen", name: "Kitchen", type: "indoor", address: "Home" },
            { id: "city_park", name: "City Park", type: "outdoor", address: "Central Park" },
            { id: "city_cafe", name: "Cafe", type: "indoor", address: "Main Street" },
            { id: "gym", name: "Gym", type: "indoor", address: "Fitness Center" },
            { id: "work", name: "Office", type: "indoor", address: "Tech Hub" },
        ],
        current_time: new Date().toISOString(),
    };
}
/**
 * Default interests template
 */
function getInterestsTemplate() {
    return {
        active: ["Technology", "Learning", "Music"],
        passive: ["Podcasts", "Audiobooks"],
        technical: ["Coding", "AI"],
    };
}
/**
 * Default wardrobe template
 */
function getWardrobeTemplate() {
    return {
        tops: [
            { id: "casual_tshirt", name: "Casual T-Shirt", category: "tops", color: "blue", comfort: 10 },
        ],
        bottoms: [
            { id: "casual_jeans", name: "Jeans", category: "bottoms", color: "blue", comfort: 8 },
        ],
        shoes: [
            { id: "sneakers", name: "Sneakers", category: "shoes", color: "white", comfort: 7 },
        ],
        accessories: [],
        current_outfit: ["casual_tshirt", "casual_jeans", "sneakers"],
    };
}
/**
 * Run a diagnostic check
 */
async function runDiagnosticCheck(workspacePath) {
    const results = [];
    let passed = 0;
    let failed = 0;
    let warnings = 0;
    let fixed = 0;
    // 1. Bridge Verification
    const bridges = getRequiredBridges(workspacePath);
    for (const bridge of bridges) {
        const result = {
            check: `bridge:${bridge.name}`,
            status: "PASS",
            message: "",
        };
        try {
            if (!existsSync(bridge.path)) {
                if (bridge.required) {
                    result.status = "FAIL";
                    result.message = `Required bridge not found: ${bridge.path}`;
                    failed++;
                }
                else {
                    result.status = "WARN";
                    result.message = `Optional bridge not found: ${bridge.path}`;
                    warnings++;
                }
            }
            else {
                // Check if executable
                try {
                    const stats = statSync(bridge.path);
                    const mode = stats.mode;
                    const isExecutable = (mode & 0o111) !== 0;
                    if (!isExecutable) {
                        // Try to fix
                        chmodSync(bridge.path, 0o755);
                        result.status = "PASS";
                        result.message = `Bridge found and fixed (chmod +x): ${bridge.name}`;
                        result.fixed = true;
                        fixed++;
                        passed++;
                    }
                    else {
                        result.message = `Bridge found and executable: ${bridge.name}`;
                        passed++;
                    }
                }
                catch (e) {
                    result.status = "WARN";
                    result.message = `Could not check permissions: ${bridge.name}`;
                    warnings++;
                }
            }
        }
        catch (e) {
            result.status = "FAIL";
            result.message = `Error checking bridge: ${e}`;
            failed++;
        }
        results.push(result);
    }
    // 2. System Tools Check
    for (const tool of REQUIRED_SYSTEM_TOOLS) {
        const result = {
            check: `system:${tool.name}`,
            status: "PASS",
            message: "",
        };
        try {
            await execFileAsync(tool.command, tool.args, { timeout: 5000 });
            result.message = `System tool available: ${tool.name}`;
            passed++;
        }
        catch {
            result.status = "WARN";
            result.message = `System tool not available: ${tool.name} (some features may be limited)`;
            warnings++;
        }
        results.push(result);
    }
    // 3. Path Alignment Check
    const stateFiles = getRequiredStateFiles(workspacePath);
    for (const filePath of stateFiles) {
        const result = {
            check: `path:${filePath.split("/").pop()}`,
            status: "PASS",
            message: "",
        };
        const fileName = filePath.split("/").pop() || "";
        if (!existsSync(filePath)) {
            // Try to restore from template
            let template;
            switch (fileName) {
                case "physique.json":
                    template = getPhysiqueTemplate();
                    break;
                case "world.json":
                    template = getWorldTemplate();
                    break;
                case "interests.json":
                    template = getInterestsTemplate();
                    break;
                case "wardrobe.json":
                    template = getWardrobeTemplate();
                    break;
            }
            if (template) {
                try {
                    await writeJson(filePath, template);
                    result.status = "PASS";
                    result.message = `Restored missing file from template: ${fileName}`;
                    result.fixed = true;
                    fixed++;
                    passed++;
                }
                catch (e) {
                    result.status = "FAIL";
                    result.message = `Could not restore file: ${fileName} - ${e}`;
                    failed++;
                }
            }
            else {
                result.status = "FAIL";
                result.message = `Critical file missing and no template: ${fileName}`;
                failed++;
            }
        }
        else {
            // Check if file is valid JSON
            try {
                const data = await readJson(filePath);
                if (!data) {
                    result.status = "FAIL";
                    result.message = `Invalid or empty file: ${fileName}`;
                    failed++;
                }
                else {
                    result.message = `Valid file: ${fileName}`;
                    passed++;
                }
            }
            catch (e) {
                result.status = "FAIL";
                result.message = `Corrupted file (invalid JSON): ${fileName}`;
                failed++;
            }
        }
        results.push(result);
    }
    // 4. State Integrity Check (physique needs validation)
    const physiquePath = join(workspacePath, "memory", "reality", "physique.json");
    if (existsSync(physiquePath)) {
        const result = {
            check: "state:physique_integrity",
            status: "PASS",
            message: "",
        };
        try {
            const ph = await readJson(physiquePath);
            if (!ph) {
                result.status = "FAIL";
                result.message = "physique.json is empty";
                failed++;
            }
            else {
                // Validate needs
                const needs = ph.needs;
                const requiredNeeds = ["energy", "hunger", "thirst", "hygiene", "stress"];
                let hasInvalidNeeds = false;
                for (const need of requiredNeeds) {
                    if (typeof needs[need] !== "number" || needs[need] < 0 || needs[need] > 100) {
                        hasInvalidNeeds = true;
                        break;
                    }
                }
                if (hasInvalidNeeds) {
                    result.status = "WARN";
                    result.message = "physique.json has invalid need values (should be 0-100)";
                    warnings++;
                }
                else {
                    result.message = "physique.json integrity OK";
                    passed++;
                }
            }
        }
        catch (e) {
            result.status = "FAIL";
            result.message = `Error checking physique: ${e}`;
            failed++;
        }
        results.push(result);
    }
    // Phase 50: Alpaca API Credentials Check
    const modelConfigPath = join(workspacePath, "memory", "reality", "model_config.json");
    const alpacaResult = {
        check: "vault:alpaca_credentials",
        status: "PASS",
        message: "",
    };
    try {
        if (existsSync(modelConfigPath)) {
            const config = await readJson(modelConfigPath);
            const hasApiKey = !!config.vault_api_key;
            const hasSecret = !!config.vault_api_secret;
            if (!hasApiKey || !hasSecret) {
                alpacaResult.status = "WARN";
                alpacaResult.message = "Alpaca API keys not configured (Paper trading only)";
                warnings++;
            }
            else {
                alpacaResult.message = "Alpaca API credentials configured";
                passed++;
            }
        }
        else {
            alpacaResult.status = "WARN";
            alpacaResult.message = "model_config.json not found (Paper trading only)";
            warnings++;
        }
    }
    catch (e) {
        alpacaResult.status = "FAIL";
        alpacaResult.message = `Error checking Alpaca credentials: ${e}`;
        failed++;
    }
    results.push(alpacaResult);
    // Phase 50: BlendShape Keys Verification (52+ required)
    const avatarStatePath = join(workspacePath, "memory", "reality", "avatar_state.json");
    const blendResult = {
        check: "avatar:blendshape_keys",
        status: "PASS",
        message: "",
    };
    const REQUIRED_BLENDSHAPES = [
        "joy", "angry", "sad", "fear", "surprise", "neutral", "relaxed", "disgusted",
        "blinkLeft", "blinkRight", "blink", "lookUp", "lookDown", "lookLeft", "lookRight",
        "eyeWiden", "eyeSquint", "eyeClose",
        "browUp", "browDown", "browOuterUp", "browInnerUp", "browLeft", "browRight",
        "noseSneer", "noseWrinkle",
        "mouthOpen", "mouthClose", "jawOpen", "jawClose", "jawLeft", "jawRight",
        "mouthFunnel", "mouthPucker", "mouthLeft", "mouthRight",
        "mouthSmileLeft", "mouthSmileRight", "mouthFrownLeft", "mouthFrownRight",
        "mouthGrimace", "mouthLaugh", "mouthShrugUpper", "mouthShrugLower", "mouthRoll", "tongueOut",
        "cheekPuff", "cheekSquintLeft", "cheekSquintRight", "cheekSuck",
        "chinUp", "chinDown", "chinSideLeft", "chinSideRight",
        "sleeping", "breathing", "yawning", "swallowing"
    ];
    try {
        if (existsSync(avatarStatePath)) {
            const avatar = await readJson(avatarStatePath);
            const currentShapes = avatar.blendShapes || {};
            const currentKeys = Object.keys(currentShapes);
            const missingKeys = REQUIRED_BLENDSHAPES.filter(k => !currentKeys.includes(k));
            if (missingKeys.length > 10) {
                blendResult.status = "WARN";
                blendResult.message = `${missingKeys.length} BlendShape keys missing (using defaults)`;
                warnings++;
            }
            else if (currentKeys.length < 40) {
                blendResult.status = "WARN";
                blendResult.message = `Only ${currentKeys.length} BlendShapes defined (52+ recommended)`;
                warnings++;
            }
            else {
                blendResult.message = `${currentKeys.length} BlendShape keys verified`;
                passed++;
            }
        }
        else {
            blendResult.status = "WARN";
            blendResult.message = "avatar_state.json not found (will use defaults)";
            warnings++;
        }
    }
    catch (e) {
        blendResult.status = "FAIL";
        blendResult.message = `Error checking BlendShapes: ${e}`;
        failed++;
    }
    results.push(blendResult);
    // Phase 50: Portrait Storage Limit Check
    const portraitsDir = join(workspacePath, "memory", "reality", "portraits");
    const portraitResult = {
        check: "visual:portrait_storage",
        status: "PASS",
        message: "",
    };
    try {
        if (existsSync(portraitsDir)) {
            const files = await import("node:fs/promises");
            const dirFiles = await files.readdir(portraitsDir);
            const portraitFiles = dirFiles.filter(f => f.endsWith(".png"));
            const totalSize = await files.stat(portraitsDir).then(() => 0).catch(() => 0);
            // Calculate total size
            let size = 0;
            for (const file of portraitFiles) {
                try {
                    const stats = await files.stat(join(portraitsDir, file));
                    size += stats.size;
                }
                catch { /* ignore */ }
            }
            const sizeMB = (size / (1024 * 1024)).toFixed(2);
            if (portraitFiles.length > 100) {
                portraitResult.status = "WARN";
                portraitResult.message = `${portraitFiles.length} portraits (${sizeMB}MB) - consider cleanup`;
                warnings++;
            }
            else {
                portraitResult.message = `${portraitFiles.length} portraits (${sizeMB}MB) - OK`;
                passed++;
            }
        }
        else {
            portraitResult.message = "portraits directory not yet created";
            passed++;
        }
    }
    catch (e) {
        portraitResult.status = "WARN";
        portraitResult.message = `Could not check portrait storage: ${e}`;
        warnings++;
    }
    results.push(portraitResult);
    // Phase 50: Image Bridge Check
    const imageBridgePath = join(workspacePath, "skills", "soul-evolution", "tools", "vision", "generate_image.py");
    const imageBridgeResult = {
        check: "visual:image_bridge",
        status: "PASS",
        message: "",
    };
    try {
        if (!existsSync(imageBridgePath)) {
            imageBridgeResult.status = "FAIL";
            imageBridgeResult.message = "generate_image.py not found";
            failed++;
        }
        else {
            imageBridgeResult.message = "Image generation bridge available";
            passed++;
        }
    }
    catch (e) {
        imageBridgeResult.status = "FAIL";
        imageBridgeResult.message = `Error checking image bridge: ${e}`;
        failed++;
    }
    results.push(imageBridgeResult);
    // Determine overall status
    let overallStatus;
    if (failed === 0 && warnings === 0) {
        overallStatus = "HEALTHY";
    }
    else if (failed === 0) {
        overallStatus = "DEGRADED";
    }
    else {
        overallStatus = "CRITICAL";
    }
    return {
        timestamp: new Date().toISOString(),
        version: "5.5.0",
        workspacePath,
        overallStatus,
        results,
        summary: { passed, failed, warnings, fixed },
    };
}
/**
 * Run diagnostics and return formatted report
 */
export async function runDoctor(workspacePath, autoFix = true) {
    const report = await runDiagnosticCheck(workspacePath);
    return report;
}
/**
 * Quick health check - returns boolean
 */
export async function quickHealthCheck(workspacePath) {
    const report = await runDiagnosticCheck(workspacePath);
    return report.overallStatus === "HEALTHY" || report.overallStatus === "DEGRADED";
}
/**
 * Get diagnostic summary for API
 */
export async function getDiagnosticSummary(workspacePath) {
    const report = await runDiagnosticCheck(workspacePath);
    return {
        status: report.overallStatus,
        checks: report.results.map(r => ({
            name: r.check,
            status: r.status,
            message: r.message,
        })),
        summary: report.summary,
    };
}
//# sourceMappingURL=doctor.js.map