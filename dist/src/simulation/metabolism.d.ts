import type { Needs, Physique, LifecycleState, CycleState } from "../types/index.js";
export declare function getCyclePhase(day: number): CycleState["phase"];
export declare function getCycleMetabolismModifiers(phase: CycleState["phase"]): Partial<Needs>;
export declare function getCycleHormones(day: number): CycleState["hormones"];
export declare function getDefaultCycleState(): CycleState;
export declare function advanceCycleDay(cycle: CycleState): boolean;
export declare function updateMetabolism(ph: Physique, rates: Record<string, number>, modules: {
    eros: boolean;
    cycle: boolean;
}, cycleState?: CycleState | null, lifecycleState?: LifecycleState | null): boolean;
import { getAgeSensation } from "./lifecycle.js";
export { getAgeSensation };
//# sourceMappingURL=metabolism.d.ts.map