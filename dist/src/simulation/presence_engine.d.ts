import type { Physique } from "../types/index.js";
/**
 * Social post configuration
 */
interface PresenceConfig {
    enabled: boolean;
    postProbability: number;
    maxPostsPerDay: number;
}
/**
 * Social post record
 */
interface SocialPost {
    id: string;
    timestamp: string;
    type: "thought" | "selfie" | "milestone" | "reflection" | "interaction";
    content: string;
    sentiment: "joy" | "neutral" | "melancholy" | "excitement" | "frustration";
    triggered_by: string;
    likes: number;
    shares: number;
    status: "draft" | "posted" | "simulated";
}
/**
 * Presence state
 */
interface PresenceState {
    isActive: boolean;
    totalPosts: number;
    postsToday: number;
    lastPostTime: string | null;
    currentMood: string;
    feed: SocialPost[];
}
/**
 * Process presence - generate and post to social feed
 */
export declare function processPresence(workspacePath: string, physique: Physique, isExpanding?: boolean, hasSocialEvent?: boolean, dreamResult?: {
    isDreaming: boolean;
    dream_summary?: string;
}, config?: PresenceConfig): Promise<{
    posted: boolean;
    post?: SocialPost;
    feed: SocialPost[];
}>;
/**
 * Get current presence state for UI
 */
export declare function getPresenceState(workspacePath: string): Promise<PresenceState>;
/**
 * Get recent feed for display
 */
export declare function getSocialFeed(workspacePath: string, limit?: number): Promise<SocialPost[]>;
/**
 * Manual post creation
 */
export declare function createManualPost(workspacePath: string, content: string, type?: SocialPost["type"]): Promise<{
    success: boolean;
    post?: SocialPost;
    message: string;
}>;
export {};
//# sourceMappingURL=presence_engine.d.ts.map