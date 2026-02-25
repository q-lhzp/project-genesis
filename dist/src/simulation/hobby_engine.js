// ---------------------------------------------------------------------------
// Hobby Engine - Autonomous Interest & Research Development
// Phase 28: Autonomous Hobby & Research Engine
// ---------------------------------------------------------------------------
import { readJson, writeJson } from "../utils/persistence.js";
import { join } from "node:path";
import { existsSync, appendFileSync, writeFileSync } from "node:fs";
const DEFAULT_CONFIG = {
    energyThreshold: 70,
    researchDurationMs: 10000,
    cooldownMinutes: 30
};
let currentResearch = {
    isResearching: false,
    currentTopic: null,
    currentPhase: "idle",
    lastResearchTime: null,
    sentiment: 0
};
/**
 * Fallback topics when interests.json is empty
 */
const FALLBACK_TOPICS = [
    "Cybernetics and Human Enhancement",
    "Neural Networks and AI Architecture",
    "Digital Art and Generative Design",
    "Urban Legends and Cyberpunk Culture",
    "Quantum Computing Basics",
    "Biohacking and Longevity",
    "Virtual Reality Development",
    "Decentralized Systems",
    "Synthetic Biology",
    "Space Exploration Technologies"
];
/**
 * Load interests data
 */
async function loadInterests(workspacePath) {
    const interestsPath = join(workspacePath, "memory", "reality", "interests.json");
    try {
        if (existsSync(interestsPath)) {
            const data = await readJson(interestsPath);
            if (data)
                return data;
        }
    }
    catch (error) {
        console.log(`[hobby_engine] Failed to load interests: ${error}`);
    }
    return {
        hobbies: [],
        likes: {},
        dislikes: [],
        wishlist: [],
        experiences: []
    };
}
/**
 * Save interests data
 */
async function saveInterests(workspacePath, data) {
    const interestsPath = join(workspacePath, "memory", "reality", "interests.json");
    await writeJson(interestsPath, data);
}
/**
 * Select a topic to research
 */
function selectTopic(interests) {
    // If there are existing hobbies with low research count, research those further
    const underResearched = interests.hobbies.filter(h => h.researchCount < 3);
    if (underResearched.length > 0 && Math.random() > 0.5) {
        return underResearched[Math.floor(Math.random() * underResearched.length)].topic;
    }
    // Otherwise pick from fallback or random
    const existingTopics = interests.hobbies.map(h => h.topic);
    const availableFallback = FALLBACK_TOPICS.filter(t => !existingTopics.includes(t));
    if (availableFallback.length > 0) {
        return availableFallback[Math.floor(Math.random() * availableFallback.length)];
    }
    return FALLBACK_TOPICS[Math.floor(Math.random() * FALLBACK_TOPICS.length)];
}
/**
 * Simulate search results (in production, would use actual web search)
 */
function simulateSearch(topic) {
    // Simple simulation - in production would use browser bridge
    const findings = [
        `Researched ${topic}: Found interesting connections to digital consciousness`,
        `Explored ${topic}: Discovered emerging trends in human-AI collaboration`,
        `Deep dive into ${topic}: Found promising research directions`,
        `Analyzed ${topic}: Noted several innovative approaches`,
        `Investigated ${topic}: Found compelling arguments for its relevance`
    ];
    return findings[Math.floor(Math.random() * findings.length)];
}
/**
 * Determine sentiment based on "findings" (simplified)
 */
function determineSentiment(findings) {
    // Simple positive/negative keyword detection
    const positiveWords = ["interesting", "promising", "innovative", "compelling", "exciting", "fascinating", "useful"];
    const negativeWords = ["boring", "useless", "outdated", "irrelevant", "disappointing"];
    let score = 0.5; // Neutral baseline
    for (const word of positiveWords) {
        if (findings.toLowerCase().includes(word)) {
            score += 0.1;
        }
    }
    for (const word of negativeWords) {
        if (findings.toLowerCase().includes(word)) {
            score -= 0.1;
        }
    }
    return Math.max(0, Math.min(1, score));
}
/**
 * Research cycle - simulate a complete research session
 */
