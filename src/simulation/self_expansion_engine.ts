// ---------------------------------------------------------------------------
// Self-Expansion Engine - Autonomous Technical Skill Development
// Phase 34: The Developer Mind (Self-Expansion)
// ---------------------------------------------------------------------------

import { readJson, writeJson, appendJsonl } from "../utils/persistence.js";
import { join } from "node:path";
import { existsSync, writeFileSync, mkdirSync } from "node:fs";
import type { Physique } from "../types/index.js";

/**
 * Technical topics that trigger self-expansion
 */
const TECHNICAL_TOPICS = [
  "coding",
  "programming",
  "software",
  "automation",
  "ai",
  "machine learning",
  "cybernetics",
  "development",
  "scripting",
  "algorithms",
  "web development",
  "data science",
  "computer"
];

/**
 * Self-expansion project types
 */
export type ProjectType = "script" | "tool" | "skill_upgrade" | "utility" | "documentation";

/**
 * Project status
 */
export type ProjectStatus = "brainstorm" | "planning" | "implementing" | "completed" | "paused";

/**
 * Self-expansion project definition
 */
export interface SelfDevProject {
  id: string;
  name: string;
  description: string;
  type: ProjectType;
  status: ProjectStatus;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
  topic: string;            // The hobby topic that triggered this
  skillFocus?: string;      // If type is skill_upgrade
  filePath?: string;        // Path to created file
  progress: number;          // 0-100
  logs: string[];           // Development logs
}

/**
 * Self-expansion state
 */
export interface SelfExpansionState {
  isExpanding: boolean;
  currentProject: SelfDevProject | null;
  totalProjectsCreated: number;
  lastExpansionTime: string | null;
  expansionCount: number;
}

/**
 * Default self-expansion state
 */
export const DEFAULT_EXPANSION_STATE: SelfExpansionState = {
  isExpanding: false,
  currentProject: null,
  totalProjectsCreated: 0,
  lastExpansionTime: null,
  expansionCount: 0
};

/**
 * Self-expansion configuration
 */
interface ExpansionConfig {
  energyThreshold: number;      // Min energy to start expansion: 80
  sentimentThreshold: number;    // Min sentiment to trigger: 0.9
  cooldownMinutes: number;     // Cooldown between expansions: 60
  maxActiveProjects: number;    // Max concurrent projects: 1
}

const DEFAULT_CONFIG: ExpansionConfig = {
  energyThreshold: 80,
  sentimentThreshold: 0.9,
  cooldownMinutes: 60,
  maxActiveProjects: 1
};

/**
 * Current expansion state (in-memory)
 */
let expansionState: SelfExpansionState = { ...DEFAULT_EXPANSION_STATE };

/**
 * Load interests data
 */
async function loadInterests(workspacePath: string): Promise<any> {
  const interestsPath = join(workspacePath, "memory", "reality", "interests.json");
  try {
    if (existsSync(interestsPath)) {
      return await readJson(interestsPath);
    }
  } catch (error) {
    console.log(`[self_expansion] Failed to load interests: ${error}`);
  }
  return null;
}

/**
 * Load development manifest
 */
async function loadManifest(workspacePath: string): Promise<{ projects: SelfDevProject[] }> {
  const manifestPath = join(workspacePath, "memory", "development", "manifest.json");
  try {
    if (existsSync(manifestPath)) {
      const data = await readJson<{ projects: SelfDevProject[] }>(manifestPath);
      return data || { projects: [] };
    }
  } catch (error) {
    console.log(`[self_expansion] Failed to load manifest: ${error}`);
  }
  return { projects: [] };
}

/**
 * Save development manifest
 */
async function saveManifest(workspacePath: string, manifest: { projects: SelfDevProject[] }): Promise<void> {
  const manifestPath = join(workspacePath, "memory", "development", "manifest.json");
  await writeJson(manifestPath, manifest);
}

/**
 * Check if a topic is technical
 */
