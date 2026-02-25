/**
 * Prop types for 3D attachment
 */
export type PropType = "food" | "drink" | "book" | "device" | "tool" | "other";
/**
 * Prop definition for 3D objects
 */
export interface Prop {
    id: string;
    name: string;
    type: PropType;
    model_path?: string;
    bone_attachment?: string;
    animation?: string;
    description?: string;
}
/**
 * Furniture object definition
 */
export interface Furniture {
    id: string;
    name: string;
    location: string;
    position?: {
        x: number;
        y: number;
        z: number;
    };
    rotation?: {
        x: number;
        y: number;
        z: number;
        w: number;
    };
    scale?: {
        x: number;
        y: number;
        z: number;
    };
    interaction_type?: "sit" | "lie" | "stand" | "use";
    target_bone?: string;
    prop_slot?: string;
}
/**
 * Current interaction state
 */
export interface InteractionState {
    current_prop: Prop | null;
    current_furniture: Furniture | null;
    current_action: string;
    holding: string[];
    light_intensity: number;
    light_color: string;
    last_update: string;
}
/**
 * Default interaction state
 */
export declare const DEFAULT_INTERACTION: InteractionState;
/**
 * Prop mapping configuration
 */
interface PropConfig {
    action_to_prop: Record<string, {
        prop_id: string;
        bone: string;
        animation: string;
    }>;
    prop_descriptions: Record<string, string>;
}
/**
 * Load inventory items
 */
export declare function loadInventory(workspacePath: string): Promise<Prop[]>;
/**
 * Load furniture data
 */
export declare function loadFurniture(workspacePath: string): Promise<Furniture[]>;
/**
 * Map action to prop
 */
export declare function mapActionToProp(action: string, config?: PropConfig): {
    prop_id: string;
    bone: string;
    animation: string;
} | null;
/**
 * Get prop description
 */
export declare function getPropDescription(propId: string, config?: PropConfig): string;
/**
 * Find furniture by location and type
 */
export declare function findFurnitureByLocation(furniture: Furniture[], location: string, interactionType?: "sit" | "lie" | "stand" | "use"): Furniture | null;
/**
 * Update avatar interaction state
 */
export declare function updateInteractionState(workspacePath: string, state: Partial<InteractionState>): Promise<InteractionState>;
/**
 * Trigger prop when action is performed
 */
export declare function triggerPropForAction(workspacePath: string, action: string, config?: PropConfig): Promise<{
    prop_triggered: boolean;
    description: string;
}>;
/**
 * Interact with furniture (sit, lie, use)
 */
export declare function interactWithFurniture(workspacePath: string, location: string, action: "sit" | "lie" | "use"): Promise<{
    success: boolean;
    furniture: Furniture | null;
    description: string;
}>;
/**
 * Light control functions
 */
export declare function setLightState(workspacePath: string, intensity: number, color?: string): Promise<void>;
/**
 * Toggle light on/off
 */
export declare function toggleLight(workspacePath: string): Promise<{
    intensity: number;
}>;
/**
 * Clear current interaction
 */
export declare function clearInteraction(workspacePath: string): Promise<void>;
/**
 * Get current interaction for context
 */
export declare function getInteractionContext(workspacePath: string): Promise<string>;
export {};
//# sourceMappingURL=prop_mapper.d.ts.map