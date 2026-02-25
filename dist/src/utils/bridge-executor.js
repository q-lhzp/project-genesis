// ---------------------------------------------------------------------------
// Bridge Executor - Secure execFilePromise wrapper
// ---------------------------------------------------------------------------
import { execFile } from "node:child_process";
import { promisify } from "node:util";
export const execFilePromise = promisify(execFile);
export async function execBridge(scriptPath, args, options = {}) {
    return execFilePromise("python3", [scriptPath, ...args], {
        timeout: options.timeout ?? 30000,
        env: options.env ?? process.env
    });
}
export async function execBridgeWithJson(scriptPath, action, params, options = {}) {
    return execFilePromise("python3", [
        scriptPath,
        action,
        JSON.stringify(params)
    ], {
        timeout: options.timeout ?? 30000,
        env: options.env ?? process.env
    });
}
//# sourceMappingURL=bridge-executor.js.map