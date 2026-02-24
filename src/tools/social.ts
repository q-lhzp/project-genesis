// ---------------------------------------------------------------------------
// Social Tools - Extracted from index.ts
// ---------------------------------------------------------------------------

import { Type } from "@sinclair/typebox";
import { readJson, writeJson, generateId } from "../utils/persistence.js";
import type { SocialState, SocialEntity, ReputationState } from "../types/index.js";
import type { SimulationPaths, ToolModules } from "../types/paths.js";

interface ToolApi {
  registerTool: (tool: unknown) => void;
}

export function registerSocialTools(api: ToolApi, paths: SimulationPaths, modules: ToolModules): void {
  // Tool: reality_socialize
  api.registerTool({
    name: "reality_socialize",
    description: "Interact with a social contact.",
    parameters: Type.Object({
      action: Type.String({ description: "Action: talk | gift | conflict | apologize | support" }),
      contact: Type.String({ description: "Contact name" }),
      topic: Type.Optional(Type.String({ description: "Conversation topic" })),
    }),
    async execute(_id: string, params: { action: string; contact: string; topic?: string }) {
      if (!modules.social) return { content: [{ type: "text", text: "Social module not enabled." }] };

      const socialState = await readJson<SocialState>(paths.social);
      if (!socialState) return { content: [{ type: "text", text: "social.json not found." }] };

      const entity = socialState.entities.find(e => e.name.toLowerCase() === params.contact.toLowerCase());
      if (!entity) return { content: [{ type: "text", text: `Contact not found: ${params.contact}` }] };

      // Apply bond changes based on action
      const bondChanges: Record<string, number> = {
        talk: 2, gift: 8, conflict: -10, apologize: 5, support: 6
      };
      const trustChanges: Record<string, number> = {
        talk: 1, gift: 3, conflict: -5, apologize: 4, support: 3
      };

      entity.bond = Math.max(-100, Math.min(100, entity.bond + (bondChanges[params.action] ?? 0)));
      entity.trust = Math.max(0, Math.min(100, entity.trust + (trustChanges[params.action] ?? 0)));
      entity.last_interaction = new Date().toISOString();
      entity.interaction_count++;

      await writeJson(paths.social, socialState);

      return { content: [{ type: "text", text: `Interacted with ${entity.name}: ${params.action}` }] };
    },
  });

  // Tool: reality_network
  api.registerTool({
    name: "reality_network",
    description: "Manage social network: search | add | remove | circles.",
    parameters: Type.Object({
      action: Type.String({ description: "Action: search | add | remove | circles" }),
      query: Type.Optional(Type.String({ description: "Search query" })),
      name: Type.Optional(Type.String({ description: "Name for add" })),
      relationship: Type.Optional(Type.String({ description: "Relationship type" })),
    }),
    async execute(_id: string, params: { action: string; query?: string; name?: string; relationship?: string }) {
      if (!modules.social) return { content: [{ type: "text", text: "Social module not enabled." }] };

      const socialState = await readJson<SocialState>(paths.social);
      if (!socialState) return { content: [{ type: "text", text: "social.json not found." }] };

      if (params.action === "search" && params.query) {
        const results = socialState.entities.filter(e =>
          e.name.toLowerCase().includes(params.query!.toLowerCase()) ||
          e.notes.toLowerCase().includes(params.query!.toLowerCase())
        );
        return { content: [{ type: "text", text: `Found: ${results.map(e => e.name).join(", ") || "none"}` }] };
      }

      if (params.action === "add" && params.name) {
        const newEntity: SocialEntity = {
          id: generateId("contact"),
          name: params.name,
          relationship_type: (params.relationship as SocialEntity["relationship_type"]) || "acquaintance",
          bond: 0,
          trust: 10,
          intimacy: 0,
          last_interaction: new Date().toISOString(),
          interaction_count: 0,
          history_summary: `Met ${params.name}.`,
          introduced_at: new Date().toISOString(),
          notes: "",
        };
        socialState.entities.push(newEntity);
        await writeJson(paths.social, socialState);
        return { content: [{ type: "text", text: `Added: ${params.name}` }] };
      }

      return { content: [{ type: "text", text: "Use: reality_network(action: 'search', query: '...')" }] };
    },
  });
}
