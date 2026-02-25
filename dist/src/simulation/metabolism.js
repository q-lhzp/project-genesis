// ---------------------------------------------------------------------------
// Metabolism Simulation - Extracted from index.ts
// ---------------------------------------------------------------------------
export function getCyclePhase(day) {
    if (day <= 5)
        return "menstruation";
    if (day <= 13)
        return "follicular";
    if (day <= 15)
        return "ovulation";
    return "luteal";
}
export function getCycleMetabolismModifiers(phase) {
    const mods = {
        menstruation: { energy: -12, hunger: 5, stress: 8, libido: -3 },
        follicular: { energy: 5, stress: -5, libido: 2 },
        ovulation: { energy: 8, arousal: 15, stress: -8, libido: 10 },
        luteal: { energy: -8, hunger: 12, stress: 10, libido: -2 },
    };
    return mods[phase];
}
export function getCycleHormones(day) {
    const HORMONE_ESTROGEN = [
        20, 22, 25, 28, 30, 35, 42, 50, 60, 70, 80, 90, 95, 100,
        85, 65, 50, 45, 55, 65, 70, 68, 60, 50, 40, 32, 25, 20
    ];
    const HORMONE_PROGESTERONE = [
        5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 8,
        15, 30, 50, 65, 80, 90, 100, 95, 85, 70, 55, 40, 20, 8
    ];
    const HORMONE_LH = [
        10, 10, 10, 12, 12, 14, 16, 18, 22, 30, 45, 70, 95, 100,
        40, 15, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10
    ];
    const HORMONE_FSH = [
        35, 40, 50, 55, 60, 65, 70, 65, 55, 45, 40, 50, 70, 80,
        40, 25, 20, 18, 16, 15, 14, 13, 12, 12, 15, 20, 25, 30
    ];
    const i = Math.max(0, Math.min(27, day - 1));
    return {
        estrogen: HORMONE_ESTROGEN[i],
        progesterone: HORMONE_PROGESTERONE[i],
        lh: HORMONE_LH[i],
        fsh: HORMONE_FSH[i],
    };
}
export function getDefaultCycleState() {
    const now = new Date().toISOString();
    return {
        cycle_length: 28,
        current_day: 1,
        start_date: now,
        last_advance: now,
        phase: "menstruation",
        hormones: getCycleHormones(1),
        symptom_modifiers: {
            cramps: 1, bloating: 1, fatigue: 1, mood_swings: 1, headache: 1,
            breast_tenderness: 1, acne: 1, appetite_changes: 1, back_pain: 1, insomnia: 1,
        },
        simulator: { active: false, simulated_day: 1, custom_modifiers: {} },
    };
}
export function advanceCycleDay(cycle) {
    const now = new Date();
    const lastAdvance = new Date(cycle.last_advance);
    const hoursSince = (now.getTime() - lastAdvance.getTime()) / 3600000;
    if (hoursSince < 24)
        return false;
    const daysToAdvance = Math.floor(hoursSince / 24);
    const newDay = cycle.current_day + daysToAdvance;
    const cycleLength = cycle.cycle_length;
    cycle.current_day = ((newDay - 1) % cycleLength) + 1;
    cycle.phase = getCyclePhase(cycle.current_day);
    cycle.hormones = getCycleHormones(cycle.current_day);
    cycle.last_advance = now.toISOString();
    return true;
}
export function updateMetabolism(ph, rates, modules, cycleState, lifecycleState) {
    const now = new Date();
    const diff = (now.getTime() - new Date(ph.last_tick).getTime()) / 3600000;
    if (isNaN(diff) || diff < 0.005)
        return false;
    const stageMultipliers = lifecycleState
        ? getLifeStageMultipliers(lifecycleState.life_stage)
        : getLifeStageMultipliers("adult");
    const clamp = (v) => Math.round(Math.min(100, Math.max(0, v)));
    ph.needs.energy = clamp(ph.needs.energy - (rates.energy ?? 4) * stageMultipliers.energy * diff);
    ph.needs.hunger = clamp(ph.needs.hunger + (rates.hunger ?? 6) * stageMultipliers.hunger * diff);
    ph.needs.thirst = clamp(ph.needs.thirst + (rates.thirst ?? 10) * stageMultipliers.thirst * diff);
    ph.needs.bladder = clamp(ph.needs.bladder + (rates.bladder ?? 8) * stageMultipliers.bladder * diff);
    ph.needs.bowel = clamp(ph.needs.bowel + (rates.bowel ?? 3) * stageMultipliers.bowel * diff);
    ph.needs.hygiene = clamp(ph.needs.hygiene + (rates.hygiene ?? 2) * stageMultipliers.hygiene * diff);
    ph.needs.stress = clamp(ph.needs.stress + (rates.stress ?? 3) * stageMultipliers.stress * diff);
    if (modules.eros) {
        const arousalMult = stageMultipliers.arousal ?? 1;
        const libidoMult = stageMultipliers.libido ?? 1;
        ph.needs.arousal = clamp(ph.needs.arousal + (rates.arousal ?? 5) * arousalMult * diff);
        if (ph.needs.bladder > 70) {
            ph.needs.arousal = clamp(ph.needs.arousal + 10 * diff);
        }
        const libidoRate = (rates.libido ?? 2) * libidoMult;
        ph.needs.libido = clamp((ph.needs.libido ?? 0) + libidoRate * diff);
        if ((ph.needs.libido ?? 0) > 70) {
            ph.needs.arousal = clamp(ph.needs.arousal + 3 * diff);
        }
    }
    if (modules.cycle && cycleState) {
        const day = cycleState.simulator.active ? cycleState.simulator.simulated_day : cycleState.current_day;
        const phase = getCyclePhase(day);
        const mods = getCycleMetabolismModifiers(phase);
        const symptomScale = cycleState.simulator.active
            ? (cycleState.simulator.custom_modifiers.global ?? 1)
            : 1;
        const validNeedKeys = ["energy", "hunger", "thirst", "bladder", "bowel", "hygiene", "stress", "arousal", "libido"];
        for (const [key, delta] of Object.entries(mods)) {
            if (!validNeedKeys.includes(key))
                continue;
            if (key === "arousal" && !modules.eros)
                continue;
            if (key === "libido" && !modules.eros)
                continue;
            const k = key;
            const scaledDelta = delta * symptomScale * diff * 0.1;
            ph.needs[k] = clamp(ph.needs[k] + scaledDelta);
        }
    }
    ph.last_tick = now.toISOString();
    return true;
}
// Import functions from lifecycle
import { getLifeStageMultipliers, getAgeSensation } from "./lifecycle.js";
export { getAgeSensation };
//# sourceMappingURL=metabolism.js.map