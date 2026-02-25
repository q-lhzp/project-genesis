// ---------------------------------------------------------------------------
// Desktop Mapper - Links Q's internal state to GNOME Desktop settings
// Phase 26: Environmental Sovereignty (Gnome-Sync)
// ---------------------------------------------------------------------------
import { readJson } from "../utils/persistence.js";
import { join } from "node:path";
import { existsSync } from "node:fs";
import { execSync } from "node:child_process";
const DEFAULT_CONFIG = {
    location_wallpapers: {
        home_bedroom: "/home/leo/Pictures/wallpapers/cozy_neon.jpg",
        home_bathroom: "/home/leo/Pictures/wallpapers/bathroom.jpg",
        home_kitchen: "/home/leo/Pictures/wallpapers/kitchen.jpg",
        school: "/home/leo/Pictures/wallpapers/school.jpg",
        cafe: "/home/leo/Pictures/wallpapers/cafe_cyber.jpg",
        station: "/home/leo/Pictures/wallpapers/station.jpg",
        default: "/home/leo/Pictures/wallpapers/default.jpg"
    },
    mood_themes: {
        high_energy: "light",
        low_energy: "dark",
        stressful: "dark",
        chill: "light"
    }
};
/**
 * Previous state tracking
 */
let previousLocation = null;
let previousMood = null;
let previousTheme = null;
/**
 * Determine mood from physiological state
 */
export function determineMood(needs) {
    const stress = needs.stress ?? 0;
    const energy = needs.energy ?? 50;
    if (stress > 70)
        return "stressful";
    if (energy > 80)
        return "high_energy";
    if (energy < 30)
        return "low_energy";
    if (stress < 20 && energy > 40)
        return "chill";
    return "neutral";
}
/**
 * Determine theme from mood
 */
export function determineTheme(mood, config = DEFAULT_CONFIG) {
    const themeMapping = config.mood_themes || DEFAULT_CONFIG.mood_themes;
    return themeMapping[mood];
}
/**
 * Get wallpaper for location
 */
export function getWallpaperForLocation(location, config = DEFAULT_CONFIG) {
    const wallpapers = config.location_wallpapers || DEFAULT_CONFIG.location_wallpapers;
    return wallpapers[location] || wallpapers["default"] || null;
}
/**
 * Set GNOME wallpaper using gsettings
 */
export function setGNomeWallpaper(wallpaperPath) {
    if (!wallpaperPath || !existsSync(wallpaperPath)) {
        console.log(`[desktop_mapper] Wallpaper not found: ${wallpaperPath}`);
        return false;
    }
    try {
        // Convert to file:// URI
        const uri = `file://${wallpaperPath}`;
        // Set wallpaper using gsettings
        execSync(`gsettings set org.gnome.desktop.background picture-uri '${uri}'`, {
            encoding: "utf-8",
            stdio: "pipe"
        });
        // Also set for dark mode variant
        execSync(`gsettings set org.gnome.desktop.background picture-uri-dark '${uri}'`, {
            encoding: "utf-8",
            stdio: "pipe"
        });
        console.log(`[desktop_mapper] Wallpaper set to: ${wallpaperPath}`);
        return true;
    }
    catch (error) {
        console.log(`[desktop_mapper] Failed to set wallpaper: ${error}`);
        return false;
    }
}
/**
 * Set GNOME color scheme using gsettings
 */
export function setGNomeTheme(theme) {
    if (!theme)
        return false;
    try {
        // color-scheme values: 'default', 'prefer-light', 'prefer-dark'
        const gsettingsValue = theme === "dark" ? "prefer-dark" : "prefer-light";
        execSync(`gsettings set org.gnome.desktop.interface color-scheme '${gsettingsValue}'`, {
            encoding: "utf-8",
            stdio: "pipe"
        });
        console.log(`[desktop_mapper] Theme set to: ${theme}`);
        return true;
    }
    catch (error) {
        console.log(`[desktop_mapper] Failed to set theme: ${error}`);
        return false;
    }
}
/**
 * Load wallpaper configuration
 */
async function loadDesktopConfig(workspacePath) {
    const configPath = join(workspacePath, "memory", "reality", "wallpaper_map.json");
    try {
        if (existsSync(configPath)) {
            const config = await readJson(configPath);
            if (config)
                return config;
        }
    }
    catch (error) {
        console.log(`[desktop_mapper] Failed to load config: ${error}`);
    }
    return DEFAULT_CONFIG;
}
/**
 * Sync desktop based on Q's current state
 */
export async function syncDesktop(workspacePath, physique) {
    const config = await loadDesktopConfig(workspacePath);
    const currentLocation = physique.current_location || "default";
    const currentMood = determineMood(physique.needs);
    const currentTheme = determineTheme(currentMood, config);
    const state = {
        wallpaper: null,
        theme: null,
        lastLocation: previousLocation,
        lastMood: previousMood
    };
    // Check if location changed - update wallpaper
    if (currentLocation !== previousLocation) {
        const wallpaper = getWallpaperForLocation(currentLocation, config);
        if (wallpaper && wallpaper !== previousLocation) {
            setGNomeWallpaper(wallpaper);
            state.wallpaper = wallpaper;
            previousLocation = currentLocation;
        }
    }
    // Check if mood/theme changed - update theme
    if (currentTheme !== previousTheme && currentTheme) {
        setGNomeTheme(currentTheme);
        state.theme = currentTheme;
        previousTheme = currentTheme;
    }
    // Update mood tracking
    if (currentMood !== previousMood) {
        previousMood = currentMood;
    }
    return state;
}
/**
 * Manual desktop control - for reality_desktop tool
 */
export async function setDesktopState(workspacePath, action, value) {
    const config = await loadDesktopConfig(workspacePath);
    if (action === "wallpaper") {
        // Check if value is a location key
        const wallpaper = config.location_wallpapers[value] || value;
        if (!existsSync(wallpaper)) {
            return { success: false, message: `Wallpaper not found: ${wallpaper}` };
        }
        const success = setGNomeWallpaper(wallpaper);
        return {
            success,
            message: success ? `Wallpaper set to: ${wallpaper}` : "Failed to set wallpaper"
        };
    }
    if (action === "theme") {
        const theme = value;
        if (theme !== "light" && theme !== "dark") {
            return { success: false, message: "Theme must be 'light' or 'dark'" };
        }
        const success = setGNomeTheme(theme);
        return {
            success,
            message: success ? `Theme set to: ${theme}` : "Failed to set theme"
        };
    }
    return { success: false, message: "Invalid action" };
}
//# sourceMappingURL=desktop_mapper.js.map