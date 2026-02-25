import type { AgentRole, RoleMapping } from "./simulation.js";
export interface PluginConfig {
    workspacePath: string;
    language: "de" | "en";
    birthDate?: string;
    initialAgeDays?: number;
    initialBalance?: number;
    modules: {
        eros: boolean;
        cycle: boolean;
        dreams: boolean;
        hobbies: boolean;
        economy?: boolean;
        social?: boolean;
        utility?: boolean;
        psychology?: boolean;
        skills?: boolean;
        world?: boolean;
        reputation?: boolean;
        desktop?: boolean;
        legacy?: boolean;
        genesis?: boolean;
        multi_model_optimization?: boolean;
        voice_enabled?: boolean;
        mem0?: {
            enabled?: boolean;
            api_key?: string;
            user_id?: string;
        };
    };
    metabolismRates: Record<string, number>;
    reflexThreshold: number;
    growthContextEntries?: number;
    dreamWindow?: {
        start: number;
        end: number;
    };
    dreamEnergyThreshold?: number;
    evolution?: {
        governance?: string;
        reflection?: {
            routine_batch_size?: number;
            notable_batch_size?: number;
            pivotal_immediate?: boolean;
            min_interval_minutes?: number;
        };
        sources?: {
            conversation?: boolean;
            moltbook?: boolean;
            x?: boolean;
        };
    };
    development?: {
        enabled?: boolean;
        auto_load_approved?: boolean;
    };
    roleMapping?: RoleMapping;
    memoTTL?: number;
}
export declare const TOOL_ACCESS_MATRIX: Record<AgentRole, string[]>;
//# sourceMappingURL=config.d.ts.map