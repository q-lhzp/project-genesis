// ---------------------------------------------------------------------------
// Central Paths Interface - Used by all tool modules
// ---------------------------------------------------------------------------

export interface SimulationPaths {
  // Core
  physique: string;
  wardrobe: string;
  locations: string;
  interests: string;
  diary: string;
  experiences: string;

  // Lifecycle
  lifecycle: string;
  telemetry: string;
  backups: string;

  // Internal Communication (for memos)
  internalComm: string;

  // Social
  social: string;
  socialTelemetry: string;
  reputation: string;
  reputationEvents: string;
  socialEvents: string;

  // Economy
  finances: string;
  economyTelemetry: string;
  skills: string;
  skillsConfig: string;

  // Psychology
  psych: string;
  psychology: string;

  // World
  world: string;
  worldNews: string;
  newsEvents: string;

  // Dreams & Hobbies
  dreams: string;
  dreamState: string;
  hobbies: string;

  // Cycle
  cycle: string;
  cycleProfile: string;

  // Identity & Growth
  identity: string;
  emotions: string;
  growth: string;
  desires: string;

  // Interior & Inventory
  interior: string;
  inventory: string;
  media: string;

  // Development
  devManifest: string;
  devProjects: string;

  // Soul & Genesis
  soulState: string;
  pendingProposals: string;
  genesisLog: string;

  // Vault
  vaultState: string;

  // v5.1.0 Centralized Config & State
  simulationConfig: string;
  identityState: string;
  hardwareState: string;
  presenceState: string;
  economyState: string;
}

export interface ToolModules {
  eros: boolean;
  cycle: boolean;
  dreams: boolean;
  hobbies: boolean;
  economy: boolean;
  social: boolean;
  psychology: boolean;
  skills: boolean;
  world: boolean;
  reputation: boolean;
  desktop: boolean;
  utility: boolean;
  legacy: boolean;
  genesis: boolean;
  multi_model_optimization: boolean;
  voice_enabled: boolean;
  mem0: {
    enabled: boolean;
    apiKey: string;
    userId: string;
  };
}