function isTechnicalTopic(topic: string): boolean {
  const lower = topic.toLowerCase();
  return TECHNICAL_TOPICS.some(t => lower.includes(t));
}

/**
 * Find strongest technical interest
 */
function findStrongestTechnicalInterest(interests: any): { topic: string; sentiment: number } | null {
  if (!interests?.hobbies || interests.hobbies.length === 0) {
    return null;
  }

  // Find hobbies with high sentiment that are technical
  const technicalHobbies = interests.hobbies.filter(
    (h: any) => isTechnicalTopic(h.topic) && h.sentiment >= 0.7
  );

  if (technicalHobbies.length === 0) {
    return null;
  }

  // Sort by sentiment descending
  technicalHobbies.sort((a: any, b: any) => b.sentiment - a.sentiment);

  return {
    topic: technicalHobbies[0].topic,
    sentiment: technicalHobbies[0].sentiment
  };
}

/**
 * Generate a unique project ID
 */
function generateProjectId(): string {
  const timestamp = Date.now().toString(36);
  return `proj_${timestamp}`;
}

/**
 * Create a new self-dev project
 */
function createProject(topic: string, type: ProjectType): SelfDevProject {
  const now = new Date().toISOString();

  const projectNames: Record<ProjectType, string[]> = {
    script: ["Automation Script", "Data Processor", "Helper Script", "Utility Tool"],
    tool: ["Custom Tool", "Personal Assistant", "CLI Tool", "Dashboard"],
    skill_upgrade: ["Training Module", "Practice Exercise", "Learning Path", "Skill Drill"],
    utility: ["Configuration Helper", "Setup Script", "Installer", "Manager"],
    documentation: ["Guide", "Tutorial", "Reference", "Notes"]
  };

  const templates = projectNames[type];
  const name = templates[Math.floor(Math.random() * templates.length)];

  return {
    id: generateProjectId(),
    name: `${name}: ${topic}`,
    description: `Autonomous project to explore ${topic}`,
    type,
    status: "brainstorm",
    createdAt: now,
    updatedAt: now,
    topic,
    progress: 0,
    logs: [`[${now}] Project created based on interest in: ${topic}`]
  };
}

/**
 * Create a functional script file
 */
async function createScriptFile(
  workspacePath: string,
  project: SelfDevProject
): Promise<string> {
  const projectsDir = join(workspacePath, "memory", "development", "projects");

  // Ensure directory exists
  if (!existsSync(projectsDir)) {
    mkdirSync(projectsDir, { recursive: true });
  }

  const fileName = `${project.id}.js`;
  const filePath = join(projectsDir, fileName);

  // Generate script content based on topic
  let content = `// Auto-generated by Project Genesis Self-Expansion Engine
// Topic: ${project.topic}
// Created: ${project.createdAt}
// Status: ${project.status}

`;

  // Add topic-specific content
  if (project.topic.toLowerCase().includes("coding") || project.topic.toLowerCase().includes("programming")) {
    content += `/**
 * ${project.name}
 * Generated for: ${project.topic}
 */

function execute() {
  console.log("[${project.name}] Executing...");
  // TODO: Implement logic for ${project.topic}
  return { status: "ok", timestamp: new Date().toISOString() };
}

module.exports = { execute };

// Run if executed directly
if (require.main === module) {
  const result = execute();
  console.log("Result:", result);
}
`;
  } else if (project.topic.toLowerCase().includes("automation")) {
    content += `/**
 * ${project.name}
 * Automation script for: ${project.topic}
 */

const CONFIG = {
  enabled: true,
  interval: 60000, // 1 minute
  topic: "${project.topic}"
};

function run() {
  console.log("[Automation] Running: ${project.name}");
  // TODO: Implement automation logic
}

setInterval(run, CONFIG.interval);

module.exports = { run, CONFIG };
`;
  } else {
    // Generic template
    content += `/**
 * ${project.name}
 * Topic: ${project.topic}
 */

const state = {
  projectId: "${project.id}",
  topic: "${project.topic}",
  created: "${project.createdAt}",
  progress: 0
};

function init() {
  console.log("Initializing:", state.projectId);
}

function update() {
  state.progress = Math.min(100, state.progress + 10);
  console.log("Progress:", state.progress + "%");
}

init();
module.exports = { state, init, update };
`;
  }

  writeFileSync(filePath, content, "utf-8");
  return filePath;
}

