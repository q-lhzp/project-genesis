import type { Physique } from "../types/index.js";
/**
 * Economy configuration
 */
interface EconomyConfig {
    paperTrading: boolean;
    riskTolerance: "conservative" | "moderate" | "aggressive";
    minTradeInterval: number;
    maxPositionSize: number;
}
/**
 * Economy state
 */
interface EconomyState {
    isActive: boolean;
    lastTradeTime: string | null;
    totalTrades: number;
    totalProfitLoss: number;
    currentStrategy: string;
    marketMood: "bullish" | "bearish" | "neutral";
}
/**
 * Main processing function - call from tick handler
 */
export declare function processEconomy(workspacePath: string, physique: Physique, isResearching: boolean, config?: EconomyConfig): Promise<{
    isActive: boolean;
    strategy: string;
    mood: string;
    lastTrade: string | null;
}>;
/**
 * Get current economy state for UI
 */
export declare function getEconomyState(workspacePath: string): Promise<EconomyState>;
/**
 * Initialize vault with seed capital (for testing)
 */
export declare function initializeVault(workspacePath: string, initialDeposit?: number): Promise<void>;
export {};
//# sourceMappingURL=economy_engine.d.ts.map