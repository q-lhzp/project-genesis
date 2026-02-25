// ---------------------------------------------------------------------------
// World Simulation - Extracted from index.ts
// ---------------------------------------------------------------------------
import { getRealWorldSeason, getEstimatedWeather } from "../types/index.js";
export { getRealWorldSeason, getEstimatedWeather };
/**
 * Sync world state with real-world season/weather
 */
export function syncWorldWithRealWorld(worldState) {
    const currentSeason = getRealWorldSeason();
    const { weather, temp } = getEstimatedWeather(currentSeason);
    worldState.season = currentSeason;
    worldState.weather = weather;
    worldState.temperature = temp;
    worldState.last_update = new Date().toISOString();
    worldState.sync_to_real_world = true;
    return worldState;
}
/**
 * Process RSS news and update world state
 */
export function processWorldNews(worldState, headlines) {
    let changed = false;
    for (const headline of headlines) {
        if (headline.title.toLowerCase().includes("weather") || headline.title.toLowerCase().includes("storm")) {
            const weathers = ["sunny", "cloudy", "rainy", "stormy", "snowy"];
            worldState.weather = weathers[Math.floor(Math.random() * weathers.length)];
            changed = true;
        }
    }
    if (changed) {
        worldState.last_update = new Date().toISOString();
    }
    return { changed, worldState };
}
//# sourceMappingURL=world.js.map