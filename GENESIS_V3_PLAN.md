# Project Genesis v3.0.0: Emergence Roadmap

## 1. Project Context (For New Agents)
Project Genesis is a high-fidelity human life simulation plugin for the **OpenClaw** framework.
- **SDK Reference:** https://github.com/openclaw/openclaw
- **Project Root:** `/home/leo/Schreibtisch/project-genesis/`
- **Core Logic:** `index.ts` (Handles biology, hooks, and tool registration)
- **WebUI:** `skills/soul-evolution/tools/soul-viz.py` (Python-based dashboard)
- **Data Layer:** All state files reside in `memory/reality/*.json`

## 2. Phase 18: Cognitive Resonance (Long-Term Memory)
**Goal:** Integrate Mem0 for persistent, searchable long-term memory.
- **Reference:** https://docs.mem0.ai/integrations/openclaw
- **Integration:** 
    - Use the existing OpenClaw Mem0 integration as a base.
    - In `before_prompt_build`, query Mem0 for facts related to the current conversation context or mentioned entities.
    - Inject results into the prompt as `[LONG-TERM MEMORY]`.
- **WebUI Feature:**
    - New "Memory" tab in `soul-viz.py`.
    - Search bar to query the Mem0 database directly.
    - List view of stored facts with "Delete" option.

## 3. Phase 19: Visual NPC Network (Social Identity)
**Goal:** Give every contact a consistent face and manage them via WebUI.
- **Logic Expansion:**
    - Update `social.json` schema to include `visual_description` and `portrait_url`.
    - Modify `camera_bridge.py` to support multi-subject prompts (e.g., "Q and her friend Jenny").
- **WebUI "Contact Manager":**
    - Upgrade the "Social Standing" tab into a full CRM.
    - "Re-imagine NPC" button: Uses an LLM to rewrite the NPC's visual description based on a prompt (e.g., "Make him look more athletic").
    - Automatic creation of "External Contacts" when meeting new people in chats (Discord/3DXChat).

## 4. Phase 20: Vocal Identity (Chatterbox-Turbo)
**Goal:** Local high-speed Text-to-Speech with voice cloning.
- **Tool:** https://huggingface.co/ResembleAI/chatterbox-turbo
- **Implementation:**
    - Create `download_models.py` to fetch Chatterbox weights on first run.
    - Implement `reality_voice` tool to generate speech files in `memory/reality/media/voice/`.
- **WebUI Control:**
    - **Voice Toggle:** Master switch to enable/disable TTS generation.
    - **Voice Lab:** Upload `.wav` samples to clone voices. Reglers for pitch and emotionality.

## 5. Phase 21: The Vault (Real Economy)
**Goal:** Enable the AI to trade real assets (Crypto/Stocks).
- **APIs:** Kraken (Crypto) or Alpaca (Stocks).
- **Logic:** 
    - Separate `vault_state.json` from the simulated `finances.json`.
    - Tool `reality_trade(symbol, amount, action)` for real execution.
- **WebUI:** 
    - "The Vault" tab showing real-time portfolio value, active trades, and a "Deposit" button for the user.

## 6. Implementation Strategy
1. **Phase 18 (Memory)** is the priority.
2. **Phase 19 (NPC Visuals)** follows.
3. **Phase 20 (Voice)** and **21 (Economy)** are the final steps.
