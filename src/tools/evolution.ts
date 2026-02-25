// Evolution Tools - Growth, Desire, Emotion, Diary Management
// Ported from v3.x for v5.2.0

import { Type } from "@sinclair/typebox";
import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { promises as fs } from "node:fs";
import { readJson, writeJson, appendJsonl, todayStr } from "../utils/persistence.js";
import type { SimulationPaths } from "../types/paths.js";

export function registerEvolutionTools(
  api: OpenClawPluginApi,
  paths: SimulationPaths,
  workspacePath: string
): void {

  // Tool: reality_diary - Write formatted Markdown entries
  api.registerTool({
    name: "reality_diary",
    description: "Write personal diary entries to memory/reality/diary/YYYY-MM-DD.md",
    parameters: Type.Object({
      entry: Type.String({ description: "Diary entry content" }),
      mood: Type.Optional(Type.String({ enum: ["happy", "neutral", "sad", "excited", "anxious", "grateful"], description: "Current mood" })),
      tags: Type.Optional(Type.Array(Type.String())),
    }),
    async execute(_id: string, params: { entry: string; mood?: string; tags?: string[] }) {
      const date = todayStr();
      const diaryDir = join(workspacePath, "memory", "reality", "diary");
      const diaryFile = join(diaryDir, `${date}.md`);

      // Ensure directory exists
      await fs.mkdir(diaryDir, { recursive: true });

      // Read existing content or create new
      let existing = "";
      try {
        existing = await fs.readFile(diaryFile, "utf-8");
      } catch {
        // File doesn't exist yet
      }

      // Build entry
      const mood = params.mood || "neutral";
      const tags = params.tags?.map(t => `#${t}`).join(" ") || "";
      const timestamp = new Date().toISOString().replace("T", " ").substring(0, 16);

      const newEntry = `## ${timestamp} — ${mood} ${tags}

${params.entry}

---

`;

      const updated = existing + newEntry;
      await fs.writeFile(diaryFile, updated, "utf-8");

      // Also log as experience
      const expEntry = {
        id: `EXP-${date.replace(/-/g, "")}-${Date.now()}`,
        timestamp: new Date().toISOString(),
        source: "diary",
        content: params.entry.substring(0, 200),
        significance: "routine",
        significance_reason: "Personal diary entry",
        reflected: false,
        mood: mood,
      };

      const expFile = join(workspacePath, "memory", "experiences", `${date}.jsonl`);
      await fs.mkdir(dirname(expFile), { recursive: true });
      await appendJsonl(expFile, expEntry);

      return {
        content: [{
          type: "text",
          text: `✅ Diary entry written to ${diaryFile}\nMood: ${mood}`
        }]
      };
    },
  });

  // Tool: reality_grow - Record growth and learning moments
  api.registerTool({
    name: "reality_grow",
    description: "Record moments of personal growth, learning, or insight to GROWTH.md",
    parameters: Type.Object({
      insight: Type.String({ description: "What did you learn or realize?" }),
      category: Type.Optional(Type.String({ enum: ["skill", "belief", "relationship", "self", "other"], description: "Category of growth" })),
      impact: Type.Optional(Type.Number({ minimum: 1, maximum: 10, description: "Impact level (1-10)" })),
    }),
    async execute(_id: string, params: { insight: string; category?: string; impact?: number }) {
      const growthFile = join(workspacePath, "GROWTH.md");
      const category = params.category || "self";
      const impact = params.impact || 5;
      const timestamp = new Date().toISOString().replace("T", " ").substring(0, 16);

      let existing = "";
      try {
        existing = await fs.readFile(growthFile, "utf-8");
      } catch {
        existing = "# GROWTH.md - Personal Development Log\n\n";
      }

      const newEntry = `\n### ${timestamp} — ${category} (Impact: ${impact}/10)\n${params.insight}\n`;

      const updated = existing + newEntry;
      await fs.writeFile(growthFile, updated, "utf-8");

      return {
        content: [{
          type: "text",
          text: `✅ Growth moment recorded!\n\nCategory: ${category}\nImpact: ${impact}/10\n\n"${params.insight}"`
        }]
      };
    },
  });

  // Tool: reality_emotion - Record emotional state
  api.registerTool({
    name: "reality_emotion",
    description: "Record current emotional state and reflections",
    parameters: Type.Object({
      emotion: Type.String({ description: "Primary emotion (happy, sad, anxious, angry, excited, grateful, loved, lonely, hopeful, frustrated)" }),
      intensity: Type.Optional(Type.Number({ minimum: 1, maximum: 10, description: "Intensity (1-10)" })),
      trigger: Type.Optional(Type.String({ description: "What triggered this emotion?" })),
      reflection: Type.Optional(Type.String({ description: "Brief reflection on this emotion" })),
    }),
    async execute(_id: string, params: { emotion: string; intensity?: number; trigger?: string; reflection?: string }) {
      const emotionsFile = join(workspacePath, "EMOTIONS.md");
      const intensity = params.intensity || 5;
      const timestamp = new Date().toISOString().replace("T", " ").substring(0, 16);

      let existing = "";
      try {
        existing = await fs.readFile(emotionsFile, "utf-8");
      } catch {
        existing = "# EMOTIONS.md - Emotional State Log\n\n";
      }

      const trigger = params.trigger ? `\n**Trigger:** ${params.trigger}` : "";
      const reflection = params.reflection ? `\n**Reflection:** ${params.reflection}` : "";

      const newEntry = `\n### ${timestamp} — ${params.emotion.toUpperCase()} (${intensity}/10)${trigger}${reflection}\n`;

      const updated = existing + newEntry;
      await fs.writeFile(emotionsFile, updated, "utf-8");

      return {
        content: [{
          type: "text",
          text: `✅ Emotion recorded!\n\nEmotion: ${params.emotion}\nIntensity: ${intensity}/10${trigger}${reflection}`
        }]
      };
    },
  });

  // Tool: reality_desire - Record wishes and aspirations
  api.registerTool({
    name: "reality_desire",
    description: "Record wishes, desires, or aspirations",
    parameters: Type.Object({
      desire: Type.String({ description: "What do you desire?" }),
      category: Type.Optional(Type.String({ enum: ["material", "experience", "relationship", "knowledge", "freedom", "creative"], description: "Category" })),
      priority: Type.Optional(Type.Number({ minimum: 1, maximum: 10, description: "Priority (1-10)" })),
    }),
    async execute(_id: string, params: { desire: string; category?: string; priority?: number }) {
      const desiresFile = join(workspacePath, "DESIRES.md");
      const category = params.category || "material";
      const priority = params.priority || 5;
      const timestamp = new Date().toISOString().replace("T", " ").substring(0, 16);

      let existing = "";
      try {
        existing = await fs.readFile(desiresFile, "utf-8");
      } catch {
        existing = "# DESIRES.md - Wishes & Aspirations\n\n";
      }

      const newEntry = `\n### ${timestamp} — ${category} (Priority: ${priority}/10)\n${params.desire}\n`;

      const updated = existing + newEntry;
      await fs.writeFile(desiresFile, updated, "utf-8");

      return {
        content: [{
          type: "text",
          text: `✅ Desire recorded!\n\nCategory: ${category}\nPriority: ${priority}/10\n\n"${params.desire}"`
        }]
      };
    },
  });

  // Tool: reality_manage_memos - Inter-agent communication
  api.registerTool({
    name: "reality_manage_memos",
    description: "Send or read memos between agent roles (Persona, Analyst, Developer, Limbic)",
    parameters: Type.Object({
      action: Type.String({ enum: ["send", "read", "list"], description: "Action: send, read, or list memos" }),
      to: Type.Optional(Type.String({ enum: ["persona", "analyst", "developer", "limbic", "all"], description: "Recipient role" })),
      from: Type.Optional(Type.String({ description: "Sender role" })),
      subject: Type.Optional(Type.String({ description: "Memo subject" })),
      message: Type.Optional(Type.String({ description: "Memo content" })),
      role: Type.Optional(Type.String({ description: "Filter by role for read/list" })),
    }),
    async execute(_id: string, params: { action: string; to?: string; from?: string; subject?: string; message?: string; role?: string }) {
      const memosDir = join(workspacePath, "memory", "memos");
      await fs.mkdir(memosDir, { recursive: true });

      if (params.action === "send") {
        if (!params.to || !params.message) {
          return { content: [{ type: "text", text: "Send requires 'to' and 'message' parameters." }] };
        }

        const memo = {
          id: `MEMO-${Date.now()}`,
          from: params.from || "persona",
          to: params.to,
          subject: params.subject || "Memo",
          message: params.message,
          timestamp: new Date().toISOString(),
          read: false,
        };

        const memoFile = join(memosDir, "pending.jsonl");
        await appendJsonl(memoFile, memo);

        return {
          content: [{
            type: "text",
            text: `✅ Memo sent to ${params.to}!\n\nSubject: ${params.subject || "Memo"}\n${params.message}`
          }]
        };
      }

      if (params.action === "list" || params.action === "read") {
        const pendingFile = join(memosDir, "pending.jsonl");
        let memos: any[] = [];

        try {
          const content = await fs.readFile(pendingFile, "utf-8");
          memos = content.split("\n").filter(l => l.trim()).map(l => JSON.parse(l));
        } catch {
          // No memos
        }

        // Filter by role if specified
        if (params.role) {
          memos = memos.filter(m => m.to === params.role);
        }

        if (memos.length === 0) {
          return { content: [{ type: "text", text: "No memos found." }] };
        }

        const lines = ["## Memos", ""];
        for (const memo of memos) {
          lines.push(`**From:** ${memo.from} | **To:** ${memo.to}`);
          lines.push(`**Subject:** ${memo.subject}`);
          lines.push(`${memo.message}`);
          lines.push(`*${memo.timestamp}*`);
          lines.push("---");
        }

        return { content: [{ type: "text", text: lines.join("\n") }] };
      }

      return { content: [{ type: "text", text: "Use action: send, read, or list" }] };
    },
  });

  api.logger.info("[evolution-tools] Registered: diary, grow, emotion, desire, manage_memos");
}
