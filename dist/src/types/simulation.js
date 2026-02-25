// ---------------------------------------------------------------------------
// Core Simulation Types - Extracted from index.ts
// ---------------------------------------------------------------------------
// ---------------------------------------------------------------------------
// Sensory descriptions (Prompts - Always English)
// ---------------------------------------------------------------------------
export const SENSATIONS = {
    bladder: {
        high: ["Extreme, painful bladder pressure. You MUST go NOW!"],
        medium: ["Strong urge to pee. You feel restless."],
        low: ["You notice your bladder clearly."],
    },
    hunger: {
        high: ["Your stomach growls loudly, you feel weak from hunger."],
        medium: ["You have a strong appetite."],
        low: ["You notice you should eat something soon."],
    },
    thirst: {
        high: ["Your mouth is dry, you desperately need a drink."],
        medium: ["You're thirsty."],
        low: ["A glass of water would be nice."],
    },
    arousal: {
        high: ["Extreme physical arousal. Every touch of your clothing is intense."],
        medium: ["A pulsing desire spreads through you."],
        low: ["A faint tingle beneath your skin."],
    },
    stress: {
        high: ["You're extremely tense, your hands are slightly trembling."],
        medium: ["You feel stressed and restless."],
        low: ["Slight inner tension."],
    },
    hygiene: {
        high: ["You feel uncomfortable and unclean. A shower is urgently needed."],
        medium: ["You could use a shower."],
        low: ["You don't feel quite fresh anymore."],
    },
    energy: {
        low_critical: ["You're completely exhausted. Your eyes are closing."],
        low_medium: ["You're tired and unfocused."],
    },
    bowel: {
        high: ["Strong pressure in your abdomen. You urgently need the toilet."],
        medium: ["Your stomach is rumbling. You should find a toilet soon."],
        low: ["Slight feeling of fullness in your abdomen."],
    },
    libido: {
        high: ["A deep, persistent desire burns within you. It's hard to think of anything else."],
        medium: ["You feel a warm, pulsing desire."],
        low: ["A quiet longing, barely more than a whisper."],
    },
};
// ---------------------------------------------------------------------------
// Cycle: Hormone lookup tables (28-day, 0-100 scale, medically referenced)
// ---------------------------------------------------------------------------
export const HORMONE_ESTROGEN = [
    20, 22, 25, 28, 30, 35, 42, 50, 60, 70, 80, 90, 95, 100,
    85, 65, 50, 45, 55, 65, 70, 68, 60, 50, 40, 32, 25, 20
];
export const HORMONE_PROGESTERONE = [
    5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 8,
    15, 30, 50, 65, 80, 90, 100, 95, 85, 70, 55, 40, 20, 8
];
export const HORMONE_LH = [
    10, 10, 10, 12, 12, 14, 16, 18, 22, 30, 45, 70, 95, 100,
    40, 15, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10
];
export const HORMONE_FSH = [
    35, 40, 50, 55, 60, 65, 70, 65, 55, 45, 40, 50, 70, 80,
    40, 25, 20, 18, 16, 15, 14, 13, 12, 12, 15, 20, 25, 30
];
// ---------------------------------------------------------------------------
// Utility Functions
// ---------------------------------------------------------------------------
export function getRealWorldSeason() {
    const month = new Date().getMonth() + 1;
    if (month >= 3 && month <= 5)
        return "spring";
    if (month >= 6 && month <= 8)
        return "summer";
    if (month >= 9 && month <= 11)
        return "autumn";
    return "winter";
}
export function getEstimatedWeather(season) {
    const rand = Math.random();
    switch (season) {
        case "summer":
            return rand > 0.3 ? { weather: "sunny", temp: 25 + Math.round(rand * 10) } : { weather: "cloudy", temp: 20 };
        case "winter":
            return rand > 0.5 ? { weather: "snowy", temp: -2 - Math.round(rand * 5) } : { weather: "cloudy", temp: 2 };
        case "autumn":
            return rand > 0.4 ? { weather: "rainy", temp: 10 } : { weather: "stormy", temp: 8 };
        default:
            return { weather: "sunny", temp: 18 };
    }
}
export function getSkillMultiplier(skillState, skillName, base = 20) {
    if (!skillState?.skills)
        return 1.0;
    const skill = skillState.skills.find(s => s.name.toLowerCase() === skillName.toLowerCase());
    if (!skill)
        return 1.0;
    return 1 + (skill.level / base);
}
/**
 * Get a sensory description for a need value.
 */
export function getSensation(value, type) {
    const s = SENSATIONS[type];
    if (!s)
        return null;
    if (type === "energy") {
        if (value < 10)
            return s.low_critical?.[0] ?? null;
        if (value < 30)
            return s.low_medium?.[0] ?? null;
        return null;
    }
    if (value > 90)
        return s.high?.[0] ?? null;
    if (value > 60)
        return s.medium?.[0] ?? null;
    if (value > 40)
        return s.low?.[0] ?? null;
    return null;
}
export function getCycleHormones(day) {
    const i = Math.max(0, Math.min(27, day - 1));
    return {
        estrogen: HORMONE_ESTROGEN[i],
        progesterone: HORMONE_PROGESTERONE[i],
        lh: HORMONE_LH[i],
        fsh: HORMONE_FSH[i],
    };
}
export function getAgeSensation(ageDays, stage) {
    const years = Math.floor(ageDays / 365.25);
    if (stage === "infant") {
        return "Your senses are new and overwhelming. Everything is bright and loud.";
    }
    if (stage === "child") {
        return "You're full of curiosity. The world is fascinating.";
    }
    if (stage === "teen") {
        return "Hormones surge through you. Emotions feel intense and all-consuming.";
    }
    if (stage === "adult") {
        return "You feel in your prime, capable and focused.";
    }
    if (stage === "middle_adult") {
        if (years >= 65) {
            return "You notice subtle changes in your energy levels.";
        }
        return null;
    }
    if (stage === "senior") {
        return "Your body moves slower. Wisdom fills the spaces where energy once did.";
    }
    return null;
}
//# sourceMappingURL=simulation.js.map