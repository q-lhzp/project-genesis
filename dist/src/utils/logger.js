// ---------------------------------------------------------------------------
// Unified Logger - Centralized Logging System (Phase 41)
// Structured JSONL logging with rotation and filtering.
// ---------------------------------------------------------------------------
import { appendJsonl } from "./persistence.js";
import { join } from "node:path";
import { existsSync, statSync, renameSync } from "node:fs";
const DEFAULT_CONFIG = {
    logDir: "memory",
    logFile: "genesis_debug.jsonl",
    maxFileSize: 50 * 1024 * 1024, // 50MB
    maxFiles: 7, // Keep 7 days of logs
    minLevel: "INFO",
};
/**
 * Logger class
 */
class GenesisLogger {
    config;
    logPath;
    levelPriority = {
        DEBUG: 0,
        INFO: 1,
        WARN: 2,
        ERROR: 3,
    };
    constructor(config = {}) {
        this.config = { ...DEFAULT_CONFIG, ...config };
        this.logPath = join(this.config.logDir, this.config.logFile);
    }
    /**
     * Check if log level should be logged
     */
    shouldLog(level) {
        return this.levelPriority[level] >= this.levelPriority[this.config.minLevel];
    }
    /**
     * Rotate log file if needed
     */
    checkRotation() {
        try {
            if (!existsSync(this.logPath))
                return;
            const stats = statSync(this.logPath);
            if (stats.size >= this.config.maxFileSize) {
                const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
                const archivePath = join(this.config.logDir, `genesis_debug_${timestamp}.jsonl`);
                renameSync(this.logPath, archivePath);
                this.cleanOldLogs();
            }
        }
        catch (e) {
            // Ignore rotation errors
        }
    }
    /**
     * Clean old log files
     */
    cleanOldLogs() {
        try {
            const { readdirSync, unlinkSync } = require("node:fs");
            const files = readdirSync(this.config.logDir)
                .filter(f => f.startsWith("genesis_debug_") && f.endsWith(".jsonl"))
                .sort()
                .reverse();
            // Remove oldest files beyond maxFiles
            for (let i = this.config.maxFiles; i < files.length; i++) {
                unlinkSync(join(this.config.logDir, files[i]));
            }
        }
        catch (e) {
            // Ignore cleanup errors
        }
    }
    /**
     * Write log entry
     */
    write(entry) {
        if (!this.shouldLog(entry.level))
            return;
        this.checkRotation();
        try {
            // Ensure directory exists
            const { mkdirSync } = require("node:fs");
            mkdirSync(this.config.logDir, { recursive: true });
            // Write JSONL entry
            appendJsonl(this.logPath, entry);
        }
        catch (e) {
            console.error("[logger] Failed to write log:", e);
        }
    }
    /**
     * Log debug message
     */
    debug(module, message, data) {
        this.write({
            timestamp: new Date().toISOString(),
            level: "DEBUG",
            module,
            message,
            data,
        });
    }
    /**
     * Log info message
     */
    info(module, message, data) {
        this.write({
            timestamp: new Date().toISOString(),
            level: "INFO",
            module,
            message,
            data,
        });
    }
    /**
     * Log warning
     */
    warn(module, message, data) {
        this.write({
            timestamp: new Date().toISOString(),
            level: "WARN",
            module,
            message,
            data,
        });
    }
    /**
     * Log error
     */
    error(module, message, data) {
        this.write({
            timestamp: new Date().toISOString(),
            level: "ERROR",
            module,
            message,
            data,
        });
    }
    /**
     * Get recent log entries
     */
    async getRecentLines(count = 100, level, module) {
        const entries = [];
        try {
            if (!existsSync(this.logPath))
                return entries;
            const { createReadStream } = require("node:fs");
            const readline = require("node:readline");
            const fileStream = createReadStream(this.logPath, { encoding: "utf8" });
            const rl = readline.createInterface({ input: fileStream, crlfDelay: Infinity });
            for await (const line of rl) {
                try {
                    const entry = JSON.parse(line);
                    // Filter by level
                    if (level && entry.level !== level)
                        continue;
                    // Filter by module
                    if (module && entry.module !== module)
                        continue;
                    entries.push(entry);
                    // Keep only last N entries
                    if (entries.length > count) {
                        entries.shift();
                    }
                }
                catch {
                    // Skip malformed lines
                }
            }
        }
        catch (e) {
            console.error("[logger] Failed to read logs:", e);
        }
        return entries.reverse(); // Most recent first
    }
    /**
     * Get system health status
     */
    async getSystemHealth() {
        const health = {};
        // Check log file
        try {
            if (existsSync(this.logPath)) {
                const stats = statSync(this.logPath);
                health["logging"] = `Active (${(stats.size / 1024 / 1024).toFixed(1)}MB)`;
            }
            else {
                health["logging"] = "Initializing";
            }
        }
        catch {
            health["logging"] = "Error";
        }
        return health;
    }
    /**
     * Get log file path
     */
    getLogPath() {
        return this.logPath;
    }
}
// Singleton instance
let loggerInstance = null;
/**
 * Initialize logger with workspace path
 */
export function initLogger(workspacePath) {
    loggerInstance = new GenesisLogger({
        logDir: join(workspacePath, "memory"),
        logFile: "genesis_debug.jsonl",
    });
    loggerInstance.info("logger", "Logger initialized", { version: "5.1.0" });
    return loggerInstance;
}
/**
 * Get logger instance
 */
export function getLogger() {
    if (!loggerInstance) {
        // Create default instance if not initialized
        loggerInstance = new GenesisLogger();
    }
    return loggerInstance;
}
/**
 * Convenience functions
 */
export const log = {
    debug: (module, message, data) => getLogger().debug(module, message, data),
    info: (module, message, data) => getLogger().info(module, message, data),
    warn: (module, message, data) => getLogger().warn(module, message, data),
    error: (module, message, data) => getLogger().error(module, message, data),
};
//# sourceMappingURL=logger.js.map