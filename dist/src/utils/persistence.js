// ---------------------------------------------------------------------------
// Persistence Utilities - Extracted from index.ts
// ---------------------------------------------------------------------------
import { promises as fs } from "node:fs";
import { dirname, join } from "node:path";
export function resolvePath(ws, ...segments) {
    return join(ws, ...segments);
}
export async function readJson(path) {
    try {
        return JSON.parse(await fs.readFile(path, "utf-8"));
    }
    catch {
        return null;
    }
}
export async function writeJson(path, data) {
    await fs.mkdir(dirname(path), { recursive: true });
    const tmp = path + ".tmp";
    await fs.writeFile(tmp, JSON.stringify(data, null, 2));
    await fs.rename(tmp, path);
}
// ---------------------------------------------------------------------------
// File-Lock: Map-based promise queue to prevent read-modify-write races
// ---------------------------------------------------------------------------
const fileLocks = new Map();
export async function withFileLock(path, fn) {
    const prev = fileLocks.get(path) ?? Promise.resolve();
    const next = prev.then(fn, fn);
    fileLocks.set(path, next);
    try {
        return await next;
    }
    finally {
        if (fileLocks.get(path) === next)
            fileLocks.delete(path);
    }
}
export async function appendJsonl(path, entry) {
    await fs.mkdir(dirname(path), { recursive: true });
    await fs.appendFile(path, JSON.stringify(entry) + "\n");
}
const expCounters = new Map();
export function generateExpId() {
    const date = new Date().toISOString().slice(0, 10).replace(/-/g, "");
    const prev = expCounters.get(date) ?? 0;
    const next = prev + 1;
    expCounters.set(date, next);
    return `EXP-${date}-${String(next).padStart(4, "0")}`;
}
export function todayStr() {
    return new Date().toISOString().slice(0, 10);
}
export function generateId(prefix) {
    return `${prefix}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
}
//# sourceMappingURL=persistence.js.map