// ---------------------------------------------------------------------------
// Lifecycle Simulation - Extracted from index.ts
// ---------------------------------------------------------------------------

import type { LifecycleState, LifeStage, LifeStageMultipliers } from "../types/index.js";

/**
 * Calculate biological age in days from birthDate and initialAgeDays
 */
export function calculateAgeDays(birthDate: string, initialAgeDays: number): number {
  const birth = new Date(birthDate);
  if (isNaN(birth.getTime())) {
    return initialAgeDays;
  }
  const now = new Date();
  const diffTime = now.getTime() - birth.getTime();
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
  return initialAgeDays + diffDays;
}

/**
 * Convert age in days to years (decimal)
 */
export function daysToYears(days: number): number {
  return Math.floor(days / 365.25);
}

/**
 * Determine life stage based on age in days
 */
export function getLifeStage(ageDays: number): LifeStage {
  if (ageDays < 730) return "infant";
  if (ageDays < 4380) return "child";
  if (ageDays < 6570) return "teen";
  if (ageDays < 21900) return "adult";
  if (ageDays < 25550) return "middle_adult";
  return "senior";
}

/**
 * Get metabolism rate multipliers based on life stage
 */
export function getLifeStageMultipliers(stage: LifeStage): LifeStageMultipliers {
  switch (stage) {
    case "infant":
      return { energy: 2.5, hunger: 2.0, thirst: 1.8, hygiene: 1.5, stress: 0.8, bladder: 2.5, bowel: 2.0, arousal: 0, libido: 0 };
    case "child":
      return { energy: 1.8, hunger: 1.8, thirst: 1.5, hygiene: 1.3, stress: 1.0, bladder: 2.0, bowel: 1.8, arousal: 0, libido: 0 };
    case "teen":
      return { energy: 1.5, hunger: 1.5, thirst: 1.3, hygiene: 1.2, stress: 1.5, bladder: 1.5, bowel: 1.3, arousal: 1.2, libido: 1.5 };
    case "adult":
      return { energy: 1.0, hunger: 1.0, thirst: 1.0, hygiene: 1.0, stress: 1.0, bladder: 1.0, bowel: 1.0, arousal: 1.0, libido: 1.0 };
    case "middle_adult":
      return { energy: 0.85, hunger: 0.9, thirst: 0.9, hygiene: 0.95, stress: 1.1, bladder: 1.1, bowel: 1.0, arousal: 0.7, libido: 0.6 };
    case "senior":
      return { energy: 0.6, hunger: 0.7, thirst: 0.75, hygiene: 0.8, stress: 0.9, bladder: 1.3, bowel: 1.1, arousal: 0.3, libido: 0.2 };
  }
}

/**
 * Create default lifecycle state
 */
export function getDefaultLifecycleState(birthDate?: string, initialAgeDays: number = 0): LifecycleState {
  const now = new Date();
  const bd = birthDate ?? now.toISOString().slice(0, 10);
  const ageDays = birthDate ? calculateAgeDays(bd, 0) : initialAgeDays;

  return {
    birth_date: bd,
    biological_age_days: ageDays,
    life_stage: getLifeStage(ageDays),
    last_aging_check: now.toISOString(),
    age_progression_enabled: true,
  };
}

/**
 * Update lifecycle - calculate aging and stage transitions
 */
export function updateLifecycle(lifecycle: LifecycleState): boolean {
  const now = new Date();
  const lastCheck = new Date(lifecycle.last_aging_check);

  const diffMs = now.getTime() - lastCheck.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays < 1 && lifecycle.age_progression_enabled) {
    const fraction = diffMs / (1000 * 60 * 60 * 24);
    lifecycle.biological_age_days += fraction;
  } else if (lifecycle.age_progression_enabled) {
    lifecycle.biological_age_days += diffDays;
  }

  lifecycle.last_aging_check = now.toISOString();

  const newStage = getLifeStage(lifecycle.biological_age_days);
  if (newStage !== lifecycle.life_stage) {
    lifecycle.life_stage = newStage;
    return true;
  }

  return false;
}

/**
 * Advance lifecycle state - calculates aging and stage transitions
 */
export function advanceLifecycle(
  lifecycleState: LifecycleState,
  birthDate: string,
  initialAgeDays: number
): { changed: boolean; newStage?: LifeStage } {
  const now = new Date();
  const lastCheck = new Date(lifecycleState.last_aging_check);

  const diffMs = now.getTime() - lastCheck.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays < 1 && lifecycleState.age_progression_enabled) {
    const fraction = diffMs / (1000 * 60 * 60 * 24);
    lifecycleState.biological_age_days += fraction;
  } else if (lifecycleState.age_progression_enabled) {
    lifecycleState.biological_age_days += diffDays;
  }

  lifecycleState.last_aging_check = now.toISOString();

  const newStage = getLifeStage(lifecycleState.biological_age_days);

  if (newStage !== lifecycleState.life_stage) {
    lifecycleState.life_stage = newStage;
    return { changed: true, newStage };
  }

  return { changed: false };
}

/**
 * Get age sensation based on life stage
 */
export function getAgeSensation(ageDays: number, stage: LifeStage): string | null {
  const years = Math.floor(ageDays / 365.25);

  if (stage === "infant") {
    return "Your senses are new and overwhelming. Everything is bright and loud.";
  }
  if (stage === "child") {
    return "You're full of curiosity. The world is fascinating.";
  }
  if (stage === "teen") {
    return "Hormones surge through you. Emotions feel intense and all-consuming.";
  }
  if (stage === "adult") {
    return "You feel in your prime, capable and focused.";
  }
  if (stage === "middle_adult") {
    if (years >= 65) {
      return "You notice subtle changes in your energy levels.";
    }
    return null;
  }
  if (stage === "senior") {
    return "Your body moves slower. Wisdom fills the spaces where energy once did.";
  }
  return null;
}
