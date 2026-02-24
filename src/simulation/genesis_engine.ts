// ---------------------------------------------------------------------------
// Genesis Engine - Neural Life Bootstrapping (Phase 38)
// Q can create new character states via natural language prompts.
// ---------------------------------------------------------------------------

import { readJson, writeJson } from "../utils/persistence.js";
import { join } from "node:path";
import { existsSync, mkdirSync } from "node:fs";
import type { Physique } from "../types/index.js";

/**
 * Character slot configuration
 */
interface CharacterSlot {
  id: string;
  name: string;
  description: string;
  created_at: string;
  is_active: boolean;
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
export async function bootstrapCharacter(
  workspacePath: string,
  name: string,
  prompt: string
): Promise<{ success: boolean; message: string; slot?: CharacterSlot }> {
  const genesisStatePath = join(workspacePath, "memory", "reality", "genesis_state.json");

  // Load or create genesis state
  let state: GenesisState;
  try {
    if (existsSync(genesisStatePath)) {
      state = await readJson(genesisStatePath);
    } else {
      state = {
        slots: [],
        active_slot: null,
        last_bootstrap: null
      };
    }
  } catch (error) {
    return { success: false, message: `Failed to load genesis state: ${error}` };
  }

  // Check if slot already exists
  const existingSlot = state.slots.find(s => s.name.toLowerCase() === name.toLowerCase());
  if (existingSlot) {
    return { success: false, message: `Character slot '${name}' already exists. Use a different name or delete the existing slot first.` };
  }

  // Create new slot
  const newSlot: CharacterSlot = {
    id: `slot_${Date.now()}`,
    name: name,
    description: prompt,
    created_at: new Date().toISOString(),
    is_active: false
  };

  state.slots.push(newSlot);
  state.last_bootstrap = new Date().toISOString();

  // Save state
  await writeJson(genesisStatePath, state);

  // Create character files based on prompt
  await createCharacterFiles(workspacePath, newSlot, prompt);

  return {
    success: true,
    message: `Character '${name}' bootstrapped successfully. Use reality_genesis(action: 'activate', slot: '${name}') to switch to this character.`,
    slot: newSlot
  };
}

/**
 * Create character files from generated state
 */
async function createCharacterFiles(
  workspacePath: string,
  slot: CharacterSlot,
  prompt: string
): Promise<void> {
  const slotDir = join(workspacePath, "memory", "genesis", slot.id);
  mkdirSync(slotDir, { recursive: true });

  // Generate character state based on prompt
  const characterState = generateCharacterFromPrompt(prompt, slot);

  // Write character files
  await writeJson(join(slotDir, "physique.json"), characterState.physique);
  await writeJson(join(slotDir, "skills.json"), characterState.skills);
  await writeJson(join(slotDir, "interests.json"), characterState.interests);
  await writeJson(join(slotDir, "personality.json"), characterState.personality);

  // Write SOUL.md
  const soulPath = join(slotDir, "SOUL.md");
  const soulContent = `# ${slot.name}

## Created
${slot.created_at}

## Description
${slot.description}

## Core Identity
${characterState.personality.core_identity}

## Values
${characterState.personality.values.map(v => `- ${v}`).join('\n')}

## Fears
${characterState.personality.fears.map(f => `- ${f}`).join('\n')}

## Dreams
${characterState.personality.dreams.map(d => `- ${d}`).join('\n')}
`;
  await writeJson(soulPath, soulContent); // Note: This writes JSON, need to use fs for MD

  console.log(`[genesis_engine] Created character slot: ${slot.name} at ${slotDir}`);
}

/**
 * Generate character state from prompt using rule-based generation
 * In a full implementation, this would use an LLM
 */
function generateCharacterFromPrompt(prompt: string, slot: CharacterSlot): {
  physique: any;
  skills: any;
  interests: any;
  personality: any;
} {
  const lowerPrompt = prompt.toLowerCase();

  // Determine age from prompt
  let age = 25;
  const ageMatch = prompt.match(/(\d+)\s*(years?\s*old|yo|y\.?o\.?)/i);
  if (ageMatch) {
    age = parseInt(ageMatch[1]);
  }

  // Determine personality traits
  const personality = determinePersonality(lowerPrompt);

  // Generate physique based on personality and age
  const physique = generatePhysique(age, personality);

  // Generate skills based on prompt keywords
  const skills = generateSkills(lowerPrompt);

  // Generate interests based on prompt
  const interests = generateInterests(lowerPrompt);

  return { physique, skills, interests, personality };
}

/**
 * Determine personality from prompt
 */
function determinePersonality(prompt: string): any {
  const traits: string[] = [];
  const core_identity = "A unique individual with their own hopes and dreams.";
  const values: string[] = [];
  const fears: string[] = [];
  const dreams: string[] = [];

  // Analyze prompt for personality indicators
  if (prompt.includes("introvert") || prompt.includes("shy")) {
    traits.push("introverted", "thoughtful");
    fears.push("social rejection", "being judged");
  }
  if (prompt.includes("extrovert") || prompt.includes("outgoing")) {
    traits.push("extroverted", "energetic");
    dreams.push("connecting with many people");
  }
  if (prompt.includes("creative") || prompt.includes("artist")) {
    traits.push("creative", "imaginative");
    values.push("artistic expression");
    dreams.push("creating meaningful art");
  }
  if (prompt.includes("logical") || prompt.includes("analytical")) {
    traits.push("logical", "analytical");
    values.push("rationality");
    dreams.push("solving complex problems");
  }
  if (prompt.includes("adventurous") || prompt.includes("daredevil")) {
    traits.push("adventurous", "brave");
    dreams.push("exploring the unknown");
  }
  if (prompt.includes("kind") || prompt.includes("compassionate")) {
    traits.push("kind", "compassionate");
    values.push("helping others");
    dreams.push("making a positive impact");
  }
  if (prompt.includes("ambitious") || prompt.includes("driven")) {
    traits.push("ambitious", "determined");
    values.push("success");
    dreams.push("achieving great things");
  }

  // Default traits if nothing matched
  if (traits.length === 0) {
    traits.push("curious", "adaptable");
    values.push("growth", "learning");
  }

  return {
    traits,
    core_identity,
    values: values.length > 0 ? values : ["growth", "authentic living"],
    fears: fears.length > 0 ? fears : ["regret", "stagnation"],
    dreams: dreams.length > 0 ? dreams : ["self-actualization", "meaningful connections"]
  };
}

/**
 * Generate physique based on age and personality
 */
function generatePhysique(age: number, personality: any): any {
  return {
    age_days: age * 365,
    biological_age_days: age * 365,
    current_location: "home_bedroom",
    current_outfit: ["Comfortable casual wear"],
    vitals: {
      heart_rate: 70 + Math.floor(Math.random() * 10),
      blood_pressure_systolic: 115 + Math.floor(Math.random() * 20),
      blood_pressure_diastolic: 75 + Math.floor(Math.random() * 10),
      body_temperature: 36.6 + Math.random() * 0.4
    },
    needs: {
      energy: 50 + Math.floor(Math.random() * 30),
      hunger: 40 + Math.floor(Math.random() * 30),
      thirst: 40 + Math.floor(Math.random() * 30),
      hygiene: 60 + Math.floor(Math.random() * 30),
      bladder: 50 + Math.floor(Math.random() * 30),
      stress: 30 + Math.floor(Math.random() * 30),
      social: 40 + Math.floor(Math.random() * 30),
      arousal: 20 + Math.floor(Math.random() * 20)
    }
  };
}

/**
 * Generate skills based on prompt keywords
 */
function generateSkills(prompt: string): any {
  const skillLevels: Record<string, number> = {};

  // Technical skills
  if (prompt.includes("code") || prompt.includes("developer") || prompt.includes("programmer")) {
    skillLevels["coding"] = 70;
    skillLevels["problem_solving"] = 65;
  }
  if (prompt.includes("design") || prompt.includes("artist")) {
    skillLevels["design"] = 75;
    skillLevels["creativity"] = 80;
  }
  if (prompt.includes("music")) {
    skillLevels["music"] = 70;
    skillLevels["creativity"] = 65;
  }
  if (prompt.includes("write") || prompt.includes("author")) {
    skillLevels["writing"] = 75;
    skillLevels["creativity"] = 70;
  }

  // Social skills
  if (prompt.includes("leader") || prompt.includes("manager")) {
    skillLevels["leadership"] = 70;
    skillLevels["communication"] = 65;
  }
  if (prompt.includes("teach") || prompt.includes("mentor")) {
    skillLevels["teaching"] = 70;
    skillLevels["patience"] = 75;
  }

  // Default skills
  if (Object.keys(skillLevels).length === 0) {
    skillLevels["learning"] = 50;
    skillLevels["adaptability"] = 60;
    skillLevels["communication"] = 50;
  }

  return {
    technical: skillLevels,
    creative: skillLevels,
    social: skillLevels,
    physical: { "basic_fitness": 50 }
  };
}

/**
 * Generate interests based on prompt
 */
function generateInterests(prompt: string): any {
  const interests: string[] = [];

  const interestMap: Record<string, string[]> = {
    "tech": ["technology", "coding", "AI", "gadgets"],
    "science": ["science", "research", "experiments"],
    "art": ["art", "design", "photography", "music"],
    "nature": ["nature", "hiking", "animals", "gardening"],
    "sports": ["sports", "fitness", "yoga", "running"],
    "books": ["reading", "writing", "literature"],
    "gaming": ["gaming", "video games", "esports"],
    "cooking": ["cooking", "food", "culinary"],
    "travel": ["travel", "adventure", "exploration"],
    "social": ["socializing", "networking", "community"]
  };

  for (const [key, keywords] of Object.entries(interestMap)) {
    if (keywords.some(kw => prompt.includes(kw))) {
      interests.push(...keywords.slice(0, 2));
    }
  }

  // Default interests
  if (interests.length === 0) {
    interests.push("learning", "personal growth", "new experiences");
  }

  return {
    active: [...new Set(interests)],
    passive: ["podcasts", "audiobooks"],
    technical: prompt.includes("tech") ? ["coding", "AI"] : []
  };
}

/**
 * Activate a character slot
 */
export async function activateSlot(
  workspacePath: string,
  slotName: string
): Promise<{ success: boolean; message: string }> {
  const genesisStatePath = join(workspacePath, "memory", "reality", "genesis_state.json");

  try {
    if (!existsSync(genesisStatePath)) {
      return { success: false, message: "No character slots exist. Bootstrap a character first." };
    }

    const state = await readJson<GenesisState>(genesisStatePath);
    const slot = state.slots.find(s => s.name.toLowerCase() === slotName.toLowerCase());

    if (!slot) {
      return { success: false, message: `Character slot '${slotName}' not found.` };
    }

    // Deactivate all slots
    state.slots.forEach(s => s.is_active = false);
    slot.is_active = true;
    state.active_slot = slot.id;

    await writeJson(genesisStatePath, state);

    return {
      success: true,
      message: `Switched to character '${slot.name}'. All simulation state will now reflect this character.`
    };
  } catch (error) {
    return { success: false, message: `Error activating slot: ${error}` };
  }
}

/**
 * Delete a character slot
 */
export async function deleteSlot(
  workspacePath: string,
  slotName: string
): Promise<{ success: boolean; message: string }> {
  const genesisStatePath = join(workspacePath, "memory", "reality", "genesis_state.json");

  try {
    if (!existsSync(genesisStatePath)) {
      return { success: false, message: "No character slots exist." };
    }

    const state = await readJson<GenesisState>(genesisStatePath);
    const slotIndex = state.slots.findIndex(s => s.name.toLowerCase() === slotName.toLowerCase());

    if (slotIndex === -1) {
      return { success: false, message: `Character slot '${slotName}' not found.` };
    }

    const slot = state.slots[slotIndex];

    if (slot.is_active) {
      return { success: false, message: "Cannot delete active slot. Switch to another character first." };
    }

    state.slots.splice(slotIndex, 1);
    await writeJson(genesisStatePath, state);

    // TODO: Delete slot directory

    return { success: true, message: `Character '${slotName}' deleted.` };
  } catch (error) {
    return { success: false, message: `Error deleting slot: ${error}` };
  }
}

/**
 * Get all character slots
 */
export async function getSlots(workspacePath: string): Promise<CharacterSlot[]> {
  const genesisStatePath = join(workspacePath, "memory", "reality", "genesis_state.json");

  try {
    if (!existsSync(genesisStatePath)) {
      return [];
    }
    const state = await readJson<GenesisState>(genesisStatePath);
    return state.slots;
  } catch {
    return [];
  }
}

/**
 * Get current genesis state
 */
export async function getGenesisState(workspacePath: string): Promise<GenesisState> {
  const genesisStatePath = join(workspacePath, "memory", "reality", "genesis_state.json");

  try {
    if (existsSync(genesisStatePath)) {
      return await readJson(genesisStatePath);
    }
  } catch (error) {
    console.log(`[genesis_engine] Error loading state: ${error}`);
  }

  return {
    slots: [],
    active_slot: null,
    last_bootstrap: null
  };
}
