// ---------------------------------------------------------------------------
// Economy Engine - Autonomous Trading (Phase 37)
// Q manages her own wealth based on internal state and market analysis.
// ---------------------------------------------------------------------------

import { readJson, writeJson, appendJsonl } from "../utils/persistence.js";
import { join } from "node:path";
import { existsSync } from "node:fs";
import { execFilePromise } from "../utils/bridge-executor.js";
import { log } from "../utils/logger.js";
import type { Physique } from "../types/index.js";

/**
 * Economy configuration
 */
interface EconomyConfig {
  paperTrading: boolean;      // Default true for safety
  riskTolerance: "conservative" | "moderate" | "aggressive";
  minTradeInterval: number;   // ms between trades
  maxPositionSize: number;   // max % of portfolio per trade
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
 * Trade record
 */
interface TradeRecord {
  timestamp: string;
  symbol: string;
  type: "buy" | "sell";
  amount: number;
  price: number;
  total: number;
  strategy: string;
  reason: string;
  mood: string;
}

const DEFAULT_CONFIG: EconomyConfig = {
  paperTrading: true,
  riskTolerance: "moderate",
  minTradeInterval: 300000, // 5 minutes
  maxPositionSize: 0.2,    // 20% max per trade
};

const DEFAULT_STATE: EconomyState = {
  isActive: false,
  lastTradeTime: null,
  totalTrades: 0,
  totalProfitLoss: 0,
  currentStrategy: "observe",
  marketMood: "neutral",
};

/**
 * Available trading symbols
 */
const CRYPTO_SYMBOLS = ["BTC", "ETH", "SOL", "XRP", "ADA", "DOGE"];
const STOCK_SYMBOLS = ["AAPL", "GOOGL", "MSFT", "NVDA", "TSLA", "META"];

/**
 * Load economy state from disk
 */
async function loadEconomyState(workspacePath: string): Promise<EconomyState> {
  const statePath = join(workspacePath, "memory", "reality", "economy_state.json");
  try {
    if (existsSync(statePath)) {
      return await readJson(statePath) || DEFAULT_STATE;
    }
  } catch (error) {
    console.log(`[economy_engine] Failed to load state: ${error}`);
  }
  return DEFAULT_STATE;
}

/**
 * Save economy state
 */
async function saveEconomyState(workspacePath: string, state: EconomyState): Promise<void> {
  const statePath = join(workspacePath, "memory", "reality", "economy_state.json");
  await writeJson(statePath, state);
}

/**
 * Determine risk tolerance based on Q's internal state
 */
function determineRiskTolerance(physique: Physique): EconomyConfig["riskTolerance"] {
  const stress = physique.needs.stress ?? 50;
  const joy = (physique.needs as any).joy ?? 50;

  // High stress + low joy = conservative (panic mode)
  if (stress > 70 || joy < 30) return "conservative";

  // Low stress + high joy = aggressive
  if (stress < 30 && joy > 70) return "aggressive";

  return "moderate";
}

/**
 * Analyze market mood based on Q's state
 */
function analyzeMarketMood(physique: Physique, isResearching: boolean): EconomyState["marketMood"] {
  const stress = physique.needs.stress ?? 50;
  const joy = (physique.needs as any).joy ?? 50;

  // If researching (morning routine), more analytical
  if (isResearching) {
    if (joy > 60 && stress < 40) return "bullish";
    if (joy < 40 || stress > 60) return "bearish";
    return "neutral";
  }

  // Emotional trading based on internal state
  if (stress > 80) return "bearish"; // Panic selling
  if (joy > 70) return "bullish";    // Euphoric buying

  return "neutral";
}

/**
 * Select trading strategy based on market mood and risk tolerance
 */
function selectStrategy(
  mood: EconomyState["marketMood"],
  riskTolerance: EconomyConfig["riskTolerance"]
): string {
  if (riskTolerance === "conservative") {
    return mood === "bearish" ? "panic_sell" : "hold";
  }

  if (riskTolerance === "aggressive") {
    if (mood === "bullish") return "momentum_buy";
    if (mood === "bearish") return "buy_the_dip";
    return "day_trade";
  }

  // Moderate
  if (mood === "bullish") return "gradual_buy";
  if (mood === "bearish") return "stop_loss";
  return "dollar_cost_average";
}

/**
 * Execute a trade via vault bridge
 */
async function executeTrade(
  workspacePath: string,
  symbol: string,
  amount: number,
  tradeType: "buy" | "sell",
  strategy: string,
  reason: string,
  mood: string
): Promise<{ success: boolean; message: string; trade?: TradeRecord }> {
  const vaultBridge = join(workspacePath, "skills", "soul-evolution", "tools", "vault_bridge.py");

  try {
    const { stdout } = await execFilePromise("python3", [
      vaultBridge,
      JSON.stringify({
        action: "trade",
        symbol: symbol,
        amount: amount,
        type: tradeType,
      }),
    ], { timeout: 30000 });

    const result = JSON.parse(stdout);

    if (result.success) {
      const trade: TradeRecord = {
        timestamp: new Date().toISOString(),
        symbol,
        type: tradeType,
        amount,
        price: result.transaction?.price ?? 0,
        total: result.transaction?.total ?? 0,
        strategy,
        reason,
        mood,
      };

      // Log trade to history
      const tradeHistoryPath = join(workspacePath, "memory", "vault", "trade_history.jsonl");
      await appendJsonl(tradeHistoryPath, trade);

      return {
        success: true,
        message: `${tradeType.toUpperCase()} ${amount} ${symbol} at $${result.transaction?.price?.toFixed(2)} - Strategy: ${strategy}`,
        trade,
      };
    }

    return { success: false, message: result.error || "Trade failed" };
  } catch (error) {
    return { success: false, message: `Trade error: ${error}` };
  }
}

/**
 * Get current portfolio status
 */
async function getPortfolioStatus(workspacePath: string): Promise<{
  totalValue: number;
  cash: number;
  positions: Record<string, any>;
}> {
  const vaultBridge = join(workspacePath, "skills", "soul-evolution", "tools", "vault_bridge.py");

  try {
    const { stdout } = await execFilePromise("python3", [
      vaultBridge,
      JSON.stringify({ action: "status" }),
    ], { timeout: 30000 });

    const result = JSON.parse(stdout);
    const balances = result.balances || {};

    let totalValue = balances.USD || 0;

    // Calculate position values
    const positions = result.positions || {};

    return {
      totalValue,
      cash: balances.USD || 0,
      positions,
    };
  } catch (error) {
    console.log(`[economy_engine] Portfolio error: ${error}`);
    return { totalValue: 0, cash: 0, positions: {} };
  }
}

/**
 * Main processing function - call from tick handler
 */
export async function processEconomy(
  workspacePath: string,
  physique: Physique,
  isResearching: boolean,
  config: EconomyConfig = DEFAULT_CONFIG
): Promise<{
  isActive: boolean;
  strategy: string;
  mood: string;
  lastTrade: string | null;
}> {
  log.debug("economy", "Processing economy tick", { isResearching, stress: physique.needs.stress });

  const state = await loadEconomyState(workspacePath);

  // Determine current risk tolerance based on Q's state
  const riskTolerance = determineRiskTolerance(physique);
  log.debug("economy", "Risk tolerance determined", { riskTolerance });

  // Analyze market mood
  const mood = analyzeMarketMood(physique, isResearching);

  // Select strategy
  const strategy = selectStrategy(mood, riskTolerance);
  log.debug("economy", "Strategy selected", { strategy, mood });
  state.currentStrategy = strategy;
  state.marketMood = mood;

  // Check if should be active (researching in morning or explicit trading mode)
  const shouldBeActive = isResearching;

  if (shouldBeActive && !state.isActive) {
    state.isActive = true;
    console.log(`[economy_engine] Activated: ${strategy} (${mood} mood, ${riskTolerance} risk)`);
  } else if (!shouldBeActive && state.isActive) {
    state.isActive = false;
    console.log("[economy_engine] Deactivated");
  }

  await saveEconomyState(workspacePath, state);

  // Process trading if active
  if (state.isActive) {
    // Get portfolio status
    const portfolio = await getPortfolioStatus(workspacePath);

    // Decide whether to trade based on strategy
    if (strategy === "momentum_buy" || strategy === "gradual_buy" || strategy === "buy_the_dip") {
      // Attempt to buy
      const symbol = mood === "bullish"
        ? CRYPTO_SYMBOLS[Math.floor(Math.random() * CRYPTO_SYMBOLS.length)]
        : STOCK_SYMBOLS[Math.floor(Math.random() * STOCK_SYMBOLS.length)];

      // Calculate position size (max 10% of cash)
      const maxAmount = (portfolio.cash * config.maxPositionSize) / 100;
      const amount = Math.random() * maxAmount * 10; // Small fractional amounts

      if (amount > 0.01 && portfolio.cash > 10) {
        const result = await executeTrade(
          workspacePath,
          symbol,
          amount,
          "buy",
          strategy,
          `${mood} mood driving ${riskTolerance} buy`,
          mood
        );

        if (result.success) {
          state.lastTradeTime = new Date().toISOString();
          state.totalTrades++;
          console.log(`[economy_engine] Trade executed: ${result.message}`);
          await saveEconomyState(workspacePath, state);
        }
      }
    } else if (strategy === "panic_sell" || strategy === "stop_loss") {
      // Attempt to sell some positions
      const positions = Object.keys(portfolio.positions);

      if (positions.length > 0) {
        const symbol = positions[Math.floor(Math.random() * positions.length)];
        const position = portfolio.positions[symbol];
        const sellAmount = position.amount * 0.25; // Sell 25% of position

        if (sellAmount > 0.001) {
          const result = await executeTrade(
            workspacePath,
            symbol,
            sellAmount,
            "sell",
            strategy,
            `${mood} mood driving ${riskTolerance} sell`,
            mood
          );

          if (result.success) {
            state.lastTradeTime = new Date().toISOString();
            state.totalTrades++;
            console.log(`[economy_engine] Trade executed: ${result.message}`);
            await saveEconomyState(workspacePath, state);
          }
        }
      }
    }
  }

  return {
    isActive: state.isActive,
    strategy: state.currentStrategy,
    mood: state.marketMood,
    lastTrade: state.lastTradeTime,
  };
}

/**
 * Get current economy state for UI
 */
export async function getEconomyState(workspacePath: string): Promise<EconomyState> {
  return loadEconomyState(workspacePath);
}

/**
 * Initialize vault with seed capital (for testing)
 */
export async function initializeVault(workspacePath: string, initialDeposit: number = 10000): Promise<void> {
  const vaultBridge = join(workspacePath, "skills", "soul-evolution", "tools", "vault_bridge.py");

  try {
    const { stdout } = await execFilePromise("python3", [
      vaultBridge,
      JSON.stringify({
        action: "deposit",
        amount: initialDeposit,
      }),
    ], { timeout: 30000 });

    const result = JSON.parse(stdout);
    if (result.success) {
      console.log(`[economy_engine] Vault initialized with $${initialDeposit}`);
    }
  } catch (error) {
    console.log(`[economy_engine] Init error: ${error}`);
  }
}
