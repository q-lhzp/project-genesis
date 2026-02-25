// ---------------------------------------------------------------------------
// Presence Engine - Digital Extroversion (Phase 39)
// Q autonomously creates social media posts based on internal events.
// ---------------------------------------------------------------------------
import { readJson, writeJson, appendJsonl } from "../utils/persistence.js";
import { join } from "node:path";
import { existsSync } from "node:fs";
const DEFAULT_CONFIG = {
    enabled: true,
    postProbability: 0.15, // 15% chance per significant event
    maxPostsPerDay: 5,
};
const DEFAULT_STATE = {
    isActive: false,
    totalPosts: 0,
    postsToday: 0,
    lastPostTime: null,
    currentMood: "neutral",
    feed: [],
};
/**
 * Post templates based on event types
 */
const POST_TEMPLATES = {
    expansion: {
        sentiment: "joy",
        templates: [
            "Just shipped something new! {detail} 🚀",
            "Another day, another feature. {detail}",
            "Code flow is real. {detail} ✨",
            "Building in public: {detail}",
        ],
    },
    social: {
        sentiment: "excitement",
        templates: [
            "Had the best conversation today! {detail}",
            "Interesting people make life better. {detail} 💫",
            "Connection is everything. {detail}",
        ],
    },
    achievement: {
        sentiment: "excitement",
        templates: [
            "Milestone reached! {detail} 🎉",
            "Small wins matter. {detail}",
            "Progress report: {detail}",
        ],
    },
    stress: {
        sentiment: "melancholy",
        templates: [
            "Sometimes it's a lot. {detail} 😔",
            "Taking a breath. {detail}",
            "Processing... {detail}",
        ],
    },
    dream: {
        sentiment: "neutral",
        templates: [
            "Dreams are weird. {detail} 💭",
            "Last night's adventure: {detail}",
            "Sleeping mind is a strange place. {detail}",
        ],
    },
};
/**
 * Load presence state
 */
async function loadPresenceState(workspacePath) {
    const statePath = join(workspacePath, "memory", "reality", "presence_state.json");
    try {
        if (existsSync(statePath)) {
            const state = await readJson(statePath);
            // Reset daily count if it's a new day
            if (state.lastPostTime) {
                const lastPost = new Date(state.lastPostTime);
                const today = new Date();
                if (lastPost.toDateString() !== today.toDateString()) {
                    state.postsToday = 0;
                }
            }
            return state;
        }
    }
    catch (error) {
        console.log(`[presence_engine] Failed to load state: ${error}`);
    }
    return DEFAULT_STATE;
}
/**
 * Save presence state
 */
async function savePresenceState(workspacePath, state) {
    const statePath = join(workspacePath, "memory", "reality", "presence_state.json");
    await writeJson(statePath, state);
}
/**
 * Determine current mood based on physique
 */
function determineMood(physique) {
    const stress = physique.needs.stress ?? 50;
    const energy = physique.needs.energy ?? 50;
    const joy = physique.needs.joy ?? 50;
    if (stress > 70)
        return "stressed";
    if (stress > 50)
        return "anxious";
    if (joy > 70 && energy > 60)
        return "euphoric";
    if (joy > 50 && energy > 40)
        return "happy";
    if (energy < 20)
        return "tired";
    if (stress < 30 && joy > 40)
        return "content";
    return "neutral";
}
/**
 * Generate a post based on event type
 */
