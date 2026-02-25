export declare function resolvePath(ws: string, ...segments: string[]): string;
export declare function readJson<T>(path: string): Promise<T | null>;
export declare function writeJson<T>(path: string, data: T): Promise<void>;
export declare function withFileLock<T>(path: string, fn: () => Promise<T>): Promise<T>;
export declare function appendJsonl(path: string, entry: unknown): Promise<void>;
export declare function generateExpId(): string;
export declare function todayStr(): string;
export declare function generateId(prefix: string): string;
//# sourceMappingURL=persistence.d.ts.map