import type { Physique } from "../types/index.js";
/**
 * Desktop mapping configuration
 */
interface DesktopConfig {
    location_wallpapers: Record<string, string>;
    mood_themes: Record<string, string>;
}
/**
 * Desktop state to sync
 */
export interface DesktopState {
    wallpaper: string | null;
    theme: "light" | "dark" | null;
    lastLocation: string | null;
    lastMood: string | null;
}
/**
 * Determine mood from physiological state
 */
export declare function determineMood(needs: Physique["needs"]): string;
/**
 * Determine theme from mood
 */
export declare function determineTheme(mood: string, config?: DesktopConfig): "light" | "dark" | null;
/**
 * Get wallpaper for location
 */
export declare function getWallpaperForLocation(location: string, config?: DesktopConfig): string | null;
/**
 * Set GNOME wallpaper using gsettings
 */
export declare function setGNomeWallpaper(wallpaperPath: string): boolean;
/**
 * Set GNOME color scheme using gsettings
 */
export declare function setGNomeTheme(theme: "light" | "dark"): boolean;
/**
 * Sync desktop based on Q's current state
 */
export declare function syncDesktop(workspacePath: string, physique: Physique): Promise<DesktopState>;
/**
 * Manual desktop control - for reality_desktop tool
 */
export declare function setDesktopState(workspacePath: string, action: "wallpaper" | "theme", value: string): Promise<{
    success: boolean;
    message: string;
}>;
export {};
//# sourceMappingURL=desktop_mapper.d.ts.map