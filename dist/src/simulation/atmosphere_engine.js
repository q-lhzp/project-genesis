// ---------------------------------------------------------------------------
// Atmosphere Engine - Time and Weather-based Lighting
// Phase 29: Atmospheric Sync (Weather, Time & Lighting)
// ---------------------------------------------------------------------------
import { readJson, writeJson } from "../utils/persistence.js";
import { join } from "node:path";
import { existsSync, readFileSync } from "node:fs";
/**
 * Get time of day from hour
 */
export function getTimeOfDay(hour) {
    if (hour >= 5 && hour < 7)
        return "dawn";
    if (hour >= 7 && hour < 10)
        return "morning";
    if (hour >= 10 && hour < 14)
        return "noon";
    if (hour >= 14 && hour < 17)
        return "afternoon";
    if (hour >= 17 && hour < 19)
        return "evening";
    if (hour >= 19 && hour < 21)
        return "dusk";
    if (hour >= 21 || hour < 1)
        return "night";
    return "midnight";
}
/**
 * Get season from day of year
 */
export function getSeason(dayOfYear) {
    if (dayOfYear >= 79 && dayOfYear < 172)
        return "spring";
    if (dayOfYear >= 172 && dayOfYear < 266)
        return "summer";
    if (dayOfYear >= 266 && dayOfYear < 355)
        return "autumn";
    return "winter";
}
/**
 * Calculate lighting based on time of day
 */
function calculateLighting(timeOfDay, hour) {
    // Default values
    let lightIntensity = 0.8;
    let lightColor = "#ffffff";
    let ambientIntensity = 0.6;
    let ambientColor = "#ffffff";
    let backgroundColor = "#1a1a2e";
    switch (timeOfDay) {
        case "dawn":
            lightIntensity = 0.4;
            lightColor = "#ff9966"; // Warm orange
            ambientIntensity = 0.3;
            ambientColor = "#ffaa77";
            backgroundColor = "#2d1f3d"; // Purple-ish
            break;
        case "morning":
            lightIntensity = 0.7;
            lightColor = "#ffe4b5"; // Warm white
            ambientIntensity = 0.5;
            ambientColor = "#fff8dc";
            backgroundColor = "#1e3a5f"; // Blue-ish
            break;
        case "noon":
            lightIntensity = 1.0;
            lightColor = "#ffffff"; // Bright white
            ambientIntensity = 0.7;
            ambientColor = "#ffffff";
            backgroundColor = "#1a1a2e"; // Normal
            break;
        case "afternoon":
            lightIntensity = 0.8;
            lightColor = "#fffacd"; // Lemon chiffon
            ambientIntensity = 0.6;
            ambientColor = "#f0e68c";
            backgroundColor = "#1f2d3d";
            break;
        case "evening":
            lightIntensity = 0.5;
            lightColor = "#ffa07a"; // Light salmon
            ambientIntensity = 0.4;
            ambientColor = "#ffb347";
            backgroundColor = "#2d1f2e"; // Warm dark
            break;
        case "dusk":
            lightIntensity = 0.3;
            lightColor = "#ff7f50"; // Coral
            ambientIntensity = 0.25;
            ambientColor = "#ff6347";
            backgroundColor = "#1a1520"; // Dark purple
            break;
        case "night":
            lightIntensity = 0.1;
            lightColor = "#4169e1"; // Royal blue (moonlight)
            ambientIntensity = 0.15;
            ambientColor = "#6495ed";
            backgroundColor = "#0a0a15"; // Very dark
            break;
        case "midnight":
            lightIntensity = 0.05;
            lightColor = "#191970"; // Midnight blue
            ambientIntensity = 0.1;
            ambientColor = "#2c3e50";
            backgroundColor = "#050510"; // Almost black
            break;
    }
    return { lightIntensity, lightColor, ambientIntensity, ambientColor, backgroundColor };
}
/**
 * Get weather condition (simulated or from real data)
 */
