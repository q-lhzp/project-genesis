// ---------------------------------------------------------------------------
// Configuration Types - Extracted from index.ts
// ---------------------------------------------------------------------------

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
  dreamWindow?: { start: number; end: number };
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

// Tool access matrix
export const TOOL_ACCESS_MATRIX: Record<AgentRole, string[]> = {
  persona: [
    "reality_needs", "reality_move", "reality_dress", "reality_shop",
    "reality_diary", "reality_pleasure", "reality_cycle", "reality_emotion",
    "reality_desire", "reality_hobby", "reality_dream",
    "reality_socialize", "reality_network",
    "reality_interior", "reality_inventory",
    "reality_manage_memos",
    "reality_browse",
    "reality_camera",
    "reality_vision_analyze"
  ],
  analyst: [
    "reality_job_market", "reality_work",
    "reality_override", "reality_inject_event", "reality_export_research_data",
    "reality_socialize", "reality_network",
    "reality_develop", "reality_review_project",
    "soul_evolution_pipeline", "soul_evolution_propose", "soul_evolution_reflect",
    "soul_evolution_govern", "soul_evolution_apply",
    "reality_manage_memos",
    "reality_genesis",
    "reality_profile",
    "reality_camera",
    "reality_vision_analyze"
  ],
  developer: [
    "reality_develop",
    "reality_manage_memos"
  ],
  limbic: [
    "reality_needs", "reality_move", "reality_dress",
    "reality_emotion", "reality_desire", "reality_cycle",
    "reality_socialize", "reality_network",
    "reality_manage_memos"
  ],
  world_engine: [
    "reality_cycle",
    "reality_override",
    "reality_inject_event",
    "reality_manage_memos",
    "reality_news"
  ]
};