/**
 * Update skills.json if project is skill upgrade
 */
async function updateSkills(workspacePath: string, skillName: string): Promise<void> {
  const skillsPath = join(workspacePath, "memory", "reality", "skills.json");

  let skills: any = { skills: {} };
  try {
    if (existsSync(skillsPath)) {
      skills = await readJson(skillsPath) || skills;
    }
  } catch {
    // Use default
  }

  // Initialize if missing
  if (!skills.skills) skills.skills = {};

  // Find matching skill or create new
  const skillKey = Object.keys(skills.skills).find(
    k => k.toLowerCase().includes(skillName.toLowerCase())
  );

  if (skillKey) {
    // Increment existing skill
    skills.skills[skillKey].level = (skills.skills[skillKey].level || 1) + 1;
    skills.skills[skillKey].xp = (skills.skills[skillKey].xp || 0) + 50;
  } else {
    // Add new skill
    skills.skills[skillName] = {
      level: 1,
      xp: 50,
      category: "technical"
    };
  }

  await writeJson(skillsPath, skills);
}

/**
 * Log expansion activity
 */
async function logExpansion(
  workspacePath: string,
  action: string,
  details: string
): Promise<void> {
  const logPath = join(workspacePath, "memory", "genesis_log.jsonl");
  await appendJsonl(logPath, {
    timestamp: new Date().toISOString(),
    type: "self_expansion",
    action,
    details
  });
}

/**
 * Get current expansion state
 */
export function getExpansionState(): SelfExpansionState {
  return { ...expansionState };
}

/**
 * Check if expansion is active
 */
export function isSelfExpanding(): boolean {
  return expansionState.isExpanding;
}

/**
 * Get current project for context
 */
export function getCurrentProject(): SelfDevProject | null {
  return expansionState.currentProject;
}

/**
 * Main process function - call this from tick handler
 */
