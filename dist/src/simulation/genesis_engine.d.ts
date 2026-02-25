/**
 * Character slot configuration
 */
interface CharacterSlot {
    id: string;
    name: string;
    description: string;
    created_at: string;
    is_active: boolean;
    vrm_path?: string;
}
/**
 * Genesis state
 */
interface GenesisState {
    slots: CharacterSlot[];
    active_slot: string | null;
    last_bootstrap: string | null;
}
/**
 * Bootstrap a new character from a natural language prompt
 * Uses internal LLM to generate complete character state
 */
export declare function bootstrapCharacter(workspacePath: string, name: string, prompt: string): Promise<{
    success: boolean;
    message: string;
    slot?: CharacterSlot;
}>;
/**
 * Activate a character slot
 */
export declare function activateSlot(workspacePath: string, slotName: string, vrmPath?: string): Promise<{
    success: boolean;
    message: string;
}>;
/**
 * Delete a character slot
 */
export declare function deleteSlot(workspacePath: string, slotName: string): Promise<{
    success: boolean;
    message: string;
}>;
/**
 * Get all character slots
 */
export declare function getSlots(workspacePath: string): Promise<CharacterSlot[]>;
/**
 * Get current genesis state
 */
export declare function getGenesisState(workspacePath: string): Promise<GenesisState>;
export {};
//# sourceMappingURL=genesis_engine.d.ts.map