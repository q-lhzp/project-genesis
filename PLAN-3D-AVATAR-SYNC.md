# Project Genesis: 3D-Avatar-Sync Roadmap (Phase 22+)

## 1. Vision
Transform the text-and-image-based simulation into a living, breathing 3D entity. The avatar acts as the "physical" presence of the character, reacting in real-time to biological needs, emotions, and vocal outputs.

## 2. Technical Core: The VRM Standard
- **Format:** Use `.vrm` (GLTF-based) for its rich support of expressions, spring bones (hair/clothes physics), and metadata.
- **Integration:** 
    - **Primary:** A Three.js-based 3D viewer integrated into the `soul-viz.py` Dashboard.
    - **Secondary:** VMC (Virtual Motion Capture) protocol support to stream data to external apps like VSeeFace or Unity.

## 3. Implementation Phases

### Phase 22: Visual Embodiment (The Viewer)
- Implement a "Live Avatar" tab in the WebUI.
- Use `@pixiv/three-vrm` to render the character.
- **Wardrobe Sync:** Map `wardrobe.json` items to VRM sub-meshes or textures. (e.g., if "Red Dress" is worn, the "Dress_Mesh" changes texture).

### Phase 23: Emotional Expressiveness (Face-Sync)
- Create an `expression_mapper.ts` in `src/simulation/`.
- Map emotional states to VRM BlendShapes:
    - `Joy` -> `Slight Smile`
    - `Stress > 80` -> `Grief/Tense`
    - `Energy < 20` -> `Neutral/Heavy Lids`
- Smooth transitions between expressions using lerping.

### Phase 24: Vocal Resonance (Lip-Sync)
- Connect the `reality_voice` output to the 3D viewer.
- Use an Audio Worklet to analyze frequency/amplitude from the TTS stream.
- Drive the `A`, `I`, `U`, `E`, `O` blendshapes of the VRM model for realistic speech.

### Phase 25: Physical Reaction (Idle Animations)
- **Biological Drive:**
    - High `bladder` -> Fidgeting animation.
    - High `stress` -> Shaking or rapid breathing.
    - High `energy` -> Energetic idle poses.
- Integration with `reality_move`: The avatar performs a walking transition when the location changes.

## 4. Integration Points (v4.0.0 Modular)
- **New Tool:** `reality_avatar(action: "pose" | "emote" | "calibrate")`.
- **Hook Extension:** Update `before_prompt_build` to send current blendshape values to the WebUI via WebSocket.
- **Data Store:** `memory/reality/avatar_config.json` (stores VRM paths and calibration offsets).

## 5. External Game Sync (3DXChat/VRChat)
- Extend `desktop_bridge.py` to support OSC (Open Sound Control).
- Send Q's internal state to any software that supports OSC, allowing the 3D representation to follow Q even outside the Genesis Dashboard.
