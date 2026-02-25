/**
 * Time of day periods
 */
export type TimeOfDay = "dawn" | "morning" | "noon" | "afternoon" | "evening" | "dusk" | "night" | "midnight";
/**
 * Weather conditions
 */
export type WeatherCondition = "clear" | "cloudy" | "rainy" | "stormy" | "snowy" | "foggy" | "windy";
/**
 * Atmosphere state for 3D rendering
 */
export interface AtmosphereState {
    timeOfDay: TimeOfDay;
    hour: number;
    minute: number;
    dayOfYear: number;
    season: "spring" | "summer" | "autumn" | "winter";
    lightIntensity: number;
    lightColor: string;
    ambientIntensity: number;
    ambientColor: string;
    backgroundColor: string;
    weather: WeatherCondition;
    temperature: number;
    humidity: number;
    sensoryDescription: string;
}
/**
 * Get time of day from hour
 */
export declare function getTimeOfDay(hour: number): TimeOfDay;
/**
 * Get season from day of year
 */
export declare function getSeason(dayOfYear: number): "spring" | "summer" | "autumn" | "winter";
/**
 * Main atmosphere sync function
 */
export declare function syncAtmosphere(workspacePath: string, location?: string): Promise<AtmosphereState>;
/**
 * Get atmosphere for context injection
 */
export declare function getAtmosphereContext(): string | null;
//# sourceMappingURL=atmosphere_engine.d.ts.map