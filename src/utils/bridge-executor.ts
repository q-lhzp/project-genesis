// ---------------------------------------------------------------------------
// Bridge Executor - Secure execFilePromise wrapper
// ---------------------------------------------------------------------------

import { execFile } from "node:child_process";
import { promisify } from "node:util";

export const execFilePromise = promisify(execFile);

export interface BridgeOptions {
  timeout?: number;
  env?: NodeJS.ProcessEnv;
}

export async function execBridge(
  scriptPath: string,
  args: string[],
  options: BridgeOptions = {}
): Promise<{ stdout: string; stderr: string }> {
  return execFilePromise("python3", [scriptPath, ...args], {
    timeout: options.timeout ?? 30000,
    env: options.env ?? process.env
  });
}

export async function execBridgeWithJson(
  scriptPath: string,
  action: string,
  params: Record<string, unknown>,
  options: BridgeOptions = {}
): Promise<{ stdout: string; stderr: string }> {
  return execFilePromise("python3", [
    scriptPath,
    action,
    JSON.stringify(params)
  ], {
    timeout: options.timeout ?? 30000,
    env: options.env ?? process.env
  });
}
