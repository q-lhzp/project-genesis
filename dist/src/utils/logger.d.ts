/**
 * Log levels
 */
export type LogLevel = "DEBUG" | "INFO" | "WARN" | "ERROR";
/**
 * Log entry structure
 */
export interface LogEntry {
    timestamp: string;
    level: LogLevel;
    module: string;
    message: string;
    data?: Record<string, any>;
}
/**
 * Logger configuration
 */
interface LoggerConfig {
    logDir: string;
    logFile: string;
    maxFileSize: number;
    maxFiles: number;
    minLevel: LogLevel;
}
/**
 * Logger class
 */
declare class GenesisLogger {
    private config;
    private logPath;
    private levelPriority;
    constructor(config?: Partial<LoggerConfig>);
    /**
     * Check if log level should be logged
     */
    private shouldLog;
    /**
     * Rotate log file if needed
     */
    private checkRotation;
    /**
     * Clean old log files
     */
    private cleanOldLogs;
    /**
     * Write log entry
     */
    private write;
    /**
     * Log debug message
     */
    debug(module: string, message: string, data?: Record<string, any>): void;
    /**
     * Log info message
     */
    info(module: string, message: string, data?: Record<string, any>): void;
    /**
     * Log warning
     */
    warn(module: string, message: string, data?: Record<string, any>): void;
    /**
     * Log error
     */
    error(module: string, message: string, data?: Record<string, any>): void;
    /**
     * Get recent log entries
     */
    getRecentLines(count?: number, level?: LogLevel, module?: string): Promise<LogEntry[]>;
    /**
     * Get system health status
     */
    getSystemHealth(): Promise<Record<string, string>>;
    /**
     * Get log file path
     */
    getLogPath(): string;
}
/**
 * Initialize logger with workspace path
 */
export declare function initLogger(workspacePath: string): GenesisLogger;
/**
 * Get logger instance
 */
export declare function getLogger(): GenesisLogger;
/**
 * Convenience functions
 */
export declare const log: {
    debug: (module: string, message: string, data?: Record<string, any>) => void;
    info: (module: string, message: string, data?: Record<string, any>) => void;
    warn: (module: string, message: string, data?: Record<string, any>) => void;
    error: (module: string, message: string, data?: Record<string, any>) => void;
};
export {};
//# sourceMappingURL=logger.d.ts.map