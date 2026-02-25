// ---------------------------------------------------------------------------
// Social Engine - Autonomous NPC Interactions
// Phase 35: Social Fabric & NPC Autonomy
// ---------------------------------------------------------------------------
import { readJson, writeJson, appendJsonl } from "../utils/persistence.js";
import { join } from "node:path";
import { existsSync } from "node:fs";
const DEFAULT_CONFIG = {
    triggerChance: 0.15,
    cooldownMinutes: 60,
    maxPendingEvents: 3,
    bondHighThreshold: 50,
    bondLowThreshold: -20,
};
/**
 * Default social state
 */
const DEFAULT_STATE = {
    lastEventTime: null,
    pendingCount: 0,
    totalEventsTriggered: 0,
};
/**
 * Load social entities from social.json
 */
async function loadSocialEntities(workspacePath) {
    const socialPath = join(workspacePath, "memory", "reality", "social.json");
    try {
        if (existsSync(socialPath)) {
            const data = await readJson(socialPath);
            return data?.entities || [];
        }
    }
    catch (error) {
        console.log(`[social_engine] Failed to load social: ${error}`);
    }
    return [];
}
/**
 * Load pending social events
 */
async function loadPendingEvents(workspacePath) {
    const eventsPath = join(workspacePath, "memory", "reality", "social_events.json");
    try {
        if (existsSync(eventsPath)) {
            const data = await readJson(eventsPath);
            return data?.pending || [];
        }
    }
    catch (error) {
        console.log(`[social_engine] Failed to load events: ${error}`);
    }
    return [];
}
/**
 * Save pending social events
 */
async function savePendingEvents(workspacePath, events) {
    const eventsPath = join(workspacePath, "memory", "reality", "social_events.json");
    await writeJson(eventsPath, { pending: events });
}
/**
 * Select a random NPC to interact with
 */
function selectRandomNPC(entities) {
    if (entities.length === 0)
        return null;
    // Weight by recency of interaction (prefer those not contacted recently)
    const now = new Date();
    const weighted = entities.map(e => {
        const lastInteraction = e.last_interaction ? new Date(e.last_interaction).getTime() : 0;
        const hoursSince = (now.getTime() - lastInteraction) / (1000 * 60 * 60);
        // Higher weight for less recent interactions
        return { entity: e, weight: Math.min(10, hoursSince + 1) };
    });
    const totalWeight = weighted.reduce((sum, w) => sum + w.weight, 0);
    let random = Math.random() * totalWeight;
    for (const w of weighted) {
        random -= w.weight;
        if (random <= 0)
            return w.entity;
    }
    return weighted[0].entity;
}
/**
 * Generate dynamic message based on bond and relationship
 */
