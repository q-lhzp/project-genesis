// ---------------------------------------------------------------------------
// Social Tools - Extracted from index.ts
// ---------------------------------------------------------------------------

import { Type } from "@sinclair/typebox";
import { readJson, writeJson, generateId } from "../utils/persistence.js";
import type { SocialState, SocialEntity, ReputationState } from "../types/index.js";
import type { SimulationPaths, ToolModules } from "../types/paths.js";
import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { execFile } from "node:child_process";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

// Get directory paths
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const PROJECT_ROOT = join(__dirname, "..", "..");
const MEMORY_DIR = join(PROJECT_ROOT, "memory", "reality");

export function registerSocialTools(api: OpenClawPluginApi, paths: SimulationPaths, modules: ToolModules): void {
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

  // Tool: reality_generate_npc_portrait (Visual Lab)
  api.registerTool({
    name: "reality_generate_npc_portrait",
    description: "Generate a portrait for an NPC contact using AI image generation.",
    parameters: Type.Object({
      name: Type.String({ description: "NPC name (must exist in social network)" }),
      style: Type.Optional(Type.String({ description: "Style: photorealistic | anime | cyberpunk | illustration" })),
      regenerate: Type.Optional(Type.Boolean({ description: "Regenerate even if portrait exists" })),
    }),
    async execute(_id: string, params: { name: string; style?: string; regenerate?: boolean }) {
      if (!modules.social) return { content: [{ type: "text", text: "Social module not enabled." }] };

      const socialState = await readJson<SocialState>(paths.social);
      if (!socialState) return { content: [{ type: "text", text: "social.json not found." }] };

      const entity = socialState.entities.find(e => e.name.toLowerCase() === params.name.toLowerCase());
      if (!entity) return { content: [{ type: "text", text: `Contact not found: ${params.name}` }] };

      // Check if portrait already exists
      if (!params.regenerate && entity.portrait_url) {
        return { content: [{ type: "text", text: `Portrait already exists for ${entity.name}: ${entity.portrait_url}` }] };
      }

      // Build prompt from visual_description or generate default
      let prompt = entity.visual_description || `A portrait of ${entity.name}, ${entity.relationship_type}`;
      const style = (params.style || entity.portrait_style || "photorealistic") as string;

      // Add style to prompt
      const stylePrompts: Record<string, string> = {
        photorealistic: "photorealistic portrait, 8k, professional lighting",
        anime: "anime style illustration, manga, vibrant colors",
        cyberpunk: "cyberpunk style, neon lights, futuristic",
        illustration: "digital illustration, artistic, colorful"
      };
      prompt += `, ${stylePrompts[style] || stylePrompts.photorealistic}`;

      // Generate image using generate_image.py
      const timestamp = Date.now();
      const portraitsDir = paths.portraits;

      // Ensure portraits directory exists
      const fs = await import("node:fs/promises");
      await fs.mkdir(portraitsDir, { recursive: true });

      const outputPath = join(portraitsDir, `${entity.id}_${timestamp}.png`);
      const scriptPath = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "skills", "soul-evolution", "tools", "vision", "generate_image.py");

      return new Promise((resolve) => {
        execFile(
          "python3",
          [
            scriptPath,
            "--prompt", prompt,
            "--output", outputPath,
            "--provider", "auto"
          ],
          { timeout: 120000 },
          (error, stdout, stderr) => {
            if (error) {
              resolve({ content: [{ type: "text", text: `Image generation failed: ${error.message}` }] });
              return;
            }

            // Parse output for image path
            const match = stdout.match(/MEDIA: (.+)/);
            const imagePath = match ? match[1] : outputPath;

            // Update entity with portrait info
            entity.portrait_url = imagePath;
            entity.face_template_id = entity.id;
            entity.generated_at = new Date().toISOString();
            entity.portrait_style = style as SocialEntity["portrait_style"];

            // Save state
            writeJson(paths.social, socialState).then(() => {
              resolve({
                content: [
                  { type: "text", text: `Portrait generated for ${entity.name}` },
                  { type: "text", text: `Style: ${style}` },
                  { type: "text", text: `Path: ${imagePath}` }
                ]
              });
            });
          }
        );
      });
    },
  });
}
