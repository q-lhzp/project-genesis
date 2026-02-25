import { execFile } from "node:child_process";
export declare const execFilePromise: typeof execFile.__promisify__;
export interface BridgeOptions {
    timeout?: number;
    env?: NodeJS.ProcessEnv;
}
export declare function execBridge(scriptPath: string, args: string[], options?: BridgeOptions): Promise<{
    stdout: string;
    stderr: string;
}>;
export declare function execBridgeWithJson(scriptPath: string, action: string, params: Record<string, unknown>, options?: BridgeOptions): Promise<{
    stdout: string;
    stderr: string;
}>;
//# sourceMappingURL=bridge-executor.d.ts.map