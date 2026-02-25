import type { WorldState } from "../types/index.js";
import { getRealWorldSeason, getEstimatedWeather } from "../types/index.js";
export { getRealWorldSeason, getEstimatedWeather };
/**
 * Sync world state with real-world season/weather
 */
export declare function syncWorldWithRealWorld(worldState: WorldState): WorldState;
/**
 * Process RSS news and update world state
 */
export declare function processWorldNews(worldState: WorldState, headlines: {
    title: string;
    timestamp: string;
    category: string;
}[]): {
    changed: boolean;
    worldState: WorldState;
};
//# sourceMappingURL=world.d.ts.map