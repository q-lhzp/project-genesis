export * from "./metabolism.js";
export * from "./lifecycle.js";
export * from "./world.js";
export * from "./prop_mapper.js";
export * from "./self_expansion_engine.js";
export * from "./social_engine.js";
export * from "./spatial_engine.js";
export * from "./economy_engine.js";
export * from "./genesis_engine.js";
export * from "./presence_engine.js";
export * from "./hardware_engine.js";
export { getSkillMultiplier, SENSATIONS, getSensation } from "../types/simulation.js";
import type { AgentRole, RoleMapping } from "../types/simulation.js";
export declare function detectAgentRole(agentId: string, roleMapping: RoleMapping | undefined): AgentRole;
export declare function cleanupExpiredMemos(commPath: string, ttlDays: number): Promise<void>;
export declare function logVitalityTelemetry(telDir: string, lifecycle: any, needs: any, location: string): Promise<void>;
export declare function logAgentActivity(telDir: string, agentId: string, role: string, action: string, message: string, meta?: any): Promise<void>;
//# sourceMappingURL=index.d.ts.map