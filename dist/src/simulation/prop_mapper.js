// ---------------------------------------------------------------------------
// Prop Mapper - Interactive Environment & Prop Sync
// Phase 33: Interactive Environment (Props, Furniture, Light Control)
// ---------------------------------------------------------------------------
import { readJson, writeJson } from "../utils/persistence.js";
import { join } from "node:path";
import { existsSync } from "node:fs";
/**
 * Default interaction state
 */
export const DEFAULT_INTERACTION = {
    current_prop: null,
    current_furniture: null,
    current_action: "standing",
    holding: [],
    light_intensity: 0.8,
    light_color: "#ffffff",
    last_update: new Date().toISOString(),
};
const DEFAULT_CONFIG = {
    action_to_prop: {
        eat: { prop_id: "food_plate", bone: "RightHand", animation: "using" },
        drink: { prop_id: "drink_cup", bone: "RightHand", animation: "using" },
        read: { prop_id: "book_novel", bone: "LeftHand", animation: "reading" },
        work: { prop_id: "device_laptop", bone: "LeftHand", animation: "typing" },
        shower: { prop_id: "tool_sponge", bone: "RightHand", animation: "bathing" },
    },
    prop_descriptions: {
        food_plate: "Du haeltst einen Teller mit Essen in der Hand.",
        drink_cup: "Du haeltst eine Tasse in der Hand.",
        book_novel: "Du haeltst ein Buch zum Lesen.",
        device_laptop: "Du arbeitest an deinem Laptop.",
        tool_sponge: "Du wäschst dich mit einem Schwamm.",
    },
};
/**
 * Load inventory items
 */
export async function loadInventory(workspacePath) {
    const inventoryPath = join(workspacePath, "memory", "reality", "inventory.json");
    try {
        if (existsSync(inventoryPath)) {
            const data = await readJson(inventoryPath);
            if (data?.items) {
                return data.items.map(item => ({
                    id: item.id || item.name.toLowerCase().replace(/\s+/g, "_"),
                    name: item.name,
                    type: item.category || "other",
                    model_path: item.model_path,
                    bone_attachment: item.bone_attachment,
                    animation: item.animation,
                    description: item.description,
                }));
            }
        }
    }
    catch (error) {
        console.log(`[prop_mapper] Failed to load inventory: ${error}`);
    }
    return [];
}
/**
 * Load furniture data
 */
export async function loadFurniture(workspacePath) {
    const interiorPath = join(workspacePath, "memory", "reality", "interior.json");
    try {
        if (existsSync(interiorPath)) {
            const data = await readJson(interiorPath);
            if (data?.rooms) {
                const furniture = [];
                for (const room of data.rooms) {
                    if (room.furniture) {
                        for (const item of room.furniture) {
                            furniture.push({
                                id: item.id || item.name.toLowerCase().replace(/\s+/g, "_"),
                                name: item.name,
                                location: room.id || room.name,
                                position: item.position,
                                rotation: item.rotation,
                                scale: item.scale,
                                interaction_type: item.interaction_type,
                                target_bone: item.target_bone,
                                prop_slot: item.prop_slot,
                            });
                        }
                    }
                }
                return furniture;
            }
        }
    }
    catch (error) {
        console.log(`[prop_mapper] Failed to load furniture: ${error}`);
    }
    return [];
}
/**
 * Map action to prop
 */
export function mapActionToProp(action, config = DEFAULT_CONFIG) {
    return config.action_to_prop[action] || null;
}
/**
 * Get prop description
 */
export function getPropDescription(propId, config = DEFAULT_CONFIG) {
    return config.prop_descriptions[propId] || "";
}
/**
 * Find furniture by location and type
 */
export function findFurnitureByLocation(furniture, location, interactionType) {
    let candidates = furniture.filter(f => f.location === location);
    if (interactionType) {
        candidates = candidates.filter(f => f.interaction_type === interactionType);
    }
    return candidates.length > 0 ? candidates[0] : null;
}
/**
 * Update avatar interaction state
 */
export async function updateInteractionState(workspacePath, state) {
    const statePath = join(workspacePath, "memory", "reality", "interaction_state.json");
    let current = DEFAULT_INTERACTION;
    try {
        if (existsSync(statePath)) {
            current = await readJson(statePath) || DEFAULT_INTERACTION;
        }
    }
    catch {
        // Use default
    }
    const updated = {
        ...current,
        ...state,
        last_update: new Date().toISOString(),
    };
    await writeJson(statePath, updated);
    // Notify dashboard via HTTP
    notifyDashboardInteraction(updated).catch(() => { });
    return updated;
}
/**
 * Trigger prop when action is performed
 */