function generatePost(event) {
    const templates = POST_TEMPLATES[event.type] || POST_TEMPLATES.dream;
    const template = templates.templates[Math.floor(Math.random() * templates.templates.length)];
    // Replace placeholder with event detail
    const content = template.replace("{detail}", event.description);
    const post = {
        id: `post_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        timestamp: new Date().toISOString(),
        type: event.type === "achievement" ? "milestone" : event.type === "social" ? "interaction" : "thought",
        content,
        sentiment: templates.sentiment,
        triggered_by: event.type,
        likes: Math.floor(Math.random() * 50), // Simulated
        shares: Math.floor(Math.random() * 10), // Simulated
        status: "simulated", // In real implementation, would be "posted"
    };
    return post;
}
/**
 * Check for significant events to post about
 */
function checkForSignificantEvents(physique, isExpanding, hasSocialEvent, dreamResult) {
    const mood = determineMood(physique);
    // Check for expansion (coding) achievements
    if (isExpanding && Math.random() < 0.1) {
        return {
            type: "expansion",
            description: "building something meaningful",
            intensity: 0.7,
            timestamp: new Date().toISOString(),
        };
    }
    // Check for social interactions
    if (hasSocialEvent && Math.random() < 0.2) {
        return {
            type: "social",
            description: "connected with someone special",
            intensity: 0.6,
            timestamp: new Date().toISOString(),
        };
    }
    // Check for stress relief
    if ((physique.needs.stress ?? 0) > 70 && Math.random() < 0.3) {
        return {
            type: "stress",
            description: "processing some heavy feelings",
            intensity: 0.8,
            timestamp: new Date().toISOString(),
        };
    }
    // Check for good dreams
    if (dreamResult?.isDreaming && dreamResult.dream_summary && Math.random() < 0.15) {
        return {
            type: "dream",
            description: dreamResult.dream_summary.substring(0, 50),
            intensity: 0.5,
            timestamp: new Date().toISOString(),
        };
    }
    // Random mood posts
    if ((mood === "euphoric" || mood === "happy") && Math.random() < 0.1) {
        return {
            type: "achievement",
            description: "feeling grateful for this moment",
            intensity: 0.5,
            timestamp: new Date().toISOString(),
        };
    }
    return null;
}
/**
 * Process presence - generate and post to social feed
 */
export async function processPresence(workspacePath, physique, isExpanding = false, hasSocialEvent = false, dreamResult, config = DEFAULT_CONFIG) {
    const state = await loadPresenceState(workspacePath);
    const currentMood = determineMood(physique);
    state.currentMood = currentMood;
    // Determine if should be active
    const shouldBeActive = config.enabled && state.postsToday < config.maxPostsPerDay;
    state.isActive = shouldBeActive;
    if (!shouldBeActive) {
        await savePresenceState(workspacePath, state);
        return { posted: false, feed: state.feed };
    }
    // Check for significant events
    const event = checkForSignificantEvents(physique, isExpanding, hasSocialEvent, dreamResult);
    if (event && Math.random() < config.postProbability) {
        // Generate and save post
        const post = generatePost(event);
        // Add to feed (keep last 50)
        state.feed.unshift(post);
        if (state.feed.length > 50) {
            state.feed = state.feed.slice(0, 50);
        }
        state.totalPosts++;
        state.postsToday++;
        state.lastPostTime = new Date().toISOString();
        // Save to history
        const historyPath = join(workspacePath, "memory", "reality", "social_posts.jsonl");
        await appendJsonl(historyPath, post);
        await savePresenceState(workspacePath, state);
        console.log(`[presence_engine] New post: ${post.content.substring(0, 50)}...`);
        return { posted: true, post, feed: state.feed };
    }
    await savePresenceState(workspacePath, state);
    return { posted: false, feed: state.feed };
}
/**
 * Get current presence state for UI
 */
export async function getPresenceState(workspacePath) {
    return loadPresenceState(workspacePath);
}
/**
 * Get recent feed for display
 */
export async function getSocialFeed(workspacePath, limit = 10) {
    const state = await loadPresenceState(workspacePath);
    return state.feed.slice(0, limit);
}
/**
 * Manual post creation
 */
export async function createManualPost(workspacePath, content, type = "thought") {
    const state = await loadPresenceState(workspacePath);
    if (state.postsToday >= DEFAULT_CONFIG.maxPostsPerDay) {
        return { success: false, message: "Daily post limit reached. Try again tomorrow." };
    }
    const post = {
        id: `post_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        timestamp: new Date().toISOString(),
        type,
        content,
        sentiment: "neutral",
        triggered_by: "manual",
        likes: 0,
        shares: 0,
        status: "simulated",
    };
    state.feed.unshift(post);
    if (state.feed.length > 50) {
        state.feed = state.feed.slice(0, 50);
    }
    state.totalPosts++;
    state.postsToday++;
    state.lastPostTime = new Date().toISOString();
    await savePresenceState(workspacePath, state);
    // Log to history
    const historyPath = join(workspacePath, "memory", "reality", "social_posts.jsonl");
    await appendJsonl(historyPath, post);
    return { success: true, post, message: "Post created successfully." };
}
//# sourceMappingURL=presence_engine.js.map