async function getWeather(workspacePath) {
    // Try to load from world_state.json
    const worldStatePath = join(workspacePath, "memory", "reality", "world_state.json");
    try {
        if (existsSync(worldStatePath)) {
            const worldState = await readJson(worldStatePath);
            if (worldState?.weather) {
                return {
                    condition: worldState.weather,
                    temperature: worldState.temperature ?? 20,
                    humidity: worldState.humidity ?? 50
                };
            }
        }
    }
    catch (error) {
        console.log(`[atmosphere_engine] Failed to load weather: ${error}`);
    }
    // Fallback: Time-based weather simulation
    const hour = new Date().getHours();
    const month = new Date().getMonth();
    // More likely to be clear during day in summer
    if (hour >= 8 && hour <= 18 && (month >= 5 && month <= 8)) {
        return { condition: "clear", temperature: 25, humidity: 45 };
    }
    // More likely to be cloudy/rainy in winter or early morning/late evening
    if (hour < 8 || hour > 18 || (month >= 10 || month <= 2)) {
        return { condition: "cloudy", temperature: 10, humidity: 70 };
    }
    // Default
    return { condition: "clear", temperature: 20, humidity: 50 };
}
/**
 * Generate sensory description
 */
function generateSensoryDescription(timeOfDay, weather, temperature, location = "Berlin") {
    const timeDesc = {
        dawn: "in the early dawn",
        morning: "on a crisp morning",
        noon: "at noon",
        afternoon: "in the afternoon",
        evening: "in the evening",
        dusk: "at dusk",
        night: "at night",
        midnight: "in the late night"
    };
    const weatherDesc = {
        clear: "the sky is clear and bright",
        cloudy: "clouds cover the sky",
        rainy: "rain taps against the windows",
        stormy: "thunder rolls in the distance",
        snowy: "snowflakes drift down gently",
        foggy: "a thick fog hangs in the air",
        windy: "a brisk wind blows"
    };
    return `It's ${temperature}°C ${timeDesc[timeOfDay]}, ${weatherDesc[weather]} in ${location}.`;
}
/**
 * Main atmosphere sync function
 */
export async function syncAtmosphere(workspacePath, location = "home_bedroom") {
    const now = new Date();
    const hour = now.getHours();
    const minute = now.getMinutes();
    const dayOfYear = Math.floor((now.getTime() - new Date(now.getFullYear(), 0, 0).getTime()) / (1000 * 60 * 60 * 24));
    // Get time-based values
    const timeOfDay = getTimeOfDay(hour);
    const season = getSeason(dayOfYear);
    // Get weather
    const weatherData = await getWeather(workspacePath);
    // Calculate lighting
    const lighting = calculateLighting(timeOfDay, hour);
    // Generate sensory description
    const sensoryDescription = generateSensoryDescription(timeOfDay, weatherData.condition, weatherData.temperature);
    const atmosphere = {
        timeOfDay,
        hour,
        minute,
        dayOfYear,
        season,
        weather: weatherData.condition,
        temperature: weatherData.temperature,
        humidity: weatherData.humidity,
        lightIntensity: lighting.lightIntensity,
        lightColor: lighting.lightColor,
        ambientIntensity: lighting.ambientIntensity,
        ambientColor: lighting.ambientColor,
        backgroundColor: lighting.backgroundColor,
        sensoryDescription
    };
    // Write to state file for dashboard
    const statePath = join(workspacePath, "memory", "reality", "atmosphere_state.json");
    await writeJson(statePath, atmosphere);
    // Also try HTTP notification
    notifyDashboard(atmosphere).catch(() => { });
    return atmosphere;
}
/**
 * Non-blocking HTTP notification
 */
async function notifyDashboard(atmosphere) {
    try {
        const http = await import("node:http");
        const postData = JSON.stringify({
            action: "sync_atmosphere",
            atmosphere
        });
        const options = {
            hostname: "127.0.0.1",
            port: 8080,
            path: "/api/avatar/update",
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Content-Length": Buffer.byteLength(postData)
            }
        };
        return new Promise((resolve) => {
            const req = http.request(options, (res) => resolve());
            req.on("error", () => resolve());
            req.write(postData);
            req.end();
        });
    }
    catch {
        // Ignore
    }
}
/**
 * Get atmosphere for context injection
 */
export function getAtmosphereContext() {
    try {
        const statePath = "/home/leo/Schreibtisch/memory/reality/atmosphere_state.json";
        if (existsSync(statePath)) {
            const data = JSON.parse(readFileSync(statePath, "utf8"));
            return data.sensoryDescription;
        }
    }
    catch {
        // Ignore
    }
    return null;
}
//# sourceMappingURL=atmosphere_engine.js.map