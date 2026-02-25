/**
 * Diagnostic result for a single check
 */
export interface DiagnosticResult {
    check: string;
    status: "PASS" | "FAIL" | "WARN";
    message: string;
    details?: Record<string, any>;
    fixed?: boolean;
}
/**
 * Full diagnostic report
 */
export interface DiagnosticReport {
    timestamp: string;
    version: string;
    workspacePath: string;
    overallStatus: "HEALTHY" | "DEGRADED" | "CRITICAL";
    results: DiagnosticResult[];
    summary: {
        passed: number;
        failed: number;
        warnings: number;
        fixed: number;
    };
}
/**
 * Run diagnostics and return formatted report
 */
export declare function runDoctor(workspacePath: string, autoFix?: boolean): Promise<DiagnosticReport>;
/**
 * Quick health check - returns boolean
 */
export declare function quickHealthCheck(workspacePath: string): Promise<boolean>;
/**
 * Get diagnostic summary for API
 */
export declare function getDiagnosticSummary(workspacePath: string): Promise<{
    status: string;
    checks: {
        name: string;
        status: string;
        message: string;
    }[];
    summary: {
        passed: number;
        failed: number;
        warnings: number;
        fixed: number;
    };
}>;
//# sourceMappingURL=doctor.d.ts.map