function generateMessage(entity, category, isDe = false) {
    const bond = entity.bond;
    const relType = entity.relationship_type;
    const messages = {
        chat: {
            high: isDe
                ? ["Hey, wie geht's?", "Lange nicht mehr gesprochen!", "Was machst du so?"]
                : ["Hey, how are you?", "Long time no see!", "What have you been up to?"],
            low: isDe
                ? ["Was willst du?", "Rede nicht mit mir.", "Hau ab."]
                : ["What do you want?", "Don't talk to me.", "Go away."],
            neutral: isDe
                ? ["Na?", "Alles klar?", "Hi."]
                : ["Hey?", "All good?", "Hi."],
        },
        support: {
            high: isDe
                ? ["Ich bin fuer dich da!", "Du schaffst das!", "Denk an dich!"]
                : ["I'm here for you!", "You've got this!", "Take care of yourself!"],
            low: [], // No support from enemies
            neutral: isDe
                ? ["Geht's dir gut?", "Kann ich helfen?", "Alles okay?"]
                : ["You doing okay?", "Need any help?", "Everything alright?"],
        },
        request: {
            high: isDe
                ? ["Kannst du mir einen Gefallen tun?", "Brauche mal kurz deine Hilfe!", "Kannst du mich unterstuetzen?"]
                : ["Can you do me a favor?", "Need your help with something!", "Can you support me?"],
            low: isDe
                ? ["Ich brauche das von dir.", "Du schuldest mir was.", "Mach das fuer mich."]
                : ["I need this from you.", "You owe me.", "Do this for me."],
            neutral: isDe
                ? ["Koenntest du das machen?", "Wuerdest du das tun?", "Ich brauche jemanden dafuer."]
                : ["Could you do this?", "Would you do this?", "I need someone for this."],
        },
        conflict: {
            high: [], // Friends don't start conflicts
            low: isDe
                ? ["Wir haben noch eine Rechnung offen.", "Das vergesse ich nicht.", "Das ruecke ich dir nicht raus."]
                : ["We have unfinished business.", "I won't forget this.", "You're not getting away with this."],
            neutral: isDe
                ? ["Das ist nicht fair.", "Ich habe ein Problem damit.", "Das stimmt so nicht."]
                : ["That's not fair.", "I have a problem with this.", "That's not right."],
        },
        invitation: {
            high: isDe
                ? ["Lass uns was unternehmen!", "Wollen wir zusammen was machen?", "Wie waer's mit heute Abend?"]
                : ["Let's hang out!", "Want to do something together?", "How about tonight?"],
            low: isDe
                ? ["Du koenntest kommen... aber ich weiss nicht.", "Vielleicht solltest du kommen."]
                : ["You could come... but I don't know.", "Maybe you should come."],
            neutral: isDe
                ? ["Es gibt eine Party/Event.", "Treffen wir uns?", "Willst du mitkommen?"]
                : ["There's a party/event.", "Should we meet up?", "Want to come along?"],
        },
        gossip: {
            high: isDe
                ? ["Rate mal was ich gehoert habe!", "Du wirst es nicht glauben...", "Das musst du hoeren!"]
                : ["Guess what I heard!", "You won't believe this...", "You have to hear this!"],
            low: isDe
                ? ["Ich weiss etwas ueber dich...", "Leute reden ueber dich."]
                : ["I know something about you...", "People are talking about you."],
            neutral: isDe
                ? ["Interessante Neuigkeiten...", "Hast du das gehoert?", "Weisst du schon bescheid?"]
                : ["Interesting news...", "Have you heard?", "Do you know about this?"],
        },
    };
    let pool;
    if (bond > 50)
        pool = messages[category].high;
    else if (bond < -20)
        pool = messages[category].low;
    else
        pool = messages[category].neutral;
    // Fallback to neutral if specific pool is empty
    if (pool.length === 0) {
        pool = messages[category].neutral.length > 0 ? messages[category].neutral : messages.chat.neutral;
    }
    return pool[Math.floor(Math.random() * pool.length)];
}
/**
 * Determine event category based on relationship
 */
function determineCategory(entity) {
    const bond = entity.bond;
    const relType = entity.relationship_type;
    // High bond friends: support, invitations, chat
    if (bond > 50) {
        const categories = ["chat", "support", "invitation", "gossip"];
        return categories[Math.floor(Math.random() * categories.length)];
    }
    // Low bond enemies: conflict
    if (bond < -20) {
        return Math.random() < 0.7 ? "conflict" : "request";
    }
    // Neutral/acquaintances: chat, request, gossip
    const categories = ["chat", "request", "gossip"];
    return categories[Math.floor(Math.random() * categories.length)];
}
/**
 * Calculate emotional impact of the event
 */
function calculateEmotionalImpact(category, bond) {
    const impacts = {
        chat: { stress: 0, joy: 5 },
        support: { stress: -10, joy: 15 },
        request: { stress: 5, joy: 0 },
        conflict: { stress: 20, joy: -15 },
        invitation: { stress: -5, joy: 10 },
        gossip: { stress: 5, joy: 5 },
    };
    const impact = impacts[category];
    // Bond modifier: high bond amplifies positive, low bond amplifies negative
    const bondMultiplier = bond > 50 ? 1.2 : (bond < -20 ? 1.3 : 1.0);
    return {
        stressChange: Math.round(impact.stress * bondMultiplier),
        joyChange: Math.round(impact.joy * bondMultiplier),
    };
}
/**
 * Update entity's bond based on event
 */
function updateEntityBond(entity, category) {
    const bondChange = {
        chat: 2,
        support: 10,
        request: -2,
        conflict: -15,
        invitation: 5,
        gossip: 1,
    };
    return {
        ...entity,
        bond: Math.max(-100, Math.min(100, (entity.bond || 0) + bondChange[category])),
        last_interaction: new Date().toISOString(),
        interaction_count: (entity.interaction_count || 0) + 1,
    };
}
/**
 * Log social activity
 */