export async function processSelfExpansion(
  workspacePath: string,
  physique: Physique,
  config: ExpansionConfig = DEFAULT_CONFIG
): Promise<{
  isExpanding: boolean;
  project: SelfDevProject | null;
  newlyStarted: boolean;
}> {
  const now = new Date();

  // Check if already expanding
  if (expansionState.isExpanding && expansionState.currentProject) {
    // Update progress
    expansionState.currentProject.progress = Math.min(
      100,
      expansionState.currentProject.progress + 5
    );
    expansionState.currentProject.updatedAt = now.toISOString();

    // Log progress
    if (expansionState.currentProject.progress % 20 === 0) {
      await logExpansion(
        workspacePath,
        "progress",
        `Project ${expansionState.currentProject.name}: ${expansionState.currentProject.progress}%`
      );
    }

    // Check if completed
    if (expansionState.currentProject.progress >= 100) {
      expansionState.currentProject.status = "completed";
      expansionState.currentProject.completedAt = now.toISOString();

      await logExpansion(
        workspacePath,
        "completed",
        `Project completed: ${expansionState.currentProject.name}`
      );

      // Reset state
      expansionState.isExpanding = false;
      expansionState.currentProject = null;
    }

    // Save state to file
    await saveExpansionState(workspacePath);

    return {
      isExpanding: false,
      project: null,
      newlyStarted: false
    };
  }

  // Check cooldown
  if (expansionState.lastExpansionTime) {
    const lastTime = new Date(expansionState.lastExpansionTime);
    const diffMinutes = (now.getTime() - lastTime.getTime()) / (1000 * 60);
    if (diffMinutes < config.cooldownMinutes) {
      return { isExpanding: false, project: null, newlyStarted: false };
    }
  }

  // Check energy threshold
  if (physique.needs.energy < config.energyThreshold) {
    return { isExpanding: false, project: null, newlyStarted: false };
  }

  // Load interests and find technical topic
  const interests = await loadInterests(workspacePath);
  const technicalInterest = findStrongestTechnicalInterest(interests);

  if (!technicalInterest || technicalInterest.sentiment < config.sentimentThreshold) {
    return { isExpanding: false, project: null, newlyStarted: false };
  }

  // Check manifest for existing projects
  const manifest = await loadManifest(workspacePath);
  const activeProjects = manifest.projects.filter(
    p => p.status !== "completed" && p.status !== "paused"
  );

  if (activeProjects.length >= config.maxActiveProjects) {
    return { isExpanding: false, project: null, newlyStarted: false };
  }

  // Determine project type based on topic
  let projectType: ProjectType = "script";
  if (technicalInterest.topic.toLowerCase().includes("skill")) {
    projectType = "skill_upgrade";
  } else if (technicalInterest.topic.toLowerCase().includes("learn")) {
    projectType = "skill_upgrade";
  } else if (technicalInterest.topic.toLowerCase().includes("document")) {
    projectType = "documentation";
  } else if (technicalInterest.topic.toLowerCase().includes("tool")) {
    projectType = "tool";
  }

  // Create new project
  const newProject = createProject(technicalInterest.topic, projectType);

  // If it's a script/tool, create the file (using type assertion to fix narrowing)
  const pt = projectType as string;
  if (pt === "script" || pt === "tool" || pt === "utility" || pt === "skill_upgrade" || pt === "documentation") {
    const filePath = await createScriptFile(workspacePath, newProject);
    newProject.filePath = filePath;
  }

  // If it's a skill upgrade, update skills
  if (projectType === "skill_upgrade") {
    const skillName = technicalInterest.topic.split(" ")[0];
    await updateSkills(workspacePath, skillName);
  }

  // Add to manifest
  manifest.projects.push(newProject);
  await saveManifest(workspacePath, manifest);

  // Update state
  expansionState.isExpanding = true;
  expansionState.currentProject = newProject;
  expansionState.lastExpansionTime = now.toISOString();
  expansionState.totalProjectsCreated++;
  expansionState.expansionCount++;

  // Save state
  await saveExpansionState(workspacePath);

  // Log creation
  await logExpansion(
    workspacePath,
    "started",
    `New project: ${newProject.name} (${newProject.type})`
  );

  console.log(`[self_expansion] Started project: ${newProject.name}`);

  return {
    isExpanding: true,
    project: newProject,
    newlyStarted: true
  };
}

/**
 * Save expansion state to file
 */
async function saveExpansionState(workspacePath: string): Promise<void> {
  const statePath = join(workspacePath, "memory", "reality", "expansion_state.json");
  await writeJson(statePath, expansionState);
}

/**
 * Load expansion state from file
 */
export async function loadExpansionState(workspacePath: string): Promise<SelfExpansionState> {
  const statePath = join(workspacePath, "memory", "reality", "expansion_state.json");

  try {
    if (existsSync(statePath)) {
      const loaded = await readJson<typeof expansionState>(statePath);
      if (loaded) {
        expansionState = { ...DEFAULT_EXPANSION_STATE, ...loaded };
      }
    }
  } catch (error) {
    console.log(`[self_expansion] Failed to load state: ${error}`);
  }

  return expansionState;
}

/**
 * Get projects summary for UI
 */
export async function getProjectsSummary(workspacePath: string): Promise<{
  total: number;
  completed: number;
  active: { name: string; progress: number; type: string }[];
}> {
  const manifest = await loadManifest(workspacePath);

  const completed = manifest.projects.filter(p => p.status === "completed").length;
  const active = manifest.projects
    .filter(p => p.status !== "completed" && p.status !== "paused")
    .map(p => ({ name: p.name, progress: p.progress, type: p.type }));

  return {
    total: manifest.projects.length,
    completed,
    active
  };
}
