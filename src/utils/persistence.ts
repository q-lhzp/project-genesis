// ---------------------------------------------------------------------------
// Persistence Utilities - Extracted from index.ts
// ---------------------------------------------------------------------------

import { promises as fs } from "node:fs";
import { dirname, join } from "node:path";

export function resolvePath(ws: string, ...segments: string[]): string {
  return join(ws, ...segments);
}

export async function readJson<T>(path: string): Promise<T | null> {
  try {
    return JSON.parse(await fs.readFile(path, "utf-8")) as T;
  } catch {
    return null;
  }
}

export async function writeJson<T>(path: string, data: T): Promise<void> {
  await fs.mkdir(dirname(path), { recursive: true });
  const tmp = path + ".tmp";
  await fs.writeFile(tmp, JSON.stringify(data, null, 2));
  await fs.rename(tmp, path);
}

// ---------------------------------------------------------------------------
// File-Lock: Map-based promise queue to prevent read-modify-write races
// ---------------------------------------------------------------------------

const fileLocks = new Map<string, Promise<unknown>>();

export async function withFileLock<T>(path: string, fn: () => Promise<T>): Promise<T> {
  const prev = fileLocks.get(path) ?? Promise.resolve();
  const next = prev.then(fn, fn);
  fileLocks.set(path, next);
  try {
    return await next;
  } finally {
    if (fileLocks.get(path) === next) fileLocks.delete(path);
  }
}

export async function appendJsonl(path: string, entry: unknown): Promise<void> {
  await fs.mkdir(dirname(path), { recursive: true });
  await fs.appendFile(path, JSON.stringify(entry) + "\n");
}

const expCounters = new Map<string, number>();

export function generateExpId(): string {
  const date = new Date().toISOString().slice(0, 10).replace(/-/g, "");
  const prev = expCounters.get(date) ?? 0;
  const next = prev + 1;
  expCounters.set(date, next);
  return `EXP-${date}-${String(next).padStart(4, "0")}`;
}

export function todayStr(): string {
  return new Date().toISOString().slice(0, 10);
}

export function generateId(prefix: string): string {
  return `${prefix}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
}

/**
 * Read a JSONL (JSON Lines) file and return array of objects
 */
export async function readJsonl<T>(path: string): Promise<T[]> {
  try {
    const content = await fs.readFile(path, "utf-8");
    const lines = content.split("\n").filter(line => line.trim());
    return lines.map(line => JSON.parse(line) as T);
  } catch {
    return [];
  }
}

/**
 * Read the header and the last N sections (starting with ###) from a markdown file.
 */
export async function readMarkdownTail(path: string, maxSections: number = 10): Promise<string> {
  try {
    const content = await fs.readFile(path, "utf-8");
    const parts = content.split(/\n### /);
    if (parts.length <= 1) return content;

    const header = parts[0];
    const sections = parts.slice(1).map(s => "### " + s);
    
    if (sections.length <= maxSections) return content;

    const tail = sections.slice(-maxSections);
    return header + "\n" + tail.join("\n");
  } catch {
    return "";
  }
}