export async function triggerPropForAction(workspacePath, action, config = DEFAULT_CONFIG) {
    const mapping = mapActionToProp(action, config);
    if (!mapping) {
        return { prop_triggered: false, description: "" };
    }
    const inventory = await loadInventory(workspacePath);
    const prop = inventory.find(p => p.id === mapping.prop_id);
    if (prop) {
        const state = await updateInteractionState(workspacePath, {
            current_prop: prop,
            current_action: prop.animation || "using",
            holding: [prop.id],
        });
        return {
            prop_triggered: true,
            description: getPropDescription(prop.id, config),
        };
    }
    return { prop_triggered: false, description: "" };
}
/**
 * Interact with furniture (sit, lie, use)
 */
export async function interactWithFurniture(workspacePath, location, action) {
    const furniture = await loadFurniture(workspacePath);
    const targetFurniture = findFurnitureByLocation(furniture, location, action);
    if (!targetFurniture) {
        return { success: false, furniture: null, description: "" };
    }
    const state = await updateInteractionState(workspacePath, {
        current_furniture: targetFurniture,
        current_action: targetFurniture.interaction_type || action,
        holding: [],
    });
    const descriptions = {
        sit: `Du sitzt auf ${targetFurniture.name}.`,
        lie: `Du liegst auf ${targetFurniture.name}.`,
        use: `Du nutzt ${targetFurniture.name}.`,
    };
    return {
        success: true,
        furniture: targetFurniture,
        description: descriptions[action] || `Du interagierst mit ${targetFurniture.name}.`,
    };
}
/**
 * Light control functions
 */
export async function setLightState(workspacePath, intensity, color) {
    await updateInteractionState(workspacePath, {
        light_intensity: Math.max(0, Math.min(1, intensity)),
        light_color: color || "#ffffff",
    });
}
/**
 * Toggle light on/off
 */
export async function toggleLight(workspacePath) {
    const statePath = join(workspacePath, "memory", "reality", "interaction_state.json");
    let currentIntensity = 0.8;
    try {
        if (existsSync(statePath)) {
            const state = await readJson(statePath);
            currentIntensity = state?.light_intensity || 0.8;
        }
    }
    catch {
        // Use default
    }
    const newIntensity = currentIntensity > 0 ? 0 : 0.8;
    await setLightState(workspacePath, newIntensity);
    return { intensity: newIntensity };
}
/**
 * Clear current interaction
 */
export async function clearInteraction(workspacePath) {
    await updateInteractionState(workspacePath, {
        current_prop: null,
        current_furniture: null,
        current_action: "standing",
        holding: [],
    });
}
/**
 * Get current interaction for context
 */
export async function getInteractionContext(workspacePath) {
    const statePath = join(workspacePath, "memory", "reality", "interaction_state.json");
    try {
        if (existsSync(statePath)) {
            const state = await readJson(statePath);
            if (!state)
                return "";
            const parts = [];
            if (state.current_furniture) {
                const actionDesc = {
                    sit: "sitting on",
                    lie: "lying on",
                    use: "using",
                    stand: "standing at",
                };
                parts.push(`You are ${actionDesc[state.current_action] || "at"} ${state.current_furniture.name}`);
            }
            if (state.current_prop) {
                parts.push(`holding ${state.current_prop.name}`);
            }
            if (state.light_intensity < 0.3) {
                parts.push("in dim light");
            }
            else if (state.light_intensity > 0.9) {
                parts.push("in bright light");
            }
            return parts.length > 0 ? parts.join(", ") + "." : "";
        }
    }
    catch {
        // Ignore
    }
    return "";
}
/**
 * Non-blocking HTTP notification to dashboard
 */
async function notifyDashboardInteraction(state) {
    try {
        const http = await import("node:http");
        const postData = JSON.stringify({
            action: "interaction_update",
            state: {
                current_action: state.current_action,
                holding: state.holding,
                light_intensity: state.light_intensity,
                light_color: state.light_color,
                furniture: state.current_furniture?.name,
                prop: state.current_prop?.name,
            }
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
//# sourceMappingURL=prop_mapper.js.map