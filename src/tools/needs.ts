// ---------------------------------------------------------------------------
// Needs Tools - Modular implementation for Project Genesis
// ---------------------------------------------------------------------------

import { Type } from "@sinclair/typebox";
import { readJson, writeJson } from "../utils/persistence.js";
import { getSkillMultiplier } from "../simulation/index.js";
import type { Physique, SkillState, Needs, WorldLocation, WardrobeItem } from "../types/index.js";
import type { SimulationPaths, ToolModules } from "../types/paths.js";

interface ToolApi {
  registerTool: (tool: unknown) => void;
}

export function registerNeedsTools(api: ToolApi, paths: SimulationPaths, modules: ToolModules, lang: "de" | "en" = "en") {
  // Tool: reality_needs
  api.registerTool({
    name: "reality_needs",
    description: "Satisfy a biological need. action: toilet | eat | drink | sleep | shower",
    parameters: Type.Object({
      action: Type.String({ description: "Action to perform: toilet | eat | drink | sleep | shower" }),
    }),
    async execute(_id: string, params: { action: string }) {
      const ph = await readJson<Physique>(paths.physique);
      if (!ph) return { content: [{ type: "text", text: "physique.json not found." }] };

      const skillState = modules.skills ? await readJson<SkillState>(paths.skills) : null;
      const cookingMultiplier = getSkillMultiplier(skillState, "cooking", 20);

      const actionMap: Record<string, Partial<Needs>> = {
        toilet: { bladder: 0, bowel: 0 },
        eat: { hunger: 0 },
        drink: { thirst: 0 },
        sleep: { energy: 100, stress: Math.max(0, ph.needs.stress - 30) },
        shower: { hygiene: 0 },
      };

      if (!Object.prototype.hasOwnProperty.call(actionMap, params.action)) {
        return { content: [{ type: "text", text: `Unknown action. Valid: ${Object.keys(actionMap).join(", ")}` }] };
      }

      let changes = actionMap[params.action];
      if (changes && params.action === "eat") {
        const baseHunger = ph.needs.hunger;
        const effectiveReduction = Math.min(100, baseHunger * cookingMultiplier);
        changes = { hunger: Math.max(0, ph.needs.hunger - effectiveReduction) };
      }

      if (changes) Object.assign(ph.needs, changes);
      ph.last_tick = new Date().toISOString();
      await writeJson(paths.physique, ph);

      const msgs: Record<string, Record<string, string>> = {
        toilet: { de: "Erleichterung. Du fuehlst dich wieder frei.", en: "Relief. You feel free again." },
        eat: { de: "Satt. Der Hunger ist gestillt.", en: "Full. The hunger is satisfied." },
        drink: { de: "Erfrischt. Der Durst ist geloescht.", en: "Refreshed. Your thirst is quenched." },
        sleep: { de: "Ausgeruht. Du fuehlst dich energiegeladen.", en: "Rested. You feel energized." },
        shower: { de: "Sauber und frisch. Das fuehlt sich gut an.", en: "Clean and fresh. That feels good." },
      };

      let msg = msgs[params.action]?.[lang] ?? "Done.";
      if (params.action === "eat" && cookingMultiplier > 1) {
        const bonus = Math.round((cookingMultiplier - 1) * 100);
        msg += ` (+${bonus}% ${lang === "de" ? "Kochen-Skill Bonus" : "Cooking skill bonus"})`;
      }

      return { content: [{ type: "text", text: msg }] };
    },
  });

  // Tool: reality_move
  api.registerTool({
    name: "reality_move",
    description: "Move to a different location in the world",
    parameters: Type.Object({
      location: Type.String({ description: "Target location ID or name" }),
    }),
    async execute(_id: string, params: { location: string }) {
      const ph = await readJson<Physique>(paths.physique);
      if (!ph) return { content: [{ type: "text", text: "physique.json not found." }] };

      const world = await readJson<{ locations: WorldLocation[] }>(paths.locations);
      if (world) {
        const valid = world.locations.find(
          (l) => l.id === params.location || l.name.toLowerCase() === params.location.toLowerCase()
        );
        if (!valid) {
          const available = world.locations.map((l) => l.name).join(", ");
          return { content: [{ type: "text", text: lang === "de" ? `Unbekannter Ort. Verfuegbar: ${available}` : `Unknown location. Available: ${available}` }] };
        }
        ph.current_location = valid.name;
      } else {
        ph.current_location = params.location;
      }

      ph.last_tick = new Date().toISOString();
      await writeJson(paths.physique, ph);

      const msg = lang === "de"
        ? `Du bist jetzt in: ${ph.current_location}`
        : `You are now at: ${ph.current_location}`;
      return { content: [{ type: "text", text: msg }] };
    },
  });

  // Tool: reality_dress
  api.registerTool({
    name: "reality_dress",
    description: "Change your current outfit",
    parameters: Type.Object({
      outfit: Type.Array(Type.String(), { description: "List of clothing items to wear" }),
    }),
    async execute(_id: string, params: { outfit: string[] }) {
      const ph = await readJson<Physique>(paths.physique);
      if (!ph) return { content: [{ type: "text", text: "physique.json not found." }] };

      const wardrobe = await readJson<{ inventory?: Record<string, WardrobeItem[]> }>(paths.wardrobe);
      if (wardrobe?.inventory) {
        const allItems = Object.values(wardrobe.inventory).flat();
        const missing = params.outfit.filter(
          (item) => !allItems.some((w) => w.name.toLowerCase() === item.toLowerCase())
        );
        if (missing.length > 0) {
          return { content: [{ type: "text", text: lang === "de" ? `Nicht im Kleiderschrank: ${missing.join(", ")}. Nutze reality_shop zum Einkaufen.` : `Not in wardrobe: ${missing.join(", ")}. Use reality_shop to buy first.` }] };
        }
      }

      ph.current_outfit = params.outfit;
      ph.last_tick = new Date().toISOString();
      await writeJson(paths.physique, ph);

      const msg = lang === "de"
        ? `Outfit gewechselt: ${params.outfit.join(", ")}`
        : `Changed outfit: ${params.outfit.join(", ")}`;
      return { content: [{ type: "text", text: msg }] };
    },
  });
}