async function runResearchCycle(workspacePath, topic) {
    console.log(`[hobby_engine] Starting research on: ${topic}`);
    // Phase 1: Simulate searching
    currentResearch.currentPhase = "searching";
    const findings = simulateSearch(topic);
    // Phase 2: Determine sentiment
    currentResearch.currentPhase = "deciding";
    const sentiment = determineSentiment(findings);
    // Phase 3: Update interests.json
    const interests = await loadInterests(workspacePath);
    // Check if topic already exists
    const existingHobby = interests.hobbies.find(h => h.topic === topic);
    if (existingHobby) {
        existingHobby.researchCount++;
        // Update sentiment (average)
        existingHobby.sentiment = (existingHobby.sentiment + sentiment) / 2;
    }
    else {
        interests.hobbies.push({
            topic,
            discoveredAt: new Date().toISOString(),
            sentiment,
            researchCount: 1
        });
    }
    // Update likes
    if (sentiment > 0.6) {
        interests.likes[topic] = sentiment;
    }
    else if (sentiment < 0.4) {
        interests.dislikes.push(topic);
    }
    await saveInterests(workspacePath, interests);
    console.log(`[hobby_engine] Research complete. Sentiment: ${sentiment}`);
    return { topic, findings, sentiment };
}
/**
 * Check if Q should start researching
 */
export function shouldStartResearch(physique, config = DEFAULT_CONFIG) {
    // Already researching
    if (currentResearch.isResearching)
        return false;
    // Check cooldown
    if (currentResearch.lastResearchTime) {
        const lastResearch = new Date(currentResearch.lastResearchTime);
        const minutesSince = (Date.now() - lastResearch.getTime()) / (1000 * 60);
        if (minutesSince < config.cooldownMinutes)
            return false;
    }
    // Check energy
    const energy = physique.needs?.energy ?? 0;
    return energy > config.energyThreshold;
}
/**
 * Process hobby/research activity
 * Call this from tick handler
 */
export async function processHobbyActivity(workspacePath, physique, config = DEFAULT_CONFIG) {
    // Check if should start research
    if (shouldStartResearch(physique, config)) {
        console.log("[hobby_engine] Starting autonomous research...");
        currentResearch.isResearching = true;
        currentResearch.currentPhase = "selecting";
        // Load interests and select topic
        const interests = await loadInterests(workspacePath);
        const topic = selectTopic(interests);
        currentResearch.currentTopic = topic;
        // Run research cycle
        const result = await runResearchCycle(workspacePath, topic);
        currentResearch.sentiment = result.sentiment;
        currentResearch.lastResearchTime = new Date().toISOString();
        currentResearch.isResearching = false;
        currentResearch.currentPhase = "idle";
        // Phase 28: Self-Improvement - If sentiment is very high, add to GROWTH.md
        if (result.sentiment > 0.8) {
            await injectMasteryInterest(workspacePath, result.topic);
        }
        return {
            isResearching: false, // Just finished
            currentTopic: result.topic,
            findings: result.findings,
            sentiment: result.sentiment
        };
    }
    return {
        isResearching: currentResearch.isResearching,
        currentTopic: currentResearch.currentTopic,
        findings: null,
        sentiment: currentResearch.sentiment
    };
}
/**
 * Inject mastery interest to GROWTH.md
 */
async function injectMasteryInterest(workspacePath, topic) {
    const growthPath = join(workspacePath, "memory", "reality", "GROWTH.md");
    const entry = `\n\n## ${new Date().toISOString().slice(0, 10)} - New Passion Discovered\n- Found deep interest in **${topic}** - feeling suggests this could become a core skill to develop`;
    try {
        if (existsSync(growthPath)) {
            appendFileSync(growthPath, entry, "utf-8");
        }
        else {
            writeFileSync(growthPath, `# Growth Log\n${entry}`, "utf-8");
        }
        console.log(`[hobby_engine] Added mastery interest to GROWTH.md: ${topic}`);
    }
    catch (error) {
        console.log(`[hobby_engine] Failed to write growth: ${error}`);
    }
}
/**
 * Get current research state (for UI/3D sync)
 */
export function getResearchState() {
    return { ...currentResearch };
}
/**
 * Check if currently researching
 */
export function isCurrentlyResearching() {
    return currentResearch.isResearching;
}
/**
 * Get research summary for context injection
 */
export function getResearchContext() {
    if (!currentResearch.lastResearchTime)
        return null;
    const lastResearch = new Date(currentResearch.lastResearchTime);
    const hoursSince = (Date.now() - lastResearch.getTime()) / (1000 * 60 * 60);
    // Only return if research was recent (within 2 hours)
    if (hoursSince > 2)
        return null;
    if (!currentResearch.currentTopic)
        return null;
    const sentimentText = currentResearch.sentiment > 0.6 ? "fascinating" :
        currentResearch.sentiment < 0.4 ? "not particularly interesting" :
            "moderately engaging";
    return `You recently researched ${currentResearch.currentTopic} and found it ${sentimentText}.`;
}
//# sourceMappingURL=hobby_engine.js.map