async function logSocialActivity(workspacePath, action, details) {
    const logPath = join(workspacePath, "memory", "genesis_log.jsonl");
    await appendJsonl(logPath, {
        timestamp: new Date().toISOString(),
        type: "social_engine",
        action,
        details
    });
}
/**
 * Main process function - call from tick handler
 */
export async function processSocialDynamics(workspacePath, physique, config = DEFAULT_CONFIG, isDe = false) {
    const now = new Date();
    // Load pending events
    const pendingEvents = await loadPendingEvents(workspacePath);
    const pendingCount = pendingEvents.filter(e => !e.processed).length;
    // Check if we have too many pending events
    if (pendingCount >= config.maxPendingEvents) {
        return { hasNewEvent: false, event: null, emotionalImpact: null };
    }
    // Check cooldown
    const statePath = join(workspacePath, "memory", "reality", "social_engine_state.json");
    let state = { ...DEFAULT_STATE };
    try {
        if (existsSync(statePath)) {
            state = await readJson(statePath) || state;
        }
    }
    catch {
        // Use default
    }
    if (state.lastEventTime) {
        const lastTime = new Date(state.lastEventTime);
        const diffMinutes = (now.getTime() - lastTime.getTime()) / (1000 * 60);
        if (diffMinutes < config.cooldownMinutes) {
            return { hasNewEvent: false, event: null, emotionalImpact: null };
        }
    }
    // Check probability trigger
    if (Math.random() > config.triggerChance) {
        return { hasNewEvent: false, event: null, emotionalImpact: null };
    }
    // Load social entities
    const entities = await loadSocialEntities(workspacePath);
    if (entities.length === 0) {
        return { hasNewEvent: false, event: null, emotionalImpact: null };
    }
    // Select NPC
    const entity = selectRandomNPC(entities);
    if (!entity) {
        return { hasNewEvent: false, event: null, emotionalImpact: null };
    }
    // Determine category and generate message
    const category = determineCategory(entity);
    const message = generateMessage(entity, category, isDe);
    // Calculate emotional impact
    const emotionalImpact = calculateEmotionalImpact(category, entity.bond);
    // Create event
    const event = {
        timestamp: now.toISOString(),
        sender_name: entity.name,
        sender_id: entity.id,
        message,
        category,
        processed: false,
    };
    // Save event
    pendingEvents.push(event);
    await savePendingEvents(workspacePath, pendingEvents);
    // Update state
    state.lastEventTime = now.toISOString();
    state.pendingCount = pendingEvents.length;
    state.totalEventsTriggered++;
    await writeJson(statePath, state);
    // Update entity bond
    const updatedEntity = updateEntityBond(entity, category);
    await updateEntityInSocial(workspacePath, updatedEntity);
    // Log
    await logSocialActivity(workspacePath, "event_triggered", `${entity.name} sent ${category}: "${message}"`);
    console.log(`[social_engine] New event from ${entity.name}: ${category}`);
    return {
        hasNewEvent: true,
        event,
        emotionalImpact,
    };
}
/**
 * Update entity in social.json
 */
async function updateEntityInSocial(workspacePath, updatedEntity) {
    const socialPath = join(workspacePath, "memory", "reality", "social.json");
    try {
        const data = await readJson(socialPath);
        if (data?.entities) {
            const idx = data.entities.findIndex(e => e.id === updatedEntity.id);
            if (idx >= 0) {
                data.entities[idx] = updatedEntity;
                await writeJson(socialPath, data);
            }
        }
    }
    catch (error) {
        console.log(`[social_engine] Failed to update entity: ${error}`);
    }
}
/**
 * Get pending events for UI
 */
export async function getPendingEvents(workspacePath) {
    return loadPendingEvents(workspacePath);
}
/**
 * Mark event as processed
 */
export async function markEventProcessed(workspacePath, eventId) {
    const events = await loadPendingEvents(workspacePath);
    const idx = events.findIndex(e => e.sender_id === eventId && !e.processed);
    if (idx >= 0) {
        events[idx].processed = true;
        await savePendingEvents(workspacePath, events);
    }
}
/**
 * Get current social engine state
 */
export async function getSocialEngineState(workspacePath) {
    const statePath = join(workspacePath, "memory", "reality", "social_engine_state.json");
    try {
        if (existsSync(statePath)) {
            return await readJson(statePath) || DEFAULT_STATE;
        }
    }
    catch {
        // Use default
    }
    return DEFAULT_STATE;
}
//# sourceMappingURL=social_engine.js.map