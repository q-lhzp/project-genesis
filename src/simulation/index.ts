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

// Re-export helper functions from types
export { getSkillMultiplier, SENSATIONS, getSensation } from "../types/simulation.js";

import { readJson, appendJsonl } from "../utils/persistence.js";
import { join } from "node:path";
import type { AgentRole, RoleMapping } from "../types/simulation.js";

export function detectAgentRole(agentId: string, roleMapping: RoleMapping | undefined): AgentRole {
  if (!roleMapping) return "persona";
  const lowerId = agentId.toLowerCase();
  const validRoles = ["persona", "analyst", "developer", "limbic", "world_engine"];
  for (const [role, patterns] of Object.entries(roleMapping)) {
    if (validRoles.includes(role)) {
      if (patterns?.some(p => lowerId === p.toLowerCase() || lowerId.includes(p.toLowerCase()))) {
        return role as AgentRole;
      }
    }
  }
  return "persona";
}

export async function cleanupExpiredMemos(commPath: string, ttlDays: number) {
  const comm = await readJson<any>(commPath);
  if (!comm?.memos) return;
  const now = new Date().getTime();
  const filtered = comm.memos.filter((m: any) => {
    const expiresAt = new Date(m.expires_at).getTime();
    return expiresAt > now;
  });
  if (filtered.length !== comm.memos.length) {
    comm.memos = filtered;
    comm.last_cleanup = new Date().toISOString();
    // await writeJson(commPath, comm); // Careful with concurrent writes
  }
}

export async function logVitalityTelemetry(telDir: string, lifecycle: any, needs: any, location: string) {
  const date = new Date().toISOString().slice(0, 10);
  const logPath = join(telDir, `vitality_${date}.jsonl`);
  const entry = {
    timestamp: new Date().toISOString(),
    age_days: lifecycle.biological_age_days,
    life_stage: lifecycle.life_stage,
    needs,
    location
  };
  await appendJsonl(logPath, entry);
}

export async function logAgentActivity(telDir: string, agentId: string, role: string, action: string, message: string, meta: any = {}) {
  const date = new Date().toISOString().slice(0, 10);
  const logPath = join(telDir, `activity_${date}.jsonl`);
  const entry = {
    timestamp: new Date().toISOString(),
    agent_id: agentId,
    role,
    action,
    message,
    ...meta
  };
  await appendJsonl(logPath, entry);
}
